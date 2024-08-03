# Импортируем класс, который говорит нам о том,
# что в этом представлении мы будем выводить список объектов из БД
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin # специальный миксин для представлений,
                                                    # работающих тольбко после авторизации. Альтернатива
                                                    # комбинации login_required method_decorator
from django.views import View
from django.core.mail import send_mail, EmailMultiAlternatives # объект письма с HTML
from django.template.loader import render_to_string # функция для рендера HTML в строку
from django.utils.decorators import method_decorator # данный декоратор применяется для метода dispatch класса представлений
from django.views.generic import ListView, DetailView, TemplateView
from django.shortcuts import render
from .models import Post, Comment, Category, Mail, PostCategory, UserSubcribes, User
from .filters import PostFilter
from .forms import PostForm, CategorySubcsribeForm
from django.shortcuts import reverse, render, redirect
from datetime import datetime
from pprint import pprint


class ProtectedView(LoginRequiredMixin,TemplateView):
    template_name = 'flatpages/authorization.html'

class PostsList(LoginRequiredMixin, ListView): #класс для показа общего списка всех публикаций
    # Указываем модель, объекты которой мы будем выводить
    model = Post
    # Поле, которое будет использоваться для сортировки объектов
    # ordering = 'create_time'
    # Указываем имя шаблона, в котором будут все инструкции о том,
    # как именно пользователю должны быть показаны наши объекты
    template_name = 'flatpages/news.html'
    # Это имя списка, в котором будут лежать все объекты.
    # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
    context_object_name = 'post'
    paginate_by = 10

    def form(self): # метод для присвоения формы, используемой при подписке на категории новостей
        form = CategorySubcsribeForm()  # форма, отображающая список категорий, на которые еще не подписан пользователь
        form.fields['category'].queryset = (
            Category.objects.exclude(usersubcribes__subcribe=self.request.user))
        form_subsribe = CategorySubcsribeForm() # форма, в которой отображается список подписок пользователя
        form_subsribe.fields['category'].label = 'Подписки пользователя'
        form_subsribe.fields['category'].queryset =(
            Category.objects.filter(usersubcribes__subcribe=self.request.user)) # выводится на форме список
                                                    # категорий публикаций, на которые подписан пользователь

        return (form, form_subsribe)

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['form'] = self.form()[0]
        context['form_subscribe'] = self.form()[1]
        return context

    def post(self, request, *args, **kwargs):
        if request.method=='POST':
            user=request.user # присвоение переменной текущего пользователя
            form = CategorySubcsribeForm(request.POST)
            if request.POST['subscribe']=='Подписаться':
                if form.is_valid():
                    for i in form.cleaned_data['category']:
                        UserSubcribes.objects.create(subcribe=user, category=i)
            else:
                list=[]
                if form.is_valid():
                    for i in form.cleaned_data['category']:
                        user_sub=UserSubcribes.objects.get(subcribe=user, category=i)
                        list.append(user_sub)
                    for i in list:
                        i.delete()
            return redirect('main_page')

class PostDetail(LoginRequiredMixin, DetailView): # детальная информация конкретного поста
    model = Post
    template_name = 'flatpages/post.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs): # модернизация контекста для отображения комментариев
                                                # на отдельной странице поста
        context=super().get_context_data(**kwargs)
        context['comm'] = Comment.objects.filter(post_id=self.kwargs['pk'])
        form=PostForm(initial={'title': self.object.title,
                               'content': self.object.content,
                               'create_time': self.object.create_time,
                               'author': self.object.author,
                               'postType': self.object.postType,
                               'category': PostCategory.objects.filter(post_id=self.kwargs['pk']) }
                               )
        form.fields['author'].disabled = True
        form.fields['title'].disabled = True
        form.fields['content'].disabled = True
        form.fields['create_time'].disabled = True
        form.fields['postType'].disabled = True
        form.fields['category'].disabled = True
        context['form'] = form
        context['id']=self.object.pk # переменная контекста, передающая id поста
        return context

class PostFilterView(ListView): # класс для отображения фильтра поста на отдельной HTML странице 'search.html'
    model = Post
    template_name = 'flatpages/search.html'
    context_object_name = 'post'
    paginate_by =3

    def get_queryset(self):
        queryset=super().get_queryset()
        self.filter = PostFilter(self.request.GET,queryset)
        return self.filter.qs

    def get_context_data(self,  **kwargs): #добавление в контекст фильтра
        context=super().get_context_data(**kwargs)
        context['filter']=self.filter
        return context

