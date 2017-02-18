from django import forms
from pagedown.widgets import PagedownWidget
from .models import Post
from django.utils import timezone

class PostForm(forms.ModelForm):
    content = forms.CharField(widget=PagedownWidget(show_preview=False))
    publish = forms.DateField(widget=forms.SelectDateWidget, initial=timezone.now().date())
    class Meta:
        model = Post
        fields = [
            'title',
            'content',
            'image',
            'draft',
            'publish',
        ]
