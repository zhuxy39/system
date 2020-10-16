from django.contrib.auth.models import User

from application.models import EmailVerifyRecord, student, teacher
from random import Random
from django.core.mail import send_mail
from django.conf import settings

# 生成随机数
def random_str(randomlength=8):
    rand_str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        rand_str += chars[random.randint(0, length)]
    return rand_str

#注册或找回密码
def send_register_email(email, send_type="register"):
    email_record = EmailVerifyRecord()
    code = random_str(16)
    email_record.code = code
    email_record.email = email
    email_record.send_type = send_type
    email_record.save() # 生成一个随机码存入
    email_title = ""
    email_body = ""

    if send_type == "register":
        email_title = "课室管理系统账号激活"
        email_body = "请点击以下链接激活您的账号：http://127.0.0.1:8000/active/{0}".format(code)
        # send_mail(email_title, email_body, settings.EMAIL_FROM, [email, ])
    all_records = EmailVerifyRecord.objects.filter(code =code)
    if all_records:
        for record in all_records:
            email = record.email
            user = User.objects.get(email=email)
            try:
                s = student.objects.get(user=user)
                s.status = True
                s.save()
            except:
                t = teacher.objects.get(user=user)
                t.status = True
                t.save()
            user.is_active = True
            user.save()
        all_records.delete()


def send_reset_password_email(email, send_type="reset_password"):
    email_record = EmailVerifyRecord()
    code = random_str(16)
    email_record.code = code
    email_record.email = email
    email_record.send_type = send_type
    email_record.save() # 生成一个随机码存入
    email_title = ""
    email_body = ""

    if send_type == "reset_password":
        email_title = "课室管理系统密码重置"
        email_body = "请点击以下链接重置您的密码：http://127.0.0.1:8000/confirm_reset/{0}".format(code)
        send_mail(email_title, email_body, settings.EMAIL_FROM, [email,])

