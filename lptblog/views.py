from django.shortcuts import get_object_or_404, render
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'lptblog/post/list.html'

# Create your views here.
def post_list(request):
    object_list = Post.published.all()
    paginator = Paginator(object_list,3) # Phân trang 3 bài 
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'lptblog/post/list.html',{'page':page,'posts':posts})

# To display a single post
def post_detail(request, year, month, day, post):
    post = get_object_or_404(
                Post, 
                slug=post, 
                status='published',
                publish__year = year, 
                publish__month = month, 
                publish__day = day)
    # Bình luận
    comments = post.comments.filter(active=True)
    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()
    return render(request, 'lptblog/post/detail.html',
                            {'post':post, 
                            'comments':comments, 
                            'new_comment': new_comment, 
                            'comment_form': comment_form})

def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status = 'published')
    sent = False
    if(request.method == 'POST'):
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
        #.... Gửi mail
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read" f"{post.title}"
            messages = f"Read {post.title} at {post_url} \n\n" f" {cd['name']}\'s comments: {cd['comments']}'"
            send_mail(subject, messages, 'lephatloc2016@gmail.com',[cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request,'lptblog/post/share.html',{'post':post,'form':form,'sent': sent} )