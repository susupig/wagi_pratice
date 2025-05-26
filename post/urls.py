# post/urls.py

from django.urls import path
from . import views

app_name = 'post'


urlpatterns = [
    path('', views.home, name='home'),
    path('write/', views.write, name='write'),
    path('detail/<int:post_id>/', views.detail, name='detail'),
    path('update/<int:post_id>/', views.update, name='update'),
    path('like/<int:post_id>/', views.toggle_like, name='toggle_like'),

]
