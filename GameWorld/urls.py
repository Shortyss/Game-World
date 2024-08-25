"""
URL configuration for GameWorld project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from tkinter.font import names

from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.views import LoginView
from django.urls import path, include

from accounts.views import *
from viewer.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('administration', administration, name='administration'),

    path('accounts/login/', LoginView.as_view(), name='login'),
    path('accounts/logout/', logout_view, name='logout'),
    path('accounts/signup/', SignUpView.as_view(), name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),

    path('accounts/profile_create/<pk>', ProfileCreateView.as_view(), name='profile_create'),
    path('accounts/profile/<pk>/', profile, name='profile'),
    path('accounts/profile_edit/', profile_edit, name='profile_edit'),

    path('wishlist/', wishlist, name='wishlist'),

    path('game/create/', GameCreateView.as_view(), name='game_create'),
    path('game/update/<pk>/', GameUpdateVIew.as_view(), name='game_update'),
    path('game/confirm_delete/<pk>/', GameDeleteView.as_view(), name='game_confirm_delete'),
    path('wishlist/toggle/<int:game_id>/', toggle_wishlist, name='toggle_wishlist'),

    path('games/', GamesView.as_view(), name='games'),
    path('game/<pk>/', game, name='game_detail'),
    path('games/PC/', GamesByPlatformView.as_view(platform='PC'), name='games_pc'),
    path('games/PS/', GamesByPlatformView.as_view(platform='PS'), name='games_ps'),
    path('games/XBOX/', GamesByPlatformView.as_view(platform='XBOX'), name='games_xbox'),

    path('games/genre/<str:genre_name>/', GamesFilteredByGenreView.as_view(), name='games_by_genre'),
    path('games/<str:platform_name>/', GamesFilteredByPlatformView.as_view(), name='games_by_platform'),
    path('games/mode/<str:mode_name>/', GamesFilteredByModeView.as_view(), name='games_by_mode'),
    path('games/developer/<str:developer_name>/', GamesFilteredByDeveloperView.as_view(), name='games_by_developer'),
    path('games/publisher/<str:publisher_name>/', GamesFilteredByPublisherView.as_view(), name='games_by_publisher'),

    path('new_releases/', NewReleasesView.as_view(), name='new_releases'),
    path('pre_orders/', PreOrdersView.as_view(), name='pre_orders'),
    path('bestsellers/', bestsellers_view, name='bestsellers'),
    path('sales/', sales_view, name='sales'),

    path('discounts/', discount_list, name='discount_list'),
    path('discount/add/', add_discount, name='discount_add'),
    path('discounts/edit/<int:pk>/', DiscountUpdateView.as_view(), name='discount_edit'),
    path('discounts/delete/<int:pk>/', DiscountDeleteView.as_view(), name='discount_delete'),

    path('cart/', cart, name='cart'),
    path('cart/add/<pk>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<pk>/', remove_from_cart, name='remove_from_cart'),
    path('checkout/', checkout, name='checkout'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
