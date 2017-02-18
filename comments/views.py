from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404, HttpResponse


from .models import Comment
from .forms import CommentForm
# Create your views here.

@login_required
def comment_delete(request, id):
    try:
        obj = Comment.objects.get(id= id)
    except:
        raise Http404

    if obj.user != request.user:
        messages.warning(request, "You cannot delete comments that are not yours.")
        error_context = {'status_code' : 403, 'error_message': "You do not have permission to view this."}
        return render(request, "error.html", error_context, status=403) #Access Denied/Forbidden

    if request.method == "POST": #If user wishes to delete comment
        parent_obj_url = obj.content_object.get_absolute_url() # URL of post related to comment
        obj.delete() #Delete comment
        messages.success(request, "Comment has been deleted.")
        return HttpResponseRedirect(parent_obj_url)

    context = {
        "object": obj,
    }
    return render(request, "comments/confirm_delete.html", context)


def comment_thread(request, id):
    try:
        obj = Comment.objects.get(id= id)
    except:
        raise Http404

    if not obj.is_parent:
        obj = obj.parent

    initial_data = {
        "content_type": obj.content_type, #Post related to Comment Thread
        "object_id": obj.object_id,
    }

    form = CommentForm(request.POST or None, initial = initial_data)
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
        return HttpResponseRedirect(new_comment.parent.get_absolute_url())
        
    context = {
         'comment': obj,
         'form': form,
    }
    return render(request, "comments/comment_thread.html", context)

    #TODO: Edit comments
