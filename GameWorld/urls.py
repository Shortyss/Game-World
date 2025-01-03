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

    path('game/create/', GenericCreateView.as_view(model=Game, form_class=GameModelForm), name='game_create'),
    path('game/update/<pk>/', GenericUpdateView.as_view(model=Game, form_class=GameModelForm), name='game_update'),
    path('game/confirm_delete/<pk>/', GenericDeleteView.as_view(model=Game), name='game_confirm_delete'),
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
    path('discounts/delete/<int:pk>/', GenericDeleteView.as_view(model=Discount), name='discount_delete'),

    path('cart/', cart, name='cart'),
    path('cart/add/<pk>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<pk>/', remove_from_cart, name='remove_from_cart'),
    path('checkout/', checkout, name='checkout'),
    path('update-cart-item/<int:item_id>/', update_cart_item, name='update_cart_item'),

    path('genres/create/', GenresCreate.as_view(), name='genres_create'),
    path('genre/update/<pk>/', GenreUpdate.as_view(), name='genre_update'),
    path('genre/delete/<pk>/', GenericDeleteView.as_view(model=Genre), name='genre_delete'),

    path('genre-autocomplete/', GenreAutocomplete.as_view(), name='genre-autocomplete'),

    path('game-mode/create/', GameModeCreate.as_view(), name='game_mode_create'),
    path('game-mode/update/<pk>/', GameModeUpdate.as_view(), name='game_mode_update'),
    path('game-mode/delete/<pk>/', GenericDeleteView.as_view(model=GameMode), name='game_mode_delete'),

    path('developer/create/', DeveloperCreate.as_view(), name='developer_create'),
    path('developer/update/<pk>/', DeveloperUpdate.as_view(), name='developer_update'),
    path('developer/delete/<pk>/', GenericDeleteView.as_view(model=Developer), name='developer_delete'),

    path('publisher/create/', PublisherCreate.as_view(), name='publisher_create'),
    path('publisher/update/<pk>/', PublisherUpdate.as_view(), name='publisher_update'),
    path('publisher/delete/<pk>/', GenericDeleteView.as_view(model=Publisher), name='publisher_delete'),

    path('os/create/', GenericCreateView.as_view(model=OS, form_class=OsModelForm), name='os_create'),
    path('os/update/<pk>/', GenericUpdateView.as_view(model=OS, form_class=OsModelForm), name='os_update'),
    path('os/delete/<pk>/', GenericDeleteView.as_view(model=OS), name='os_delete'),

    path('cpu/create/', GenericCreateView.as_view(model=CPU, form_class=CPUModelForm), name='cpu_create'),
    path('cpu/update/<pk>/', GenericUpdateView.as_view(model=CPU, form_class=CPUModelForm), name='cpu_update'),
    path('cpu/delete/<pk>/', GenericDeleteView.as_view(model=CPU), name='cpu_delete'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
