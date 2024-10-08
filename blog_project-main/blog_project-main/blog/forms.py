from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

class EmailBlogForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)
    comments = forms.CharField(required=False, widget=forms.Textarea)