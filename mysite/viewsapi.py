#_*_ coding:utf-8 _*_

from mysite import models
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.decorators.csrf import  csrf_exempt
from django.core import serializers
#from singledispatch import singledispatch
import subprocess
import json
import datetime
from decimal import Decimal
from cart.cart import Cart
from cart.models import Item
import cart
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail

#测试的时候把csrf关了

@csrf_exempt
def product_get(req):
    #获取 post 数据
    #if req.method == 'POST':
    postbody = req.body
    json_result = json.loads(postbody)
    #cate = req.POST.get('cate','')
    #page = req.POST.get('page','')
    cate = json_result['cat']
    page = json_result['pag']
    context ={'status':200}
    context['cate'] , context['page'] = cate ,page

        #根据类别在数据库找到相应数据
    if cate == 0:
        #Products_list = serializers.serialize("json", models.Product.objects.all())
        Products_list = models.Product.objects.all()
    else:
        try:
            category = models.Category.objects.get(id=cate)
        except:
            category = None
        if category is not None:
            #Products_list = serializers.serialize("json", models.Product.objects.filter(category=category))
            Products_list = models.Product.objects.filter(category=category)
        else:
            Products_list = None

        #数据为空直接返回json
    if Products_list == None:
        return JsonResponse({'status':10021,'message':'parameter error'})

    #分页
    paginator = Paginator(Products_list,4)
    try:
        Productss = paginator.page(page)
    except PageNotAnInteger:
        Productss = paginator.page(1)
    except EmptyPage:
        Productss = paginator.page(paginator.num_pages)

    #一页商品的个数，是否有前一页，是否有后一页
    context['queryNum'],context['hasPrevios'],context['hasNext'] = len(Productss),Productss.has_previous(),Productss.has_next()

    #将数据存入data[]
    data = []
    if Productss:
        for i in Productss:
            Product = {}
            Product['id'] = str(i.id).strip('L')
            Product['sku'] = i.sku
            Product['name'] = i.name
            Product['description'] = i.description
            catedev1 = str(i.category)
            Product['category'] = catedev1.strip('<>')
            catedev2 = str(i.image)
            #Product['image'] = catedev2.strip('<>')
            cateimage = catedev2.strip('<>').lower()
            cateimage2 = cateimage.replace('%','').replace('$','').replace('&','').replace('@','').replace('#','').replace('=','').replace('.','').replace(',','').split('jpg')[0] + '.jpg'
            simage = subprocess.Popen(['find', '/data/mshop/staticfiles', '-name', '%s' % cateimage2], stdout=subprocess.PIPE)
            infosimage = simage.communicate()
            simage.stdout.close()
            #urlimage = '47.89.181.139' + '/data/mshop/staticfiles/media/filer' + str(infosimage[0].replace('\n', '')) 
            Product['image'] = '47.89.181.139' + infosimage[0].replace('\n', '').replace('/data/mshop/staticfiles','')
            Product['stock'] = i.stock
            catedev3 = str(i.price)
            Product['price'] = catedev3.strip('Decimal()')
            data.append(Product)
        # 将data存进context
        context.update({'data':data})
        # 返回json
        #return JsonResponse(context)
        return HttpResponse(json.dumps(context), content_type="application/json")
        #return json.dumps(context, cls=ExtendJSONEncoder)
        #context_value =  serializers.serialize("json", context)
        #return HttpResponse(context_value)
    else:
        return  JsonResponse({'status':10022,'message':'query Products isempty'})


@csrf_exempt
def putinto_cart(request):
    postbody = request.body
    json_result = json.loads(postbody) 
    quantity = json_result['cou']
    #unit_price = json_result['price']
    product_id = json_result['obj']
    context ={'status':200}
    context['quantity'] , context['product_id'] = quantity ,product_id
    #return HttpResponse(json.dumps(context), content_type="application/json")
    #context ={'status':200}
    #context['quantity'] , context['product_id'] = quantity ,product_id

    #data = []
    product = models.Product.objects.get(id=int(product_id))
    cart = Cart(request)
    cart.add(product, product.price, quantity)
    cart_count = cart.count()
    #request.session['cart_id'] = cart.cart_id

    return HttpResponse(json.dumps(cart_count), content_type="application/json")

#@csrf_exempt
#def list_cart(request):
#    context ={'status':200}
#    #cartid = request.session['cart_id']
#    items = Item.objects.get(cart_id=cartid)
#    data = []
#    if items:
#        for item in items:
#            cartitem = {}
#            cartitem['id'] = item.product.id
#            cartitem['name'] = item.product.name
#            cartitem['price'] = str(item.product.price).strip('Decimal()')
#            cartitem['quantity'] = str(item.quantity).strip('L')
#            cartitem['total_price'] = str(item.total_price).strip('Decimal()')
#            data.append(cartitem)
#        context.update({'data':data})
#        return HttpResponse(json.dumps(context), content_type="application/json")
#    else:
#        return JsonResponse({'status':10024,'message':'The cart is empty'})

