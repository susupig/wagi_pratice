from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Image
from .forms import PostForm, ImageForm
from django.forms import modelformset_factory
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

def home(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'list.html', {'posts': posts})


def detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'detail.html', {'post': post})


@login_required
def write(request):
    ImageFormSet = modelformset_factory(Image, form=ImageForm, extra=3)

    if request.method == 'POST':
        post_form = PostForm(request.POST)
        formset = ImageFormSet(request.POST, request.FILES, queryset=Image.objects.none())

        if post_form.is_valid() and formset.is_valid():
            post = post_form.save(commit=False)
            post.author = request.user  # ✅ 로그인한 유저를 작성자로 설정
            post.save()

            for form in formset.cleaned_data:
                if form:
                    image = form['image']
                    Image.objects.create(post=post, image=image)

            return redirect('home')
    else:
        post_form = PostForm()
        formset = ImageFormSet(queryset=Image.objects.none())

    return render(request, 'write.html', {
        'post_form': post_form,
        'formset': formset
    })


@login_required
def update(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        return HttpResponseForbidden("수정 권한이 없습니다.")

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('detail', post_id=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, 'update.html', {'form': form})   

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        user = User.objects.create_user(username=username, password=password, email=email)
        login(request, user)  # 가입 후 바로 로그인
        return redirect('home')
    return render(request, 'signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': '로그인 실패'})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

