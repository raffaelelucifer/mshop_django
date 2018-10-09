#_*_ coding:utf-8 _*_

from django.template import RequestContext
from django.template.loader import get_template
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from mysite import models
from django.core.mail import EmailMessage, send_mail
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import date
from cart.cart import Cart
from mysite import forms
from django.contrib.auth.models import User
from django.contrib import messages
from allauth.account.decorators import verified_email_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
#from paypal.standard.forms import PayPalPaymentsForm
from django.core.urlresolvers import reverse

def index(request, cat_id=0):
    allproducts = None
    allcategories = models.Category.objects.all()
    if cat_id > 0:
        try:
            category = models.Category.objects.get(id=cat_id)
        except:
            category = None
        if category is not None:
            allproducts = models.Product.objects.filter(category=category)

    if allproducts is None:
        allproducts = models.Product.objects.all()

    paginator = Paginator(allproducts, 4)
    p = request.GET.get('p')
    try:
        products = paginator.page(p)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

#    allpolls = models.Poll.objects.all()
    cart = Cart(request)
    template = get_template('index.html')
    request_context = RequestContext(request)
    request_context.push(locals())
    html = template.render(request_context)
    return HttpResponse(html)

def product(request, product_id):
    try:
        product = models.Product.objects.get(id=product_id)
    except:
        product = None
    template = get_template('product.html')
    request_context = RequestContext(request)
    request_context.push(locals())
    html = template.render(request_context)
    return HttpResponse(html)


@login_required
def redact(request):
    template = get_template('redact.html')
    request_context = RequestContext(request)
    html = template.render(request_context)
    return HttpResponse(html)
    

@login_required
def poll(request, pollid):
    try:
        poll = models.Poll.objects.get(id = pollid)
    except:
        poll = None
    if poll is not None:
        pollitems = models.PollItem.objects.filter(poll=poll).order_by('-vote')
    template = get_template('poll.html')
    request_context = RequestContext(request)
    request_context.push(locals())
    html = template.render(request_context)
    return HttpResponse(html)

@login_required
def vote(request, pollid, pollitemid):
    target_url = '/poll/' + pollid 
    if models.VoteCheck.objects.filter(userid=request.user.id, pollid=pollid, vote_date=date.today()):
        return redirect(target_url) 
    else:
        vote_rec = models.VoteCheck(userid=request.user.id, pollid=pollid, vote_date=date.today())
        vote_rec.save()      
    try:
        pollitem = models.PollItem.objects.get(id = pollitemid)
    except:
        pollitem = None
    if pollitem is not None:
        pollitem.vote = pollitem.vote + 1
        pollitem.save()
    return redirect(target_url)

@login_required
def addpoll(request):
    if request.method == 'POST':
        post_form = forms.PostpollForm(request.POST)
        if post_form.is_valid():
            message = '添加成功'
            post_form.save()
            return HttpResponseRedirect('/')     
        else:
            message = '请填写信息'
    else:
        post_form = forms.PostpollForm()
        message = '请填写信息'
    template = get_template('postpoll.html')
    request_context = RequestContext(request)
    request_context.push(locals())
    html = template.render(request_context)
    return HttpResponse(html)

@login_required
def addpollitem(request):
    if request.method == 'POST':
        postItem_form = forms.PostitemForm(request.POST)
        if postItem_form.is_valid():
            message = '添加成功'
            postItem_form.save()
            return HttpResponseRedirect('/')     
        else:
            message = '请填写信息'
    else:
        postItem_form = forms.PostitemForm()
        message = '请填写信息'
    template = get_template('postitem.html')
    request_context = RequestContext(request)
    request_context.push(locals())
    html = template.render(request_context)
    return HttpResponse(html)

@login_required
def govote(request):
    if request.method == 'GET' and request.is_ajax():
        pollitemid = request.GET.get('pollitemid')
        pollid = request.GET.get('pollid')
        bypass = False
        if models.VoteCheck.objects.filter(userid=request.user.id, pollid=pollid, vote_date=date.today()):
            bypass = True
        else:
            vote_rec = models.VoteCheck(userid=request.user.id, pollid=pollid, vote_date=date.today())
            vote_rec.save()
        try:
            pollitem = models.PollItem.objects.get(id=pollitemid)
            if not bypass:
                pollitem.vote = pollitem.vote + 1
                pollitem.save()
            votes = pollitem.vote
        except:
            votes = 0
    else:
        votes = 0
    return HttpResponse(votes)

