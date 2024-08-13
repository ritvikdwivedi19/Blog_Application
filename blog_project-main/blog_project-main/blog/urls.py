from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_list, name='blog_list'),
    path('search/', views.search, name='search'),
    path('blog/<int:pk>/', views.blog_detail, name='blog_detail'),
    path('search/', views.search, name='search'),
    path('tag/<str:tag_name>/', views.tag_view, name='tag_view'),
    path('blog/<int:pk>/', views.blog_detail, name='blog_detail'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/signup/', views.signup, name='signup'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('blogs/share/<int:blog_id>/', views.share_blog, name='share_blog'),   
]