@login_required
def create_post(request): # функция для создания и добавления новой публикации
    form=PostForm()
    form.fields['create_time'].disabled = True
    if request.method=='POST':
        form=PostForm(request.POST)
        if form.is_valid():
            post=Post.objects.create(content=form.cleaned_data.get('content'),
                                     author=form.cleaned_data.get('author'),
                                     title=form.cleaned_data.get('title'),
                                     postType=form.cleaned_data.get('postType')
                                     )
            for i in form.cleaned_data['category']:
                PostCategory.objects.create(category_id=i.pk, post_id=post.pk)
            recepient_list=[]

            # Рассылка писем подписчикам по добавленной статье
            for i in UserSubcribes.objects.filter(category=post.category):
                if i.subcribe.email not in recepient_list: # подписчик может быть подписан на несколько категорий,
                                    # в то же время пост может относиться к нескольким категориям одновременно.
                                    # Поэтому, чтобы на одну и ту же статью не было повторных сообщенгий пользователю
                                    # и вводится данное условие
                    recepient_list.append(i.subcribe.email)
            subcribers=Category.objects.filter(category=post.category)
            render_to_string('flatpages/send_html_mail.html',{'post':post})
            send_mail(subject='New',
                      message=f'New post {post.title} has been',
                      from_email='sportactive.SK@yandex.ru')
            return render(request, 'flatpages/messages.html', {'state':'Новая публикация добавлена успешно!','list':recepient_list})
    return render(request, 'flatpages/edit.html', {'form':form, 'button':'Опубликовать'})

def test(request):
    if request.method == 'POST':
        pk = request.POST['post_id']
        post=Post.objects.get(pk=pk)
        email=request.POST['email']
        list=[]
        for i in PostCategory.objects.filter(post_id=post.pk):
            for j in UserSubcribes.objects.filter(category=i.category):
                list.append(j.subcribe.email)
        html_content=render_to_string('flatpages/send_html_mail.html',{'post':post})
        msg = EmailMultiAlternatives(subject=f'{post.title} has been',
                                     body=html_content,
                                     from_email='sportactive.SK@yandex.ru',
                                     to=list
                                     )

        msg.attach_alternative(html_content,'text/html')
        msg.send()


        return render(request, 'flatpages/messages.html',{'state':list})
    return render(request, 'flatpages/test.html')

@login_required
def edit_post(request, pk): # функция для редактирования названия и содержания поста
    post = Post.objects.get(pk=pk)
    form=PostForm(initial={'create_time':post.create_time,
                           'author':post.author,
                           'postType':post.postType,
                           'title': post.title,
                           'content': post.content,
                           'category': PostCategory.objects.filter(post_id=post.pk)
                           })
    form.fields['postType'].disabled = True
    form.fields['author'].disabled = True
    form.fields['create_time'].disabled = True

    # recepient_list = []
    recepient_list=request.user.is_authenticated
    # for i in PostCategory.objects.filter(post_id=post.pk):
    #     for j in UserSubcribes.objects.filter(category_id=i.category_id):
    #     # if i.subcribe.email not in recepient_list:  # подписчик может быть подписан на несколько категорий
    #         # в то же время пост может относиться к нескольким категориям одновременно.
    #         # Поэтому, чтобы на одну и ту же статью не было повторных сообщенгий пользователю
    #         # и вводится данное условие
    #         recepient_list.append(j.subcribe.email)

    if request.method=='POST':
        form=PostForm(request.POST, post)
        form.fields['postType'].required = False
        form.fields['author'].required = False
        form.fields['create_time'].required = False
        try:
            if form.is_valid():
                Post.objects.filter(pk=pk).update(**{'author':post.author,
                                                     'postType':post.postType,
                                                     'create_time':post.create_time,
                                                     'title':form.cleaned_data['title'],
                                                     'content':form.cleaned_data['content']})
                return render(request, 'flatpages/messages.html', {'state': 'Изменения успешно сохранены.'})
        except TypeError:
            return render(request, 'flatpages/messages.html', {'state':'Возникла ошибка! Возможно причина в превышении лимита названия поста, попавшего в БД не через форму'})
    return render(request, 'flatpages/edit.html', {'form':form, 'button':'Сохранить изменения', 'list':recepient_list})

def delete_post(request, pk):
    post = Post.objects.get(pk=pk)
    if request.method=='POST':
        post.delete()
        return render(request, 'flatpages/messages.html', {'state': 'Пост успешно удален'})
    return render(request, 'flatpages/del_post.html',{'post':post})

class MailView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'flatpages/mail.html', {})

    def post(self, request, *args, **kwargs):
        mail = Mail(client=request.POST['client_name'],
                                   # date=datetime.strptime(request.POST['date'],''),
                                   message=request.POST['message'])
        mail.save()

        # преоьразование HTML в текст
        html_content =render_to_string('flatpages/send_html_mail.html', {'mail':mail})
        msg=EmailMultiAlternatives(subject=f'{mail.client} ',
                                   body=mail.message,
                                   from_email='sportactive.SK@yandex.ru',
                                   to=[f'{request.POST['email']}'])
        msg.attach_alternative(html_content, 'text/html')
        msg.send()
        return render(request, 'flatpages/messages.html', {})




# -! Неиспользуемые классы ниже
class CommListView(ListView):  # класс для отобрпажения
    model = Comment
    template_name = 'flatpages/comm.html'
    context_object_name = 'cmts'