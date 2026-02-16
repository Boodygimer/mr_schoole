import os
"""
my_school_project — Research Search (مدرسة) Flask application

This file contains a lightweight school/research collaboration app used as
the basis for a small research-oriented platform. Key concerns addressed in
this refactor:
- Use environment variables for secrets and mail credentials.
- Hash passwords using Werkzeug before persisting to the database.
- Keep templates styled for a professional research UI.

Security note: For production, set `SECRET_KEY`, `MAIL_USERNAME`,
`MAIL_PASSWORD`, and `DATABASE_URL` using environment variables and deploy
behind a WSGI server.
"""
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask import SocketIO, emit, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from datetime import datetime
import random
import string
import re
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

# --- App configuration ---
app = Flask(__name__)
# Use environment variables for secrets in production. The fallbacks below are
# just for local development convenience; set real secrets via env vars.
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'boody-gimer-secret-key-2025')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///school.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Email Configuration ---
# Read mail credentials from environment for security
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True') in ['True', 'true', '1']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'your_email@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'your_password')

mail = Mail(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize Socket.IO
socketio = SocketIO(app, cors_allowed_origins="*")

# --- الداتا بيز ---
class User(UserMixin, db.Model):
    """User model for authentication and simple profile data.

    Passwords are stored hashed using Werkzeug's `generate_password_hash`.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    # Increase length to accommodate hashed passwords
    password = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    parent_phone_number = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(50), default="Student")

    def __init__(self, name, email, password, role="Student", phone_number=None, parent_phone_number=None):
        self.name = name
        self.email = email
        self.password = password
        self.role = role
        self.phone_number = phone_number
        self.parent_phone_number = parent_phone_number

class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(10))
    channels = db.relationship('Channel', backref='server', cascade="all, delete-orphan")

class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    server_id = db.Column(db.Integer, db.ForeignKey('server.id'), nullable=False)

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    link = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100), default="General") # e.g., Math, Science, General

class ChatMessage(db.Model):
    """Chat message stored in database for persistence and history."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room = db.Column(db.String(100), nullable=False)  # server name (e.g., "مادة الرياضيات")
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    user = db.relationship('User', backref='messages')
    
    def to_dict(self):
        """Convert to dict for JSON serialization."""
        return {
            'id': self.id,
            'author': self.user.name if self.user else 'Unknown',
            'message': self.message,
            'time': self.timestamp.strftime('%H:%M:%S'),
            'room': self.room
        }

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- الصفحات ---
@app.route('/')
@login_required
def home():
    first_server = Server.query.first()
    if first_server:
        return redirect(url_for('server_view', server_id=first_server.id))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        # Prefer hashed verification. If the stored password is plaintext
        # (legacy), allow login and immediately upgrade it to a hashed value.
        if user:
            # Correct hashed password
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('home'))

            # Legacy plaintext password support: detect exact match and upgrade
            if user.password == password:
                try:
                    user.password = generate_password_hash(password)
                    db.session.commit()
                except Exception:
                    # If upgrading fails, continue with login anyway
                    pass
                login_user(user)
                return redirect(url_for('home'))

        # If we reach here, authentication failed
        flash('بيانات خطأ، حاول تاني', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone_number = request.form.get('phone_number')
        parent_phone_number = request.form.get('parent_phone_number')

        # Regex Validation for Egyptian Phone Numbers
        phone_pattern = re.compile(r'^201\d{9}$')
        if not phone_pattern.match(phone_number) or not phone_pattern.match(parent_phone_number):
            flash('أرقام الهاتف لازم تكون مصرية (تبدأ بـ 201 وتتكون من 12 رقم)', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('الإيميل ده متسجل قبل كده', 'warning')
            return redirect(url_for('register'))

        # Check if it's the first user (Owner)
        role = "Owner" if not User.query.first() else "Student"

        # Generate OTP and store temporary registration data in session.
        # Store the password hashed so we never keep plaintext passwords in session.
        otp = ''.join(random.choices(string.digits, k=6))

        hashed_password = generate_password_hash(password)

        # Store minimal necessary data in session until verification completes
        session['register_data'] = {
            'name': name,
            'email': email,
            'password_hash': hashed_password,
            'phone_number': phone_number,
            'parent_phone_number': parent_phone_number,
            'role': role,
            'otp': otp
        }

        # Send OTP Email
        try:
            msg = Message('رمز التحقق الخاص بك', sender='noreply@school.com', recipients=[email])
            msg.body = f'رمز التحقق الخاص بك هو: {otp}'
            mail.send(msg)
            flash('تم إرسال رمز التحقق للإيميل', 'info')
        except Exception as e:
            print(f"Error sending email: {e}")
            flash(f'فشل إرسال الإيميل. الرمز (للاختبار) هو: {otp}', 'warning') # For testing/dev

        return redirect(url_for('verify_otp'))
    return render_template('register.html')

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if 'register_data' not in session:
        return redirect(url_for('register'))

    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        stored_data = session.get('register_data')

        if entered_otp == stored_data['otp']:
            # Create user using the hashed password stored earlier
            new_user = User(
                name=stored_data['name'],
                email=stored_data['email'],
                password=stored_data['password_hash'],
                phone_number=stored_data.get('phone_number'),
                parent_phone_number=stored_data.get('parent_phone_number'),
                role=stored_data.get('role', 'Student')
            )
            db.session.add(new_user)
            db.session.commit()
            
            # Login and Clear Session
            login_user(new_user)
            session.pop('register_data', None)
            flash('تم إنشاء الحساب بنجاح', 'success')
            return redirect(url_for('home'))
        else:
            flash('الرمز غلط، حاول تاني', 'danger')
            
    return render_template('verify_otp.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/server/<int:server_id>')
@login_required
def server_view(server_id):
    servers = Server.query.all()
    current_server = Server.query.get_or_404(server_id)
    return render_template('discord_layout.html', servers=servers, current_server=current_server, user=current_user, room_name=current_server.name)

@app.route('/watch')
@login_required
def watch_video():
    video_data = {"title": "شرح الفيزياء الحديثة", "url": "https://www.w3schools.com/html/mov_bbb.mp4"}
    return render_template('watch.html', video=video_data, user=current_user)

@app.route('/dashboard')
@login_required
def dashboard():
    # Dashboard is now accessible to everyone, but content differs by role
    users = User.query.all()
    servers = Server.query.all()
    announcements = Announcement.query.order_by(Announcement.date_posted.desc()).all()
    resources = Resource.query.all()
    return render_template('dashboard.html', users=users, servers=servers, announcements=announcements, resources=resources, user=current_user)

@app.route('/add_server', methods=['POST'])
@login_required
def add_server():
    if current_user.role == 'Owner':
        name = request.form.get('server_name')
        icon = request.form.get('server_icon')
        new_server = Server(name=name, icon=icon)
        db.session.add(new_server)
        db.session.add(Channel(name="General", server=new_server))
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/delete_server/<int:id>')
@login_required
def delete_server(id):
    if current_user.role == 'Owner':
        server = Server.query.get_or_404(id)
        db.session.delete(server)
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/update_role', methods=['POST'])
@login_required
def update_role():
    if current_user.role == 'Owner':
        user_id = request.form.get('user_id')
        user = User.query.get(user_id)
        if user:
            user.role = request.form.get('new_role')
            db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/add_announcement', methods=['POST'])
@login_required
def add_announcement():
    if current_user.role in ['Owner', 'Teacher']:
        title = request.form.get('title')
        content = request.form.get('content')
        new_announcement = Announcement(title=title, content=content)
        db.session.add(new_announcement)
        db.session.commit()
        flash('تم إضافة الإعلان بنجاح', 'success')
    return redirect(url_for('dashboard'))

@app.route('/add_resource', methods=['POST'])
@login_required
def add_resource():
    if current_user.role in ['Owner', 'Teacher']:
        title = request.form.get('title')
        link = request.form.get('link')
        description = request.form.get('description')
        category = request.form.get('category')
        new_resource = Resource(title=title, link=link, description=description, category=category)
        db.session.add(new_resource)
        db.session.commit()
        flash('تم إضافة المصدر بنجاح', 'success')
    return redirect(url_for('dashboard'))

@app.route('/delete_announcement/<int:id>')
@login_required
def delete_announcement(id):
    if current_user.role in ['Owner', 'Teacher']:
        announcement = Announcement.query.get_or_404(id)
        db.session.delete(announcement)
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/delete_resource/<int:id>')
@login_required
def delete_resource(id):
    if current_user.role in ['Owner', 'Teacher']:
        resource = Resource.query.get_or_404(id)
        db.session.delete(resource)
        db.session.commit()
    return redirect(url_for('dashboard'))

# --- Chat Routes ---
@app.route('/api/chat/messages/<room>', methods=['GET'])
@login_required
def get_chat_messages(room):
    """Fetch chat history for a room (last 50 messages)."""
    messages = ChatMessage.query.filter_by(room=room).order_by(
        ChatMessage.timestamp.desc()
    ).limit(50).all()
    # Reverse to show oldest first
    messages.reverse()
    return {'messages': [msg.to_dict() for msg in messages]}

@app.route('/api/chat/save', methods=['POST'])
@login_required
def save_chat_message():
    """Save a chat message to the database."""
    data = request.get_json()
    if not data or 'message' not in data or 'room' not in data:
        return {'error': 'Missing required fields'}, 400
    
    msg = ChatMessage(
        user_id=current_user.id,
        room=data['room'],
        message=data['message']
    )
    db.session.add(msg)
    db.session.commit()
    return {'success': True, 'message': msg.to_dict()}

# --- Real-time Chat Functionality ---
@socketio.on('join_room')
def handle_join_room_event(data):
    room = data['room']
    join_room(room)
    emit('room_message', {'message': f"{data['username']} has joined the room."}, room=room)

@socketio.on('leave_room')
def handle_leave_room_event(data):
    room = data['room']
    leave_room(room)
    emit('room_message', {'message': f"{data['username']} has left the room."}, room=room)

@socketio.on('send_message')
def handle_send_message_event(data):
    room = data['room']
    emit('room_message', {'username': data['username'], 'message': data['message']}, room=room)