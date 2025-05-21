from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('upload/', views.upload_view, name='upload'),
    path('history/', views.history_view, name='history'),
    path('profile/', views.profile_view, name='profile'),
    path('recipe/<int:upload_id>/', views.recipe_detail, name='recipe_detail'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='home_page'), name='logout'),
    path('signup/', views.signup_view, name='signup'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

