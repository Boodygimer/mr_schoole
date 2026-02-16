# نظام الشات — Chat System Documentation

## نظرة عامة
نظام شات حقيقي الوقت متقدم يدعم:
- ✅ رسائل لحظية عبر Socket.IO
- ✅ حفظ دائم في قاعدة البيانات
- ✅ سجل الرسائل السابقة
- ✅ تتبع المستخدمين المتصلين
- ✅ مؤشر الكتابة (Typing indicator)
- ✅ تعقيم الرسائل (XSS prevention)

---

## البنية المعمارية

```
┌─────────────────────────────────────────┐
│         🌐 المتصفح (Flask)              │
│  discord_layout.html (Socket.IO Client) │
└──────────────┬──────────────────────────┘
               │ WebSocket
               ▼
┌─────────────────────────────────────────┐
│    🚀 Chat Server (Node.js Port 3001)   │
│         - Socket.IO Handler             │
│         - Message Broadcasting          │
│         - User Tracking                 │
└──────────────┬──────────────────────────┘
               │ REST API calls
               ▼
┌─────────────────────────────────────────┐
│     🐍 Flask App (Port 5000)            │
│  - Stores messages (ChatMessage model)  │
│  - Authenticates users                  │
│  - Provides REST endpoints               │
│  - Database persistence                 │
└─────────────────────────────────────────┘
```

---

## مكونات النظام

### 1️⃣ Flask Backend (`app.py`)

#### نموذج ChatMessage
```python
class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    room = db.Column(db.String(100))      # الغرفة/المادة
    message = db.Column(db.Text)          # محتوى الرسالة
    timestamp = db.Column(db.DateTime)    # وقت الإرسال
```

#### REST Endpoints

##### جلب سجل الرسائل
```
GET /api/chat/messages/<room>
Response: 
{
  "messages": [
    {
      "id": 1,
      "author": "أحمد",
      "message": "مرحبا",
      "time": "14:30:45",
      "room": "الرياضيات"
    }
  ]
}
```

##### حفظ رسالة جديدة
```
POST /api/chat/save
Content-Type: application/json
{
  "room": "الرياضيات",
  "message": "مرحبا",
  "userId": 1
}
```

### 2️⃣ Node.js Chat Server (`chat_server.js`)

#### Socket Events

**Client → Server:**
```javascript
socket.emit('join_room', { room, userName })
socket.emit('send_message', { room, author, message, userId })
socket.emit('typing', { room, author })
socket.emit('stop_typing', { room, author })
```

**Server → Clients:**
```javascript
socket.on('receive_message', (data) => {})
socket.on('user_joined', (data) => {})
socket.on('user_left', (data) => {})
socket.on('room_stats', (data) => { userCount, users })
socket.on('user_typing', (data) => {})
```

### 3️⃣ Frontend (`discord_layout.html`)

**المميزات:**
- متصفح رسائل تفاعلي
- عرض المستخدمين المتصلين
- مؤشر الكتابة
- تحميل السجل التلقائي

---

## التثبيت والتشغيل

### المتطلبات
```bash
# Python (Flask)
pip install -r requirements.txt

# Node.js (Chat Server)
node -v  # v14+ required
npm -v   # npm package manager
```

### خطوات التثبيت

#### 1. تثبيت حزم Python
```bash
cd my_school_project
pip install -r requirements.txt
```

#### 2. تثبيت حزم Node.js
```bash
cd my_school_project
npm install
```

يثبت:
- `socket.io` — WebSocket library
- `express` — Web framework
- `cors` — Cross-Origin Resource Sharing
- `axios` — HTTP client

#### 3. تشغيل الخادم

**Terminal 1: Flask App**
```bash
cd my_school_project
python app.py
# أو
/path/to/venv/bin/python app.py
```

**Terminal 2: Chat Server**
```bash
cd my_school_project
npm start
# أو للتطوير مع hot-reload
npm run dev  # يتطلب nodemon
```

### النتيجة المتوقعة

```
Flask:
 * Running on http://127.0.0.1:5000

Chat Server:
🚀 CHAT SERVER RUNNING ON PORT 3001
📍 Flask API: http://localhost:5000
```

---

## كيفية الاستخدام

### 1. تسجيل الدخول
- اذهب إلى `http://localhost:5000/login`
- استخدم البيانات الاختبارية أو سجّل حساباً جديداً

### 2. الانتقال إلى الشات
- انقر على "الشات (Discord)" من لوحة التحكم
- الخادم سيحمل سجل الرسائل تلقائياً

### 3. إرسال رسالة
- اكتب الرسالة
- اضغط Enter أو انقر على زر الإرسال
- الرسالة تُحفظ وتُبث للجميع

---

## الأمان (Security)

### 1. تعقيم الرسائل (XSS Prevention)
```javascript
function sanitizeMessage(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}
```

### 2. التحقق من المستخدم
- جميع الرسائل مرتبطة بـ `user_id`
- يمكن التحقق من الملكية

### 3. حدود الرسائل
- حد أقصى 500 حرف لكل رسالة
- توقف المحادثات غير النشطة

---

## استكشاف الأخطاء

### المشكلة: لا يتصل بخادم الشات

**الحل:**
```bash
# تحقق من أن خادم Node.js يعمل
curl http://localhost:3001/health

# تحقق من الأخطاء في Console
# اضغط F12 في المتصفح
```

### المشكلة: الرسائل لا تُحفظ

**الحل:**
```bash
# تحقق من اتصال قاعدة البيانات
# تحقق من logs Flask للأخطاء

# تحقق من أن الـ session صحيحة
# قد تحتاج لإعادة تسجيل الدخول
```

### المشكلة: CORS errors

**الحل:**
```javascript
// تحقق من أن CORS مفعّل في chat_server.js
const io = new Server(server, {
  cors: { origin: '*' }  // ✅ يجب أن يكون موجوداً
});
```

---

## أمثلة الاستخدام

### مثال 1: إرسال رسالة برمجياً
```javascript
socket.emit('send_message', {
  room: 'الرياضيات',
  author: 'أحمد',
  message: 'ما الإجابة على المسألة 5؟',
  userId: 123
});
```

### مثال 2: الاستماع للرسائل الجديدة
```javascript
socket.on('receive_message', (data) => {
  console.log(`${data.author}: ${data.message}`);
});
```

### مثال 3: جلب السجل من الـ API
```python
import requests

response = requests.get(
  'http://localhost:5000/api/chat/messages/الرياضيات'
)
messages = response.json()['messages']
```

---

## الأداء والحدود

| الخاصية | الحد |
|------|-----|
| حجم الرسالة | 500 حرف أقصى |
| حجم المخزن المؤقت | 1 MB |
| عمق السجل | 50 رسالة |
| المستخدمين المتزامنين | بلا حد (يعتمد على الخادم) |

---

## المستقبل

### التحسينات المخطط لها:
- [ ] تشفير الرسائل (E2E Encryption)
- [ ] ملفات الوسائط (صور، فيديو)
- [ ] Reactions على الرسائل
- [ ] البحث في السجل
- [ ] الرسائل الخاصة (Direct Messages)
- [ ] Threads
- [ ] البوتات (Bots)

---

**آخر تحديث:** 11 فبراير 2026  
**الحالة:** ✅ جاهز للإنتاج
