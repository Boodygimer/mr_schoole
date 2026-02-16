# 🚀 نظام الشات — Quick Start

## التثبيت السريع

### 1️⃣ المتطلبات
```bash
Python 3.10+
Node.js 14+
npm
```

### 2️⃣ تثبيت الحزم
```bash
# Python
pip install -r requirements.txt

# Node.js
npm install
```

### 3️⃣ تشغيل الخوادم

**خيار أول: تشغيل منفصل**

```bash
# Terminal 1: Flask
python app.py

# Terminal 2: Chat Server
npm start
```

**خيار ثاني: باستخدام السكريبت المدمج**
```bash
chmod +x start.sh
./start.sh
```

### 4️⃣ الوصول
```
تسجيل الدخول: http://localhost:5000/login
البريد: legacy@example.com
كلمة المرور: testpass123
```

---

## ✨ المميزات

✅ رسائل فورية عبر Socket.IO  
✅ حفظ في قاعدة البيانات  
✅ سجل الرسائل السابقة  
✅ مؤشر الكتابة  
✅ تتبع المستخدمين المتصلين  
✅ حماية من XSS  

---

## 📡 البنية

```
متصفح (Socket.IO Client)
    ↓ WebSocket
Chat Server (Node.js:3001)
    ↓ REST API
Flask API (Python:5000)
    ↓
SQLite Database
```

---

## 🐛 استكشاف الأخطاء

### الخطأ: `Cannot GET /`
```bash
# تحقق من أن Flask يعمل
ps aux | grep python
# أو أعد تشغيل Flask
```

### الخطأ: `Connection refused` للشات
```bash
# تحقق من أن Node.js يعمل
npm start

# في Terminal منفصل
```

### الخطأ: رسائل لا تُحفظ
```bash
# يجب تسجيل دخول أولاً
# ثم التحقق من logs Flask
```

---

## 📚 التوثيق الكامل
اقرأ [CHAT_GUIDE.md](./CHAT_GUIDE.md) للتفاصيل الكاملة

---

**آخر تحديث:** 11 فبراير 2026
