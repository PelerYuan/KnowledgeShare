import urllib

from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import UpdateView, ListView, DeleteView
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.urls import reverse, reverse_lazy

from .forms import NewTopicForm, PostForm, SearchForm
from .models import Board, Post, Topic

from django.shortcuts import render
from django.views.generic import ListView
from django.db.models import Q


class BoardListView(ListView):
    model = Board
    context_object_name = 'boards'
    template_name = 'home.html'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('query', '')
        queryset = Board.objects.all().order_by('id')

        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('query', '')
        return context


class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'topics.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        kwargs['board'] = self.board
        kwargs['search_form'] = self.search_form
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        queryset = self.board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)

        self.search_form = SearchForm(self.request.GET)
        if self.search_form.is_valid():
            query = self.search_form.cleaned_data['query']
            queryset = queryset.filter(
                Q(subject__icontains=query) |
                Q(posts__message__icontains=query)
            ).distinct()

        return queryset


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'topic_posts.html'
    paginate_by = 7

    def get_context_data(self, **kwargs):
        session_key = 'viewed_topic_{}'.format(self.topic.pk)
        if not self.request.session.get(session_key, False):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True

        kwargs['topic'] = self.topic
        kwargs['query'] = self.request.GET.get('query', '')  # Pass query to the template
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        query = self.request.GET.get('query', '')
        queryset = self.topic.posts.order_by('created_at')

        if query:
            queryset = queryset.filter(
                Q(message__icontains=query)
            )

        return queryset


@login_required
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    if request.method == 'POST':
        form = NewTopicForm(request.POST, request.FILES)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = request.user
            topic.save()
            Post.objects.create(
                message=form.cleaned_data.get('message'),
                file=form.cleaned_data.get('file'),
                topic=topic,
                created_by=request.user
            )
            if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                return JsonResponse({'redirect_url': redirect('topic_posts', pk=pk, topic_pk=topic.pk).url})
            else:
                return redirect('topic_posts', pk=pk, topic_pk=topic.pk)
        else:
            if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                return JsonResponse({'errors': form.errors}, status=400)
            else:
                return render(request, 'new_topic.html', {'board': board, 'form': form})
    else:
        form = NewTopicForm()
    return render(request, 'new_topic.html', {'board': board, 'form': form})


from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required


@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()

            topic.last_updated = timezone.now()
            topic.save()

            topic_url = reverse('topic_posts', kwargs={'pk': pk, 'topic_pk': topic_pk})
            topic_post_url = '{url}?page={page}#{id}'.format(
                url=topic_url,
                id=post.pk,
                page=topic.get_page_count()
            )

            # 检查是否通过 AJAX 发送的请求
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'redirect_url': topic_post_url})
            else:
                return redirect(topic_post_url)
    else:
        form = PostForm()

    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message', 'file')
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()

        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'redirect_url': self.get_success_url()})
        else:
            return super().form_valid(form)

    def get_success_url(self):
        return reverse('topic_posts', kwargs={'pk': self.object.topic.board.pk, 'topic_pk': self.object.topic.pk})


@method_decorator(login_required, name='dispatch')
class PostDeleteView(DeleteView):
    model = Post
    template_name = 'delete_post_confirm.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def get_success_url(self):
        post = self.object
        topic = post.topic
        if topic.posts.exclude(id=post.id).exists():  # Check if there are other posts in the topic
            return reverse_lazy('topic_posts', kwargs={'pk': topic.board.pk, 'topic_pk': topic.pk})
        else:
            topic.delete()  # Delete the topic if no posts are left
            return reverse_lazy('board_topics', kwargs={'pk': topic.board.pk})

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        response = super().delete(request, *args, **kwargs)
        topic = self.object.topic
        if topic.posts.count() == 0:
            topic.delete()
        return response


class PostDownloadView(View):
    def get(self, request, pk, topic_pk, post_pk):
        try:
            post = get_object_or_404(Post, pk=post_pk, topic__pk=topic_pk, topic__board__pk=pk)
            if post.file:
                file_name = post.get_file_name()
                file_name = urllib.parse.quote(file_name)
                response = FileResponse(post.file.open(), as_attachment=True)
                response['Content-Disposition'] = f'attachment; filename="{file_name}"'
                return response
            else:
                raise Http404("No file attached to this post.")
        except Post.DoesNotExist:
            raise Http404("Post does not exist.")
