import datetime

from django import forms
from .models import Post, Author, Category
from django.core.exceptions import ValidationError
from datetime import datetime

class PostForm(forms.Form):
    author = forms.ModelChoiceField(label='Автор', queryset=Author.objects.all())
    postType=forms.ChoiceField(label='Тип публикации',choices=Post.post_type)
    create_time = forms.DateTimeField  (label='Дата создания публикации', required=False)
    title = forms.CharField(label='Заголовок публикации', max_length=50)
    content= forms.CharField(label='Содержание публикации', widget=forms.Textarea)
    category = forms.ModelMultipleChoiceField(queryset=Category.objects.all(), widget=forms.CheckboxSelectMultiple)

    def clean(self): # проверка не слишком ли короткое название
        check=super().clean()
        title=check.get('title')
        if len(title)<5:
            raise ValidationError({'title':'Слишком короткое название.'})
        return check


class CategorySubcsribeForm(forms.Form): # отдельная форма для оформления и редактирования подписок
    # поле, в котором выводится список категорий постов для подписки
    category = forms.ModelMultipleChoiceField(queryset=Category.objects.all(), widget=forms.CheckboxSelectMultiple, label='Доступные категории')




