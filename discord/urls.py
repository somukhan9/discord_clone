from django.urls import path
from django.conf.urls.static import static
from django.conf.urls import url
from django.conf import settings
from django.views.static import serve
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('topics/', views.topics, name="topics"),
    path('room/<str:pk>/', views.room, name="room"),
    path('login/', views.login_user, name="login"),
    path('logout/', views.logout_user, name="logout"),
    path('signup/', views.signup_user, name="signup"),
    path('profile/<str:pk>/', views.profile, name="profile"),
    path('edit-profile/<str:pk>/', views.edit_profile, name="edit-profile"),
    path('create-room/', views.create_room, name="create-room"),
    path('update-room/<str:pk>/', views.update_room, name="update-room"),
    path('delete-room/<str:pk>/', views.delete_room, name="delete-room"),
    path('update-message/<str:pk>/', views.update_message, name="update-message"),
    path('delete-message/<str:pk>/', views.delete_message, name="delete-message"),


    url(r'^media/(?P<path>.*)$', serve,
        {'document_root': settings.MEDIA_ROOT}),

    url(r'^static/(?P<path>.*)$', serve,
        {'document_root': settings.STATIC_ROOT}),
]