@csrf_exempt
def list_cart(request):
    cart = Cart(request)
    context ={'status':200}
    data = []
    if cart is not None:
        for item in cart:
            cartitem = {}
            cartitem['id'] = item.product.id
            cartitem['name'] = item.product.name
            cartitem['price'] = str(item.product.price).strip('Decimal()')
            cartitem['quantity'] = str(item.quantity).strip('L')
            cartitem['total_price'] = str(item.total_price).strip('Decimal()')
            data.append(cartitem)
        context.update({'data':data})
        return HttpResponse(json.dumps(context), content_type="application/json")
    else:
        return JsonResponse({'status':10024,'message':'The cart is empty'})

@csrf_exempt
def remove_from_cart(request):
    postbody = request.body
    json_result = json.loads(postbody)
    product_id = json_result['id']
    product = models.Product.objects.get(id=int(product_id))
    cart=Cart(request)
    cart.remove(product)
    cart_count = cart.count()
    return HttpResponse(json.dumps(cart_count), content_type="application/json")

@csrf_exempt
def add_to_order(request):
    cart = Cart(request)
    #user = models.UserManage.objects.get(name=request.user.username)
    userid = request.session['uuserid']
    user = models.UserManage.objects.get(id=userid)
    order = models.Order(user=user, createdat=datetime.datetime.now())
    order.save()
    email_messages = "您订购的内容如下: \n"
    for item in cart:
        models.OrderItem.objects.create(
                            order = order,
                            product = item.product,
                            price = item.product.price,
                            quantity = item.quantity)
                            #total_price = item.total_price())
     
        email_messages = email_messages + "\n" + \
                                "{}, {}, {}".format(item.product, \
                                             item.product.price, item.quantity)
    email_messages = email_messages + \
                    "\n 以上共计{}元\nhttp://mshop.raffaele.com 感谢您的订购!".\
                    format(cart.summary())
    messages.add_message(request, messages.INFO, "订单已保存，我们会尽快处理。")
    emailboss = EmailMessage( '有新的订单',
                                  email_messages,
                                  '1625504587@qq.com',
                                  [user.email])
    emailboss.send()
    cart.clear()
    return JsonResponse({'status':10091,'message':'Add to the order!!!'})

@csrf_exempt
def list_order(request):
    context ={'status':200}
    #uuser = models.UserManage.objects.get(name=request.user.username)
    #userid = request.session['uuserid']
    #user = models.UserManage.objects.get(id=userid)
    userid = request.session['uuserid']
    user = models.UserManage.objects.get(id=userid)
    order = models.Order.objects.filter(user=user)
    order_item = models.OrderItem.objects.filter(order=order)
    data = []
    if order_item:
        for i in order_item:
            item = {}
            item['product'] = str(i.product).strip('<>')
            item['price'] = str(i.price).strip('Decimal()')
            item['quantity'] = str(i.quantity).strip('L')
    #        item['total_price'] = i.total_price
            data.append(item)
        context.update({'data':data})
        return HttpResponse(json.dumps(context), content_type="application/json")
    else:
        return  JsonResponse({'status':10011,'message':'order is empty'})
   
@csrf_exempt
def add_into_myorders(request):
    postbody = request.body
    json_result = json.loads(postbody)
    name = json_result['name']
    phone = json_result['phone']
    addr = json_result['addr']
    
    userid = request.session['uuserid']
    user = models.UserManage.objects.get(id=userid)
    #myorder = models.Order(createdat=datetime.datetime.now(), updateat=datetime.datetime.now())
    allorder = models.Order.objects.all()
    allupdate = []
    for all in allorder:
        allupdate.append(all.updateat)
    for up in allupdate:
        myorder = models.Order.objects.get(user=user, updateat=up)
        myorder.full_name = name
        myorder.phone = phone
        myorder.address = addr
        myorder.updateat=datetime.datetime.now()
        myorder.save()
        break

    return  JsonResponse({'status':10021,'message':'Add to my orders succeed!!!'})

@csrf_exempt
def list_from_myorders(request):
    userid = request.session['uuserid']
    user = models.UserManage.objects.get(id=userid)
    context = {'status':200}
    try:    
        myorder = models.Order.objects.filter(user=user)
    except:
        myorder = None
    if myorder is not None:
        data = []
        for item in myorder:
            order = {}
            order['id'] = str(item.id).strip('<>')
            order['full_name'] = str(item.full_name).strip('<>')
            order['address'] = item.address
            order['phone'] = str(item.phone).strip('<>')
            order['createdat'] = str(item.createdat).strip('<>')
            order['paid'] = str(item.paid).strip('<>')
            data.append(order)
        context.update({'data':data})
        return HttpResponse(json.dumps(context), content_type="application/json")
    else:
        return  JsonResponse({'status':10031,'message':'There is no order now.'})
            
   
    
    

    
