from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    # 表单类，根据模型字段自动生成表单控件
    class Meta:
        model = Comment
        fields = ['name', 'content']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '你的昵称'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '在这里写下你的评论...'
            })
        }
        labels = {
            'name': '',
            'content': ''
        }
    # Meta子类说明了空间的html属性及与模型的关联关系