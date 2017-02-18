from django.contrib import admin
from .models import Comment


class CommentModelAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'timestamp']
    list_display_links = ['timestamp']
    list_filter = ['user', 'timestamp']

    search_fields = ['user', 'content']

    class Meta:
        model = Comment

admin.site.register(Comment, CommentModelAdmin)
