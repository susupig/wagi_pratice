from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.forms import modelformset_factory
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Post, Image, Comment
from .forms import PostForm, ImageForm, CommentForm


def home(request):
    query = request.GET.get('q')
    filter_by = request.GET.get('filter')  # 'title', 'content', 'all' 중 하나
    posts = Post.objects.all()

    if query:
        # 쉼표 또는 띄어쓰기로 나눈 키워드 리스트
        keywords = [word for word in query.replace(',', ' ').split() if word]

        # Q 객체로 다중 조건 OR 검색 구성
        q_obj = Q()
        for word in keywords:
            if filter_by == 'title':
                q_obj |= Q(title__icontains=word)
            elif filter_by == 'content':
                q_obj |= Q(content__icontains=word)
            else:  # 전체 or 선택 안 했을 경우
                q_obj |= Q(title__icontains=word) | Q(content__icontains=word)

        posts = posts.filter(q_obj).distinct().order_by('-created_at')
    else:
        posts = posts.order_by('-created_at')

    return render(request, 'list.html', {'posts': posts})


def detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all().order_by('-created_at')  # ✅ POST 밖으로 옮김

    comment_form = CommentForm()

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()



            return redirect('detail', post_id=post.id)

    return render(request, 'detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    })


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

            return redirect('post:home')
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

    ImageFormSet = modelformset_factory(Image, form=ImageForm, extra=3, can_delete=True)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        formset = ImageFormSet(request.POST, request.FILES, queryset=post.images.all())

        if form.is_valid() and formset.is_valid():
            form.save()

            for f in formset:
                if f.cleaned_data.get('DELETE'):
                    f.instance.delete()
                elif f.cleaned_data.get('image'):
                    image = f.save(commit=False)
                    image.post = post
                    image.save()

            return redirect('detail', post_id=post.id)

    else:
        form = PostForm(instance=post)
        formset = ImageFormSet(queryset=post.images.all())

    return render(request, 'update.html', {
        'form': form,
        'formset': formset,
    })



@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if user in post.likes.all():
        post.likes.remove(user)  # 이미 눌렀으면 → 좋아요 취소
    else:
        post.likes.add(user)     # 안 눌렀으면 → 좋아요 추가

    return redirect('detail', post_id=post.id)