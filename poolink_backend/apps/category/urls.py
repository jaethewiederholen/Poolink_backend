from django.urls import path
from poolink_backend.apps.category.api import views

app_name = "category"
urlpatterns = [
    path("", views.CategoryList.as_view(), name='categories'),
    path("/choice", views.CategorySelectView.as_view(), name='category-select'),
]
