from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db import models
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Post, Category, Comment, Like, UserProfile
from .forms import PostForm, EditProfileForm


# ===========================================
# EDIT PROFILE
# ===========================================
@login_required
def edit_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile', username=request.user.username)
    else:
        form = EditProfileForm(instance=user_profile)
    return render(request, 'edit_profile.html', {'form': form})
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Post, Category, Comment, Like, UserProfile
from .forms import PostForm  # you need a ModelForm for Post



# ===========================================
# HOME PAGE
# ===========================================
def home(request):
    categories = Category.objects.all()
    posts = Post.objects.filter(status=Post.STATUS_PUBLISHED)

    # Search filter
    query = request.GET.get('q', '')
    if query:
        posts = posts.filter(Q(title__icontains=query) | Q(content__icontains=query))

    # Category filter
    category_slug = request.GET.get('category', '')
    if category_slug:
        posts = posts.filter(category__name__iexact=category_slug)

    # Pagination (hardcoded 10 posts per page)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Annotate each post with whether the current user has liked it
    user = request.user
    posts_with_likes = []
    for post in page_obj:
        post.liked_by_user = False
        if user.is_authenticated:
            post.liked_by_user = post.likes.filter(user=user).exists()
        posts_with_likes.append(post)

    context = {
        'categories': categories,
        'posts': posts_with_likes,
        'query': query,
        'selected_category': category_slug,
    }
    return render(request, 'home.html', context)

# ===========================================
# POST DETAIL
# ===========================================
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk, status=Post.STATUS_PUBLISHED)
    comments = post.comments.filter(approved=True)
    liked = False
    if request.user.is_authenticated:
        liked = post.likes.filter(user=request.user).exists()

    # Handle new comment submission
    if request.method == 'POST' and 'comment_content' in request.POST:
        if request.user.is_authenticated:
            content = request.POST['comment_content']
            if content.strip():
                Comment.objects.create(post=post, author=request.user, content=content)
                messages.success(request, "Your comment was added!")
                return redirect('post_detail', pk=pk)
        else:
            messages.error(request, "You must be logged in to comment.")
            return redirect('login')

    context = {
        'post': post,
        'comments': comments,
        'liked': liked,
    }
    return render(request, 'post_detail.html', context)

# ===========================================
# LOGIN VIEW
# ===========================================
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')

# ===========================================
# REGISTER VIEW
# ===========================================
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        # Basic validation
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, "Registration successful! Welcome.")
            return redirect('home')

    return render(request, 'register.html')

# ===========================================
# PROFILE VIEW
# ===========================================
def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    published_posts = user.posts.filter(status=Post.STATUS_PUBLISHED)
    draft_posts = user.posts.filter(status=Post.STATUS_DRAFT) if request.user == user else None
    profile = getattr(user, 'profile', None)

    # Calculate total likes and comments
    total_likes = sum(post.likes.count() for post in published_posts)
    total_comments = sum(post.comments.count() for post in published_posts)

    context = {
        'profile_user': user,
        'profile': profile,
        'published_posts': published_posts,
        'draft_posts': draft_posts,
        'total_likes': total_likes,
        'total_comments': total_comments,
    }
    return render(request, 'profile.html', context)

# ===========================================
# LOGOUT
# ===========================================
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')

def toggle_like(request, post_id):
    if not request.user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'login_required'}, status=401)
        messages.error(request, "You must be logged in to like a post.")
        return redirect('login')

    post = get_object_or_404(Post, pk=post_id)
    existing_like = Like.objects.filter(post=post, user=request.user).first()

    if existing_like:
        existing_like.delete()
        liked = False
    else:
        Like.objects.create(post=post, user=request.user)
        liked = True

    # Return JSON for AJAX requests (no page reload)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'liked': liked, 'count': post.likes.count()})

    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            # Use the status selected by the user, default to draft if not present
            post.status = form.cleaned_data.get('status', Post.STATUS_DRAFT)
            post.save()
            messages.success(request, "Post created successfully!")
            return redirect('profile', username=request.user.username)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PostForm()

    return render(request, 'create_post.html', {'form': form})

@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.status = form.cleaned_data.get('status', Post.STATUS_DRAFT)
            post.save()
            messages.success(request, "Post updated successfully!")
            return redirect('profile', username=request.user.username)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PostForm(instance=post)

    return render(request, 'edit_post.html', {'form': form, 'post': post})

@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, "Post deleted successfully!")
        return redirect('profile', username=request.user.username)
    return render(request, 'delete_post.html', {'post': post})

@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user == comment.author or request.user == comment.post.author:
        post_pk = comment.post.pk
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
        return redirect('post_detail', pk=post_pk)
    else:
        messages.error(request, "You are not authorized to delete this comment.")
        return redirect('post_detail', pk=comment.post.pk)