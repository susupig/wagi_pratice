# post/forms.py

# post/forms.py

from django import forms
from .models import Post, Image

# 게시글 작성 폼
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']

# 이미지 업로드 폼
class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']
