#_*_ coding:utf-8 _*_

from mysite import models
from usermanage import models
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.decorators.csrf import  csrf_exempt
from django.core import serializers
#from singledispatch import singledispatch
import subprocess
import json
import datetime, time
from decimal import Decimal
from cart.cart import Cart
from cart.models import Item
import cart
from django.core.mail import send_mail, EmailMessage

@csrf_exempt
def sregister(request):
    postbody = request.body
    json_result = json.loads(postbody)
    name = json_result['name']
    email = json_result['email']
    password = json_result['password']
    try:
        user_name = models.UserManage.objects.get(name=name)
    except:
        user_name = None
    if user_name is not None:
        return JsonResponse({'status':10034,'message':'the username is already exists.'})
    try:
        user_email = models.UserManage.objects.get(email=email)
    except:
        user_email = None
    if user_email is not None:
        return JsonResponse({'status':10035,'message':'the email is already exists.'})
    if user_name is None and user_email is None:
        user = models.UserManage(date_joined=datetime.datetime.now(), last_login=datetime.datetime.now())
        user.name = name
        user.email = email
        user.password = password
        user.save()
        #active = models.UserActive()
        #active.name = name
        #active.email = email
    email_title = "电商网用户激活"
    email_messages =  "欢迎注册使用风炎电子商务平台，请点击以下网址完成用户激活"
    email_body = email_messages+"\n\n"+"http://47.89.181.139/active/?id=" + str(user.id)
    #send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
    emailboss = EmailMessage( email_title,
                                          email_body,
                                          '1625504587@qq.com',
                                          [user.email])
    emailboss.send()
    return HttpResponse(json.dumps(user.id), content_type="application/json")

@csrf_exempt
def sactive(request):
    #postbody = request.body
    #json_result = json.loads(postbody)
    #userid = json_result['id']
    userid = request.GET['id']
    uuser = models.UserManage.objects.get(id=userid)
    uuser.is_active = 1
    try:
        uuser.save()
    except:
        return JsonResponse({'status':10044,'message':'ERROR'})
    return JsonResponse({'status':10045,'message':'the user is actived succeed'})

@csrf_exempt
def slogin(request):
    postbody = request.body
    json_result = json.loads(postbody)
    name = json_result['name']
    password = json_result['password']
    try:
        user = models.UserManage.objects.get(name=name)
    except:
        user = None
    if user is not None:
        upassword = user.password
        if user.is_active == 1:
            if upassword == password:
                #user.last_login = time.asctime( time.localtime(time.time()) )
                user.last_login = datetime.datetime.now()
                user.save()
                request.session['uuserid'] = user.id
                return JsonResponse({'userid':request.session['uuserid'],'status':10055,'message':'Login successful!!!'})
            else:
                return JsonResponse({'status':10056,'message':'The password is wrong'})
        else:
            email_title = "电商网用户激活"
            email_messages =  "欢迎注册使用风炎电子商务平台，请点击以下网址完成用户激活"
            email_body = email_messages+"\n\n"+"http://47.89.181.139/active/?id=" + str(user.id)
            emailboss = EmailMessage( email_title,
                                      email_body,
                                      '1625504587@qq.com',
                                      [user.email])
            emailboss.send()
            return JsonResponse({'status':10057,'message':'The user is not active, please check your email'})
    else:
        return JsonResponse({'status':10055,'message':'the user is not exists'})

@csrf_exempt
def sreset_password(request):
    postbody = request.body
    json_result = json.loads(postbody)
    new_password = json_result['password']
    u_userid = request.session['uuserid']
    userid = str(u_userid).strip('L')
    if new_password is None:
        JsonResponse({'status':10061,'message':'The new password can not be none.'})
    else:
        uuser = models.UserManage.objects.get(id=int(userid))
        old_password = uuser.password
        if old_password == new_password:
            return JsonResponse({'status':10061,'message':'The new password can not be same as the old one.'})
        else:
            uuser.password = new_password
            uuser.save()
            return JsonResponse({'status':10062,'message':'The password is changed succeed!!!'})

@csrf_exempt
def sforget_password(request):
    postbody = request.body
    json_result = json.loads(postbody)
    email = json_result['email']
    #new_password = json_result['password']
    
    try:
        user = models.UserManage.objects.get(email=email)    
    except:
        user = None
    if user is not None:
        email_title = "电商网用户重置密码"
        email_messages =  "欢迎注册使用风炎电子商务平台，请点击以下网址重置密码，您的用户名为 " + str(user.name)
        email_body = email_messages+"\n\n"+"http://47.89.181.139/reset/api/?id=" + str(user.id)
        emailboss = EmailMessage( email_title,
                                  email_body,
                                  '1625504587@qq.com',
                                  [user.email])
        emailboss.send()
        return JsonResponse({'status':10072,'message':'The confirm email is already send!!!'})
        
    else:
        return JsonResponse({'status':10071,'message':'The email is not register'})
    
@csrf_exempt
def sforgetreset_password(request):
    userid = request.GET['id']
    postbody = request.body
    json_result = json.loads(postbody)
    new_password = json_result['password']
    
    try:
        user = models.UserManage.objects.get(id=userid)
    except:
        user = None
    if user is not None:
        if new_password == user.password:
            return JsonResponse({'status':10081,'message':'The password can not be the same as the old one.'})
        else:
            user.password = new_password
            user.save()
            return JsonResponse({'status':10082,'message':'The password is reseted succeed!!!'})
    else:
        return JsonResponse({'status':10083,'message':'system error'})








