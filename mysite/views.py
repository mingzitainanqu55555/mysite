import datetime
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from django.core.cache import cache

from read_statistics.utils import get_seven_days_read_date,get_today_hot_data,get_yesterday_hot_data
from blog.models import Blog
from django.urls import reverse
from user.forms import LoginForm,RegForm

def get_7_days_hot_blogs():
    today=timezone.now().date()
    date=today-datetime.timedelta(days=7)
    blogs=Blog.objects.filter(read_details__date__lt=today,read_details__date__gte=date).values('id','title').annotate(read_num_sum=Sum('read_details__read_num')).order_by('-read_num_sum')
    return blogs[:7]

def home(request):
    blog_content_type=ContentType.objects.get_for_model(Blog)
    dates,read_nums=get_seven_days_read_date(blog_content_type)
    #获取7天热门数据 缓存策略
    all_7_hot_data=cache.get('all_7_hot_data')
    if all_7_hot_data is None:
        all_7_hot_data = get_7_days_hot_blogs()
        cache.set('all_7_hot_data',all_7_hot_data,60*60*2)
        #print('缓存?')

    context={}
    context['read_nums']=read_nums
    context['dates']=dates
    context['today_hot_data']=get_today_hot_data(blog_content_type)
    context['yesterday_hot_data']=get_yesterday_hot_data(blog_content_type)
    context['all_7_hot_data']=all_7_hot_data
    return render(request,'home.html',context)
