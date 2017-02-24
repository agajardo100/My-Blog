from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404,redirect
from django.utils import timezone

from urllib.parse import quote_plus

from .models import Post
from .forms import PostForm
from comments.forms import CommentForm
from comments.models import Comment


def about(request):
    return render(request,'about.html', {})

# List of Blog Posts
def post_list(request):
    if request.user.is_staff or request.user.is_superuser:
        queryset_list = Post.objects.all()
    else:
        queryset_list = Post.objects.active()
    search_query = request.GET.get("q")

    if search_query:
        queryset_list = queryset_list.filter(
                Q(title__icontains=search_query)|
				Q(content__icontains=search_query)|
				Q(user__first_name__icontains=search_query) |
				Q(user__last_name__icontains=search_query)
                ).distinct()

    paginator = Paginator(queryset_list, 2) # Show 5 Blog Posts per page
    page_request_var = "page"
    page = request.GET.get(page_request_var)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)

    context = {
        'title': "List posts",
        'object_list': queryset,
        'page_request_var': page_request_var,
    }
    return render(request, 'post_list.html', context)


# Create a Blog Post
@login_required
def post_create(request):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.save()
        messages.success(request, "Sucessfully Created")
        return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        'form': form,
    }
    return render(request, 'post_form.html', context)


# Retrieve a Blog Post's details
def post_detail(request, slug):
    instance = get_object_or_404(Post, slug = slug)
    if not request.user.is_staff or not request.user.is_superuser:
        if instance.draft or instance.publish > timezone.now().date():
            raise Http404

    share_string = quote_plus(instance.content)
    comments = instance.comments
    initial_data = {
        'content_type': instance.get_content_type,
        'object_id': instance.id,
    }

    form = CommentForm(request.POST or None, initial=initial_data)

    if form.is_valid() and request.user.is_authenticated():
        c_type = form.cleaned_data.get("content_type")
        content_type = ContentType.objects.get(model= c_type)
        obj_id = form.cleaned_data.get("object_id")
        content_data = form.cleaned_data.get("content")
        parent_obj = None
        try:
            parent_id = request.POST.get("parent_id")
        except:
            parent_id = None

        if parent_id:
            parent_qs= Comment.objects.filter(id=parent_id)
            if parent_qs.exists():
                parent_obj = parent_qs.first()

        content = form.cleaned_data.get("content")
        new_comment, created = Comment.objects.get_or_create(
                            user= request.user,
                            content_type= content_type,
                            object_id = obj_id,
                            content= content,
                            parent= parent_obj,
                        )
        messages.success(request, "Sucessfully created comment")
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        'title': instance.title,
        'instance': instance,
        'share_string': share_string,
        'comments': comments,
        'comment_form' : form
    }
    return render(request, 'post_detail.html' , context)


# Update an already created Blog Post
def post_update(request, slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    instance = get_object_or_404(Post, slug = slug)
    form = PostForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, "Sucessfully Saved")
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        'title': "Detail",
        'instance': instance,
        'form': form,
    }
    return render(request, "post_form.html", context)


#TODO Search View


# Delete a Blog Post
@login_required
def post_delete(request, slug= None):
    """ Check if post exists """
    try:
        post_obj = Post.objects.get(slug=slug)
    except:
        raise Http404
    #
    if post_obj.user != request.user:
        messages.warning(request, "You cannot delete posts that are not yours.")
        error_context = {'error_message': "You do not have permission to view this.", 'code':403, }
        return render(request, "error.html", error_context, status=403) #Access Denied/Forbidden

    if request.method=='POST': #If user confirms delete
        post_obj.delete()
        messages.success(request, "Sucessfully deleted post")
        return redirect('posts:list')
    return render(request, "posts/confirm_delete.html", {"instance":post_obj, } )
