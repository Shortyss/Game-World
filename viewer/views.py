import json
from turtle import forward

from django_addanother.views import CreatePopupMixin
from django_addanother.widgets import AddAnotherWidgetWrapper

from .models import *

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.forms import ModelForm, ClearableFileInput, CharField, CheckboxSelectMultiple, Textarea, SelectMultiple, \
    Select
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from dal import autocomplete

import random


def index(request):
    nine_months_ago = timezone.now().date() - timezone.timedelta(days=9 * 30)
    active_discounts = Discount.objects.filter(
        start_date__lte=timezone.now().date(),
        end_date__gte=timezone.now().date()
    )
    new_releases = Game.objects.filter(release_date__lte=timezone.now().date(),
                                       release_date__gte=nine_months_ago).order_by('-release_date')[:6]
    pre_orders = Game.objects.filter(release_date__gt=timezone.now().date()).order_by('release_date')[:6]
    bestsellers = Game.objects.annotate(total_sold=Sum('platform_versions__purchaseitem__quantity')).order_by('-total_sold')[:6]
    sales = Game.objects.filter(platform_versions__discounts__in=active_discounts).distinct()[:6]
    if request.user.is_authenticated:
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        games = list(wishlist.games.all())
        random_games = random.sample(games, min(len(games), 5))
    else:
        random_games = []

    context = {
        'new_releases': new_releases,
        'pre_orders': pre_orders,
        'wishlist': random_games,
        'bestsellers': bestsellers,
        'sales': sales
    }

    return render(request, 'index.html', context)


def sales_view(request):
    active_discounts = Discount.objects.filter(
        start_date__lte=timezone.now().date(),
        end_date__gte=timezone.now().date()
    )
    sales = Game.objects.filter(discounts__in=active_discounts).distinct()

    return render(request, 'sales.html', {'sales': sales})


class DiscountForm(ModelForm):
    class Meta:
        model = Discount
        fields = '__all__'


@login_required
def add_discount(request):
    if request.method == 'POST':
        form = DiscountForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('discount_list')
    else:
        form = DiscountForm()

    return render(request, 'discount_add.html', {'form': form})


class DiscountUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'discount_add.html'
    model = Discount
    form_class = DiscountForm
    success_url = reverse_lazy('discount_list')
    permission_required = 'administrator'


def discount_list(request):
    discounts = Discount.objects.all()
    return render(request, 'discount_list.html', {'discounts':discounts})


def administration(request):
    return render(request, 'administration.html',)


def wishlist(request):
    if request.user.is_authenticated:
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        games = wishlist.games.all()
    else:
        games = []

    return render(request, 'wishlist.html', {'wishlist': games})


def toggle_wishlist(request, game_id):
    if request.user.is_authenticated:
        game = Game.objects.get(id=game_id)
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)

        if game in wishlist.games.all():
            wishlist.games.remove(game)
        else:
            wishlist.games.add(game)

        return redirect('game_detail', pk=game_id)
    return redirect('login')


class NewReleasesView(ListView):
    model = Game
    template_name = 'new_releases.html'
    context_object_name = 'new_releases'

    def get_queryset(self):
        nine_months_ago = timezone.now().date() - timezone.timedelta(days=9*30)
        return Game.objects.filter(release_date__lte=timezone.now().date(),
                                   release_date__gte=nine_months_ago).order_by('-release_date')


class PreOrdersView(ListView):
    model = Game
    template_name = 'pre_orders.html'
    context_object_name = 'pre_orders'

    def get_queryset(self):
        return Game.objects.filter(release_date__gt=timezone.now()).order_by('release_date')


class CustomClearableFileInput(ClearableFileInput):
    allow_multiple_selected = True


class GenreAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Genre.objects.all()
        print(f"žánry: {qs}")
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs


class GameModelForm(ModelForm):
    images = MultiFileField(min_num=1, max_num=10, max_file_size=1920 * 1080 * 10, required=False)
    video_urls = CharField(widget=Textarea, required=False,
                                 help_text="Vlož odkazy na videa oddělené čárkou")

    class Meta:
        model = Game
        fields = '__all__'
        widgets = {
            'genres': AddAnotherWidgetWrapper(
                SelectMultiple,
                reverse_lazy('genres_create')
            ),
            'game_mode': AddAnotherWidgetWrapper(
                SelectMultiple,
                reverse_lazy('game_mode_create')
            ),
            'developer': AddAnotherWidgetWrapper(
                SelectMultiple,
                reverse_lazy('developer_create')
            ),
            'publisher': AddAnotherWidgetWrapper(
                SelectMultiple,
                reverse_lazy('publisher_create')
            ),
            'min_configuration_os': AddAnotherWidgetWrapper(
                SelectMultiple,
                reverse_lazy('os_create')
            ),
            'min_configuration_cpu': AddAnotherWidgetWrapper(
                SelectMultiple,
                reverse_lazy('cpu_create')
            ),
        }

    def clean_name(self):
        cleaned_data = super().clean()
        name = cleaned_data['name'].strip().capitalize()
        return name

    def clean(self):
        return super().clean()

    def save(self, commit=True):
        instance = super().save(commit=False)
        images = self.cleaned_data.get('images')
        video_urls = self.cleaned_data.get('video_urls', "").split(',')

        if commit:
            instance.save()
            self.save_m2m()

        if images:
            for image in images:
                GameImage.objects.create(game=instance, image=image)

        for url in video_urls:
            if url.strip():
                GameVideo.objects.create(game=instance, video_url=url.strip())

        return instance


