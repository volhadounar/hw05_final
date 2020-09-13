from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.cache import cache_page

from . forms import CommentForm, PostForm
from . models import Follow, Group, Post


User = get_user_model()


@cache_page(10)
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator},
        content_type='text/html', status=200
    )


def group_posts(request, slug):
    gr = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=gr)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': gr,
                                          'page': page,
                                          'paginator': paginator},
                  content_type='text/html', status=200)


@login_required
def new_post(request):
    if request.method != 'POST':
        form = PostForm()
        return render(request, 'newpost.html', {'form': form})
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'newpost.html', {'form': form})
    new_item = form.save(commit=False)
    new_item.author = request.user
    new_item.save()
    return redirect(reverse('index'))


def profile(request, username):
    post_user = get_object_or_404(User, username=username)
    posts = post_user.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    cnt_following = post_user.follower.count()
    cnt_follower = post_user.following.count()
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user).filter(
                    author=post_user).exists()
    else:
        following = True
    return render(request, 'profile.html', {'page': page,
                                            'paginator': paginator,
                                            'author': post_user,
                                            'follower_cnt': cnt_follower,
                                            'following_cnt': cnt_following,
                                            'following': following},
                  content_type='text/html', status=200)


def post_view(request, username, post_id):
    post_user = User.objects.get(username=username)
    cnt = post_user.posts.all().count()
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = CommentForm()
    comments = post.comments.all()
    return render(request, 'post.html', {'post': post,
                                         'count': cnt,
                                         'post_user': post.author,
                                         'form': form,
                                         'comments': comments},
                  content_type='text/html', status=200)


def check_author(func):
    def wrapper(request, username, post_id):
        if request.user.get_username() != username:
            url = reverse('post', kwargs={'username': username,
                          'post_id': post_id})
            return redirect(url)
        return func(request, username, post_id)
    return wrapper


@login_required
@check_author
def post_edit(request, username, post_id):
    if request.method != 'POST':
        post = get_object_or_404(Post, pk=post_id, author__username=username)
        form = PostForm(instance=post)
        return render(request, 'newpost.html', {'form': form, 'post': post})
    edited_post = get_object_or_404(Post, pk=post_id,
                                    author__username=username)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=edited_post)
    if not form.is_valid():
        return render(request, 'newpost.html', {'form': form,
                                                'post': edited_post},
                      content_type='text/html', status=200)
    form.save()
    return redirect(edited_post)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        return redirect(post)
    new_item = form.save(commit=False)
    new_item.post = post
    new_item.author = request.user
    new_item.save()
    return redirect(new_item.post)


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def follow_index(request):
    following_objs = request.user.follower.all()
    posts = Post.objects.filter(author__following__in=following_objs)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {'page': page,
                                           'paginator': paginator},
                  content_type='text/html', status=200)


@login_required
def profile_follow(request, username):
    if request.user.get_username() == username:
        return redirect(reverse('profile', kwargs={'username': username}))
    author = get_object_or_404(User, username=username)
    Follow.objects.get_or_create(user=request.user, author=author)
    return redirect(reverse('profile', kwargs={'username': username}))


@login_required
def profile_unfollow(request, username):
    if request.user.get_username() == username:
        return redirect(reverse('profile', kwargs={'username': username}))
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect(reverse('profile', kwargs={'username': username}))
