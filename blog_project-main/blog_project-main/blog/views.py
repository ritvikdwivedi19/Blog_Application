from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Blog, Comment
from .forms import CommentForm
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector, TrigramSimilarity
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from .models import Blog
from .forms import EmailBlogForm

@csrf_exempt
def blog_list(request):
    blogs = Blog.objects.all()
    paginator = Paginator(blogs, 5)
    page = request.GET.get('page')
    blogs = paginator.get_page(page)
    return render(request, 'blog/blog_list.html', {'blogs': blogs})

@csrf_exempt
def blog_detail(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    comments = blog.comments.all()
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.blog = blog
            new_comment.author = request.user
            new_comment.save()
    else:
        comment_form = CommentForm()
    return render(request, 'blog/blog_detail.html', {'blog': blog, 'comments': comments, 'comment_form': comment_form})

@csrf_exempt
def search(request):
    query = request.GET.get('q')
    search_vector = SearchVector('title', weight='A') + SearchVector('content', weight='B')
    search_query = SearchQuery(query)
    full_text_results = Blog.objects.annotate(rank=SearchRank(search_vector, search_query)).filter(rank__gte=0.3).order_by('-rank')
    trigram_results = Blog.objects.annotate(similarity=TrigramSimilarity('title', query) + TrigramSimilarity('content', query)).filter(similarity__gte=0.3).order_by('-similarity')
    results = full_text_results.union(trigram_results).order_by('-rank', '-similarity')
    return render(request, 'blog/search_results.html', {'results': results})

@csrf_exempt
def tag_view(request, tag_name):
    blogs = Blog.objects.filter(tags__name=tag_name)
    return render(request, 'blog/tag.html', {'tag_name': tag_name, 'blogs': blogs})

@login_required
@csrf_exempt
def share_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    sent = False

    if request.method == 'POST':
        form = EmailBlogForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            blog_url = request.build_absolute_uri(reverse('blog_detail', args=[blog.id]))
            subject = f"{cd['name']} recommends you read {blog.title}"
            message = f"Read {blog.title} at {blog_url}\n\n{cd['name']}'s comments: {cd['comments']}"
            send_mail(subject, message, 'your-email@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailBlogForm()
    
    return render(request, 'blog/share_blog.html', {'blog': blog, 'form': form, 'sent': sent})

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # Load the profile instance created by the signal
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('blog_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
@csrf_exempt
def like_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)
    return redirect('blog_detail', pk=comment.blog.pk)

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('blog_list')
    else:
        form = AuthenticationForm()
    return render(request, 'blog/login.html', {'form': form})

@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    return render(request, 'blog/logout.html')