@login_required
def add_to_cart(request, product_id, quantity):
    product = models.Product.objects.get(id=product_id)
    cart = Cart(request)
    cart.add(product, product.price, quantity)
    return redirect('/')

@login_required
def remove_from_cart(request, product_id):
    product = models.Product.objects.get(id=product_id)
    cart=Cart(request)
    cart.remove(product)
    return redirect('/cart/')

@login_required
def cart(request):
    allcategories = models.Category.objects.all()
    cart = Cart(request)
    template = get_template('cart.html')
    request_context = RequestContext(request)
    request_context.push(locals())
    html = template.render(request_context)
    return HttpResponse(html)

@verified_email_required
def order(request):
    allcategories = models.Category.objects.all()
    cart = Cart(request)
    if request.method == 'POST':
        user = User.objects.get(username=request.user.username)
        new_order = models.Order(user=user)
        
        form = forms.OrderForm(request.POST, instance=new_order)
        if form.is_valid():
            order = form.save()
            email_messages = "您订购的内容如下: \n"
            for item in cart:
                models.OrderItem.objects.create(order=order,
                                                product=item.product,
                                                price=item.product.price,
                                                quantity=item.quantity)
                email_messages = email_messages + "\n" + \
                                "{}, {}, {}".format(item.product, \
                                             item.product.price, item.quantity)
            email_messages = email_messages + \
                            "\n 以上共计{}元\nhttp://mshop.raffaele.com 感谢您的订购!".\
                            format(cart.summary())
            messages.add_message(request, messages.INFO, "订单已保存，我们会尽快处理。")
            #send_mail("感谢您的订购",
            #          email_messages,
            #          '迷销电商',
            #          [request.user.email],)
            #send_mail("有人订购产品",
            #          email_messages,
            #          '迷你电商',
            #          ['1625504587@qq.com'],)
            emailboss = EmailMessage( '有新的订单',
                                          email_messages,
                                          '1625504587@qq.com',
                                          [request.user.email])
            emailboss.send()
            cart.clear()
            return redirect('/myorders/')
    else:
        form = forms.OrderForm()
    
    template = get_template('order.html')
    request_context = RequestContext(request)
    request_context.push(locals())
    html = template.render(request_context)
    return HttpResponse(html)

@login_required
def myorders(request):
    allcategories = models.Category.objects.all()
    orders = models.Order.objects.filter(user=request.user)
    template = get_template('myorders.html')
    request_context = RequestContext(request)
    request_context.push(locals())
    html = template.render(request_context)
    return HttpResponse(html)

#@csrf_exempt
#def payment_done(request):
#    template = get_template('payment_done.html')
#    request_context = RequestContext(request)
#    request_context.push(locals())
#    html = template.render(request_context)
#    return HttpResponse(html)
#
#@csrf_exempt
#def payment_canceled(request):
#    template = get_template('payment_canceled.html')
#    request_context = RequestContext(request)
#    request_context.push(locals())
#    html = template.render(request_context)
#    return HttpResponse(html)
#
#@login_required
#def payment(request, order_id):
#    allcategories = models.Category.objects.all()
#    try:
#        order = models.Order.objects.get(id=order_id)
#    except:
#        messages.add_message(request, messages.WARNING, "订单编号错误，无法处理付款")
#        return redirect('/')
#    allorderitems = models.OrderItem.objects.filter(order=order)
#    items = list()
#    total = 0
#    for orderitem in allorderitems:
#        t = dict()
#        t['name'] = orderitem.product.name
#        t['price'] = orderitem.product.price
#        t['quantity'] = orderitem.product.quantity
#        t['subtotal'] = orderitem.product.price * orderitem.quantity
#        total = total + orderitem.product.price
#        items.append(t)
#
#    host = request.get_host()
#    paypal_dict = {
#        "business": settings.PAYPAL_REVEIVER_EMAIL,
#        "amount": total,
#        "item_name": "迷你电商货品编号:{}".format(order_id),
#        "invoice": "invoice-{}".format(order_id),
#        "currency_code": 'TWD',
#        "notify_url": "http://{}{}".format(host, reverse('paypal-ipn')),
#        "return_url": "http://{}/done/".format(host),
#        "cancel_return": "http://{}/canceled/".format(host),
#    }
#
#    paypal_form = PayPalPaymentsForm(initial=paypal_dict)
#    template = get_template('payment.html')
#    request_context = RequestContext(request)
#    request_context.push(locals())
#    html = template.render(request_context)
#    return HttpResponse(html)
        
        
