from django import forms
from .models import Topic, Post


class NewTopicForm(forms.ModelForm):
    subject = forms.CharField(max_length=255, required=True)
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows': 5, 'placeholder': 'What is on your mind?'}
        ),
        max_length=4000,
        help_text='The max length of the text is 4000. MarkDown activated!', required=False
    )

    file = forms.FileField(required=False)

    class Meta:
        model = Topic
        fields = ['subject', 'message', 'file']


class PostForm(forms.ModelForm):
    file = forms.FileField(required=False)

    class Meta:
        model = Post
        fields = ['message', 'file']


class SearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=255, required=False)