def bestsellers_view(request):
    bestsellers = Game.objects.annotate(total_sold=Sum('purchaseitem__quantity')).order_by('-total_sold')
    return render(request, 'bestsellers.html', {'bestsellers': bestsellers})


class GenericCreateView(LoginRequiredMixin, CreateView, CreatePopupMixin):
    template_name = 'generic_create.html'
    form_class = None
    success_url = reverse_lazy('administration')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = self.model.objects.all()
        context['update_url_name'] = f'{self.model._meta.model_name}_update'
        context['delete_url_name'] = f'{self.model._meta.model_name}_delete'
        return context

    def form_valid(self, form):
        self.object = form.save()

        return HttpResponse(
            '<script>'
            'opener.dismissAddAnotherPopup(window, "%s", "%s");'
            'opener.refreshGenres();'
            '</script>' % (self.object.pk, self.object)
        )


class GenericUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'generic_create.html'
    form_class = None
    success_url = reverse_lazy('administration')


class GenericDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy(f'{self.model._meta.model_name}_create')


class GameCreateView(LoginRequiredMixin, CreateView):
    template_name = 'game_create.html'
    model = Game
    form_class = GameModelForm
    success_url = reverse_lazy('game_create')
    permission_required = 'administration'


class GameUpdateVIew(LoginRequiredMixin, UpdateView):
    template_name = 'game_create.html'
    model = Game
    form_class = GameModelForm
    success_url = reverse_lazy('games')
    permission_required = 'administration'

    def form_valid(self, form):
        response = super().form_valid(form)
        delete_images = self.request.POST.getlist('delete_images')
        if delete_images:
            for image_id in delete_images:
                try:
                    image = GameImage.objects.get(id=image_id)
                    image.delete()
                except GameImage.DoesNotExist:
                    pass
        return response


class GamesView(View):
    def get(self, request):
        game_list = Game.objects.all()
        context = {'games': game_list}
        return render(request, 'games.html', context)


class GamesByPlatformView(View):
    platform = None

    def get(self, request, *args, **kwargs):
        game_list = Game.objects.filter(platform__type_platform=self.platform)
        context = {'games': game_list, 'platform': self.platform}
        return render(request, f'games_{self.platform.lower()}.html', context)


def game(request, pk):
    game_platform = GamePlatform.objects.get(id=pk)
    related_games = Game.objects.filter(genres__in=game_platform.genres.all()).exclude(id=pk)
    wishlist = Wishlist.objects.filter(user=request.user).first() if request.user.is_authenticated else None
    active_discounts = Discount.objects.filter(
        start_date__lte=timezone.now().date(),
        end_date__gte=timezone.now().date()
    )
    sales = GamePlatform.objects.filter(discounts__in=active_discounts).distinct()
    context = {
        'game_platform': game_platform,
        'related_games': related_games,
        'wishlist': wishlist,
        'sales': sales,
    }
    return render(request, 'game_detail.html', context)


class GenreModelForm(ModelForm):
    class Meta:
        model = Genre
        fields = '__all__'


class GenresCreate(LoginRequiredMixin, CreateView, CreatePopupMixin):
    template_name = 'genres_create.html'
    model = Genre
    form_class = GenreModelForm
    success_url = reverse_lazy('genres_create')
    permission_required = 'administration'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Genre.objects.all()
        return context

    def form_valid(self, form):
        self.object = form.save()

        return HttpResponse(
            '<script>'
            'opener.dismissAddAnotherPopup(window, "%s", "%s");'
            'opener.refreshGenres();'
            '</script>' % (self.object.pk, self.object)
        )


class GenreUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'genres_create.html'
    model = Genre
    form_class = GenreModelForm
    success_url = reverse_lazy('genres_create')
    permission_required = 'administration'


class GameModeModelForm(ModelForm):
    class Meta:
        model = GameMode
        fields = '__all__'


class GameModeCreate(LoginRequiredMixin, CreateView, CreatePopupMixin):
    template_name = 'game_mode_create.html'
    model = GameMode
    form_class = GameModeModelForm
    success_url = reverse_lazy('game_mode_create')
    permission_required = 'administration'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game_modes'] = GameMode.objects.all()
        return context

    def form_valid(self, form):
        self.object = form.save()

        return HttpResponse(
            '<script>'
            'opener.dismissAddAnotherPopup(window, "%s", "%s");'
            'opener.refreshGameModes();'
            '</script>' % (self.object.pk, self.object)
        )


class GameModeUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'game_mode_create.html'
    model = GameMode
    success_url = reverse_lazy('game_mode_create')
    permission_required = 'administration'


class DeveloperModelForm(ModelForm):
    class Meta:
        model = Developer
        fields = '__all__'


class DeveloperCreate(LoginRequiredMixin, CreateView, CreatePopupMixin):
    template_name = 'developer_create.html'
    model = Developer
    form_class = DeveloperModelForm
    success_url = reverse_lazy('developer_create')
    permission_required = 'administration'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['developers'] = Developer.objects.all()
        return context

    def form_valid(self, form):
        self.object = form.save()

        return HttpResponse(
            '<script>'
            'opener.dismissAddAnotherPopup(window, "%s", "%s");'
            'opener.refreshDeveloper();'
            '</script>' % (self.object.pk, self.object)
        )


class DeveloperUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'developer_create.html'
    model = Developer
    form_class = DeveloperModelForm
    success_url = reverse_lazy('developer_create')
    permission_required = 'administration'


class PublisherModelForm(ModelForm):
    class Meta:
        model = Publisher
        fields = '__all__'


class PublisherCreate(LoginRequiredMixin, CreateView, CreatePopupMixin):
    template_name = 'publisher_create.html'
    model = Publisher
    form_class = PublisherModelForm
    success_url = reverse_lazy('publisher_create')
    permission_required = 'administration'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['publishers'] = Publisher.objects.all()
        return context

    def form_valid(self, form):
        self.object = form.save()

        return HttpResponse(
            '<script>'
            'opener.dismissAddAnotherPopup(window, "%s", "%s");'
            'opener.refreshPublisher();'
            '</script>' % (self.object.pk, self.object)
        )


class PublisherUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'publisher_create.html'
    model = Publisher
    form_class = PublisherModelForm
    success_url = reverse_lazy('publisher_create')
    permission_required = 'administration'


class OsModelForm(ModelForm):
    class Meta:
        model = OS
        fields = '__all__'


class CPUModelForm(ModelForm):
    class Meta:
        model = CPU
        fields = '__all__'


class GamesFilteredByGenreView(View):
    def get(self, request, genre_name):
        games = Game.objects.filter(genres__name__iexact=genre_name)
        context = {'games': games, 'filter_type': 'Žánr', 'filter_value': genre_name}
        return render(request, 'games_filtered.html', context)


class GamesFilteredByPlatformView(View):
    def get(self, request, platform_name):
        games = Game.objects.filter(platform__type_platform_iexact=platform_name)
        context = {'games': games, 'filter_type': 'Platforma', 'filter_value': platform_name}
        return render(request, 'games_filtered.html', context)


class GamesFilteredByModeView(View):
    def get(self, request, mode_name):
        games = Game.objects.filter(game_mode__name__iexact=mode_name)
        context = {'games': games, 'filter_type': 'Herní mód', 'filter_value': mode_name}
        return render(request, 'games_filtered.html', context)


class GamesFilteredByDeveloperView(View):
    def get(self, request, developer_name):
        games = Game.objects.filter(developer__name__iexact=developer_name)
        context = {'games': games, 'filter_type': 'Vývojář', 'filter_value': developer_name}
        return render(request, 'games_filtered.html', context)


class GamesFilteredByPublisherView(View):
    def get(self, request, publisher_name):
        games = Game.objects.filter(publisher__name__iexact=publisher_name)
        context = {'games': games, 'filter_type': 'Vydavatel', 'filter_value': publisher_name}
        return render(request, 'games_filtered.html', context)


@login_required
def cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    total_price = sum(item.get_total_price() for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})


@login_required
@require_POST
def update_cart_item(request, item_id):
    try:
        data = json.loads(request.body)
        new_quantity = int(data.get('quantity'))
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)

        if new_quantity > 0:
            cart_item.quantity = new_quantity
            cart_item.save()
        else:
            cart_item.delete()

        cart = cart_item.cart
        total_price = sum(item.get_total_price() for item in CartItem.objects.filter(cart=cart))

        return JsonResponse({
            'success': True,
            'new_price': cart_item.get_total_price() if new_quantity > 0 else 0,
            'new_total_price': total_price
        })
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item not found in cart.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def add_to_cart(request, pk):
    game_platform = get_object_or_404(GamePlatform, id=pk)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart.add_game(game_platform)
    return redirect('cart')


@login_required
def remove_from_cart(request, pk):
    game_platform = get_object_or_404(GamePlatform, id=pk)
    cart = get_object_or_404(Cart, user=request.user)
    cart.remove_game(game_platform)
    return redirect('cart')


@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    if not cart_items:
        return redirect('cart')

    purchase = Purchase.objects.create(user=request.user)
    for item in cart_items:
        purchase_item = PurchaseItem.objects.create(
            purchase=purchase,
            game_platform=item.game_platform,
            quantity=item.quantity)
        if item in cart_items.is_paid:
            purchase_item.is_paid = True
            purchase_item.save()
        purchase.calculate_total()
        cart.clear_cart()

