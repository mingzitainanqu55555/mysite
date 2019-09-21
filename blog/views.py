from django.shortcuts import render,get_object_or_404
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from .models import Blog,BlogType
from read_statistics.utils import read_statistics_once_read

from comment.models import Comment
from comment.forms import CommentForm
# Create your views here.

def get_blog_list_common_data(request,blogs_all_list):
    paginator = Paginator(blogs_all_list, settings.EACH_PAGE_BLOGS_NUMBER)  # 每10页进行分页
    page_num = request.GET.get('page', 1)  # 获取页码参数 没有的话默认为1
    page_of_blogs = paginator.get_page(page_num)
    currentr_page_num = page_of_blogs.number  # 获取当前页码
    page_range = list(range(max(currentr_page_num - 2, 1), min(currentr_page_num + 3, paginator.num_pages + 1)))
    if currentr_page_num > 4:
        page_range.insert(0, '...')
    if currentr_page_num >= 4:
        page_range.insert(0, 1)
    if paginator.num_pages - currentr_page_num > 3:
        page_range.append('...')
    if paginator.num_pages - currentr_page_num >= 3:
        page_range.append(paginator.num_pages)
    #获取博客分类的对应博客数量 第1种
    '''blog_types=BlogType.objects.all()
    blog_types_list=[]
    for blog_type in blog_types:
        blog_type.blog_count=Blog.objects.filter(blog_type=blog_type).count()
        blog_types_list.append(blog_type)'''
    # 获取日期归档的对应博客数量
    blog_dates = Blog.objects.dates('created_time', 'month', order="DESC")
    blog_dates_dict={}
    for blog_date in blog_dates:
        blog_count=Blog.objects.filter(created_time__year=blog_date.year,
                                       created_time__month=blog_date.month).count()
        blog_dates_dict[blog_date]=blog_count

    # print(min(paginator.num_pages + 1, currentr_page_num + 3))
    context = {}
    context['blogs'] = page_of_blogs.object_list
    context['page_of_blogs'] = page_of_blogs
    context['page_range'] = page_range
    context['blog_types'] = BlogType.objects.all()
    context['blog_dates'] =blog_dates_dict
    return context

def blog_list(request):
    blogs_all_list = Blog.objects.all()
    context=get_blog_list_common_data(request,blogs_all_list)
    return render(request,'blog/blog_list.html',context)
def blog_with_type(request,blog_type_pk):
    blog_type=get_object_or_404(BlogType,pk=blog_type_pk)
    blogs_all_list = Blog.objects.filter(blog_type=blog_type)
    context = get_blog_list_common_data(request,blogs_all_list)
    context['blog_type'] = blog_type

    return render(request,'blog/blogs_with_type.html',context)
def blogs_with_date(request,year,mouth):
    blogs_all_list = Blog.objects.filter(created_time__year=year,created_time__month=mouth)
    context = get_blog_list_common_data(request,blogs_all_list)
    context['blogs_with_date'] = '%s年%s月' %(year,mouth)
    return render(request, 'blog/blogs_with_date.html', context)
def blog_detail(request,blog_pk):
    context = {}
    blog = get_object_or_404(Blog,pk=blog_pk)
    context['blog'] = blog

    #返回评论
    blog_content_type = ContentType.objects.get_for_model(blog)
    comments=Comment.objects.filter(content_type=blog_content_type,object_id=blog.pk,parent=None)
    context['comments']=comments.order_by('-comment_time')
    #阅读数加1
    read_cookie_key=read_statistics_once_read(request,blog)
    #用来实现前一篇后一篇
    ## 重难点 filter的各种查询 __gt指大于
    context['previous_blog']=Blog.objects.filter(created_time__gt=blog.created_time).last()
    ## 重难点 filter的各种查询 __lt指小于
    context['next_blog']=Blog.objects.filter(created_time__lt=blog.created_time).first()
    context['comment_form']=CommentForm(initial={'content_type':blog_content_type.model,'object_id':blog_pk,'reply_comment_id': 0})

    response=render(request,'blog/blog_detail.html',context)
    response.set_cookie(read_cookie_key,'hi')#阅读标记
    return response