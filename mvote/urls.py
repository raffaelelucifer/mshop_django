"""mvote URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from mysite import views
from mysite import viewsapi
from usermanage import userviews
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^(\d*)$', views.index),
#    url(r'^poll/(\d+)$', views.poll, name='poll-url'),
#    url(r'^vote/(\d+)/(\d+)$', views.vote, name='vote-url'),
#    url(r'^redact/$', views.redact, name='redact-url'),
#    url(r'^addpoll/$', views.addpoll, name='addpoll-url'),
#    url(r'^addpollitem/$', views.addpollitem, name='addpollitem-url'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^filer/', include('filer.urls')),
    url(r'^product/(\d+)$', views.product, name='product-url'),
    url(r'^cart/$', views.cart),
    url(r'^additem/(\d+)/(\d+)$', views.add_to_cart, name='additem-url'),
    url(r'^removeitem/(\d+)/$', views.remove_from_cart, name='removeitem-url'),
    url(r'^order/$', views.order),
    url(r'^myorders/$', views.myorders),
    #url(r'^paypal/', include('paypal.standard.ipn.urls')),
    #url(r'^payment/(\d+)/$', views.payment),
    #url(r'^done/$', views.payment_done),
    #url(r'^canceled/$', views.payment_canceled),
    url(r'^product_get/api/', viewsapi.product_get),
    url(r'^addinto_cart/api/', viewsapi.putinto_cart),
    url(r'^list_cart/api/', viewsapi.list_cart),
    url(r'^removefrom_cart/api/', viewsapi.remove_from_cart),
    url(r'^register/api/', userviews.sregister),
    url(r'^active/', userviews.sactive),
    url(r'^login/api/', userviews.slogin),
    url(r'^resetpassword/api/', userviews.sreset_password),
    url(r'^forget/api/', userviews.sforget_password),
    url(r'^reset/api/', userviews.sforgetreset_password),
    url(r'^addto_order/api/', viewsapi.add_to_order),
    url(r'^listorder/api/', viewsapi.list_order),
    url(r'^addto_myorder/api/', viewsapi.add_into_myorders),
    url(r'^listmyorder/api/', viewsapi.list_from_myorders),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

