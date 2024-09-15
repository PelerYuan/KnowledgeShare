from django.urls import path
from .api_views import FileUploadView

urlpatterns = [
    path('file-upload/', FileUploadView.as_view(), name='file-upload'),
]
