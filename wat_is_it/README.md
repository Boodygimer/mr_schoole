# Research Search Platform 🔍

A professional, color-science-driven research collaboration platform built with Flask.

## 🎨 نظام الألوان المتقدم

تم تطبيق نظام لوني احترافي متوافق مع علم الألوان:
- **الأساس**: أزرق أكاديمي عميق (#0B3D91) يعكس الثقة والاحترافية
- **التنسيق**: تدرجات وظلال لطيفة توفر عمقاً بصرياً
- **إمكانية الوصول**: تباين 4.5:1+ على جميع النصوص
- **الاحترافية**: تصميم بسيط وواضح خالي من الفوضى البصرية

**شاهد التفاصيل الكاملة**: [COLOR_SYSTEM.md](./COLOR_SYSTEM.md)

## ✨ المميزات

### 🔐 الأمان
- ✅ كلمات مرور مشفرة (PBKDF2/Scrypt)
- ✅ دعم انتقالي لكلمات المرور القديمة (الترقية التلقائية)
- ✅ توثيق OTP عند التسجيل
- ✅ متغيرات بيئية للأسرار الحساسة

### 👥 إدارة المستخدمين
- تحكم قائم على الأدوار (Owner, Teacher, Student)
- إدارة علنية للمستخدمين
- أرقام هاتف مصرية محققة

### 🎓 المحتوى
- **الإعلانات**: نشر تعديلات مهمة بسهولة
- **الموارد التعليمية**: روابط منظمة مع التصنيفات
- **الحوار المباشر**: نظام دردشة Socket.IO
- **الفيديوهات**: مشغل محمي برقم مائي

## 🚀 البدء السريع

### المتطلبات
```bash
Python 3.10+
Flask, SQLAlchemy, Flask-Login, Flask-Mail
```

### التثبيت
```bash
pip install -r requirements.txt
```

### التشغيل
```bash
# تطوير
FLASK_ENV=development python app.py

# الإنتاج (استخدم خادم WSGI مثل gunicorn)
gunicorn app:app
```

### المتغيرات البيئية الموصى بها
```bash
# الأمان
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///school.db

# البريد الإلكتروني
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-app-password
```

## 📁 هيكل المشروع

```
my_school_project/
├── app.py                    # التطبيق الرئيسي
├── requirements.txt          # المتطلبات
├── COLOR_SYSTEM.md          # توثيق الألوان
├── templates/               # قوالب HTML
│   ├── login.html
│   ├── register.html
│   ├── verify_otp.html
│   ├── dashboard.html
│   ├── discord_layout.html
│   └── watch.html
├── instance/                # قاعدة البيانات
└── scripts/
    └── create_legacy_user.py  # أداة الاختبار
```

## 🔄 تدفق المستخدم

1. **التسجيل**: بيانات → OTP → تشفير آمن
2. **تسجيل الدخول**: البريد + كلمة المرور (مع دعم الترقية التلقائية)
3. **اللوحة الرئيسية**: عرض الإحصائيات والموارد
4. **الإدارة** (الملاك فقط): المستخدمين والمواد والإعلانات

## 🎯 المهام المنجزة

✅ **تدقيق الكود**: فحص شامل لجميع الملفات
✅ **الأمان**: كلمات مرور مشفرة + دعم انتقالي
✅ **التوثيق**: تعليقات واضحة في جميع الأقسام
✅ **نظام الألوان**: متوافق مع علم الألوان الحديث
✅ **التصميم**: واجهة نظيفة واحترافية
✅ **الاختبار**: التحقق من جميع الصفحات والميزات

## 📝 ملاحظات التطوير

- **الترقية**: استخدم Gunicorn أو uWSGI للإنتاج
- **قاعدة البيانات**: يمكنك التبديل إلى PostgreSQL بسهولة
- **Socket.IO**: تأكد من تشغيل `chat_server.js` للحوار المباشر
- **البريد**: اختبر مع حساب Gmail أو خدمة بريد مخصصة

## 🛠️ المراجع التقنية

- Flask: https://flask.palletsprojects.com/
- SQLAlchemy: https://www.sqlalchemy.org/
- Bootstrap 5: https://getbootstrap.com/
- Color Science: https://www.interaction-design.org/literature/topics/color-theory

---

**آخر تحديث**: 11 فبراير 2026  
**الحالة**: جاهز للتطوير والاختبار
