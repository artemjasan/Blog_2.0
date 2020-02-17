from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import ListView


from .models import Post, Comment
from .forms import EmailPostForm, CommentForm


def post_list(request):
    object_list = Post.published.all()
    paginator = Paginator(object_list, 3) # Only 3 articles on the page.
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If the page does not int number, return the first page.
        posts = paginator.page(1)
    except EmptyPage:
        # If the page number more than quantity of pages, return the lats page. 
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'page':page,'posts': posts})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published',publish__year=year, publish__month=month, publish__day=day)
    # List of active comment for this post.
    comments = post.comments.filter(active=True)
    new_comment = None

    if request.method == 'POST':
        # User send comment.
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create comment, but we do not save it in the DB yet.
            new_comment = comment_form.save(commit=False)
            # Link comment to the article.
            new_comment.post = post
            # Save comment in the DB.
            new_comment.save()    
    else:
        comment_form = CommentForm()
    return render(request,'blog/post/detail.html', {'post': post, 'comments': comments, 'new_comment': new_comment, 'comment_form': comment_form})    


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_share(request, post_id):
    # Getting an article by ID
    post = get_object_or_404(Post, id=post_id,status='published')
    sent = False
    if request.method == 'POST':
        # Form send to save.
        form = EmailPostForm(request.POST)
        if form.is_valid():
        # All fields have been validated.
            cd = form.cleaned_data
        # Mail drop-off
        post_url = request.build_absolute_uri(post.get_absolute_url())
        subject = '{} ({}) recommends you reading "{}"'.format(cd['name'], cd['email'], post.title)
        message = 'Read "{}" at {}\n\n{}\'s comments:{}'.format(post.title, post_url, cd['name'], cd['comments'])
        send_mail(subject, message, 'admin@myblog.com', [cd['to']])
        sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent':sent})