# Script to create a legacy (plaintext password) user for testing the login upgrade.
import os
import importlib.util

APP_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app.py'))

spec = importlib.util.spec_from_file_location('app_module', APP_PATH)
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)

app = app_module.app
db = app_module.db
User = app_module.User

with app.app_context():
    email = 'legacy@example.com'
    existing = User.query.filter_by(email=email).first()
    if existing:
        print('User already exists:', existing.email)
    else:
        # Intentionally store plaintext password to simulate legacy DB
        u = User(name='Legacy User', email=email, password='testpass123', role='Student')
        db.session.add(u)
        db.session.commit()
        print('Created legacy user with email:', email, 'password: testpass123')
