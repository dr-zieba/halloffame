"""vidz URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin, auth
from django.contrib.auth import views as auth_views
from django.urls import path, include
from halls import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("dashboard", views.dashboard, name="dashboard"),
    # AUTH
    path("signup/", views.SignUp.as_view(), name="signup"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    # Hall
    path("halloffame/create", views.CreateHall.as_view(), name="create-hall"),
    path("halloffame/<int:pk>", views.DetailHall.as_view(), name="detail-hall"),
    path("halloffame/<int:pk>/update", views.UpdateHall.as_view(), name="update-hall"),
    path("halloffame/<int:pk>/delete", views.DeleteHall.as_view(), name="delete-hall"),
    # Video
    path("halloffame/<int:pk>/add-video", views.add_video, name="add-video"),
    path("video/search", views.video_search, name="search-video"),
    path("video/<int:pk>/delete", views.DeleteVideo.as_view(), name='delete-video'),
]

# append static to urls
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
