from django.urls import path

from poolink_backend.apps.hashtag.api import views

app_name = "hashtag"
urlpatterns = [
    path("", views.HashtagView.as_view(), name='hashtag'),
    path("prefer", views.PreferredTagView.as_view(), name='hashtag')
]
