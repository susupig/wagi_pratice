# post/urls.py

from django.urls import path
from . import views



urlpatterns = [
    path('', views.home, name='home'),
    path('write/', views.write, name='write'),
    path('detail/<int:post_id>/', views.detail, name='detail'),
    path('update/<int:post_id>/', views.update, name='update'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('like/<int:post_id>/', views.toggle_like, name='toggle_like'),

]
