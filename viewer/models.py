from django.utils import timezone

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Model, CharField, ManyToManyField, ForeignKey, CASCADE, DateField, DecimalField, TextField, \
    DO_NOTHING, SET_NULL, IntegerField, DateTimeField, PositiveIntegerField, ImageField, BooleanField, URLField
from multiupload.fields import MultiFileField


# Create your models here.


class Platform(Model):
    PLATFORM_CHOICES = [
        ('PC', 'PC'),
        ('PS', 'Playstation'),
        ('XBOX', 'Xbox')
    ]

    type_platform = CharField(max_length=10, choices=PLATFORM_CHOICES, verbose_name='Platforma')

    def __str__(self):
        return self.get_type_platform_display()


class Genre(Model):
    name = CharField(max_length=36, null=False, blank=False, unique=True, verbose_name='Název')

    def __str__(self):
        return f"{self.name}"


class GameMode(Model):
    name = CharField(max_length=36, null=False, blank=False, unique=True, verbose_name='Název')

    def __str__(self):
        return f"{self.name}"


class Developer(Model):
    name = CharField(max_length=90, null=False, blank=False, verbose_name='Název')
    description = TextField(null=True, blank=True, verbose_name='Popis')
    founded = DateField(null=True, blank=True, verbose_name='Datum založení')

    def __str__(self):
        return f"{self.name}"


class Publisher(Model):
    name = CharField(max_length=90, null=False, blank=False, verbose_name='Název')
    description = TextField(null=True, blank=True, verbose_name='Popis')
    founded = DateField(null=True, blank=True, verbose_name='Datum založení')

    def __str__(self):
        return f"{self.name}"


class OS(Model):
    name = CharField(max_length=100, null=True, blank=True, verbose_name='Operační systém')

    def __str__(self):
        return f"{self.name}"


class CPU(Model):
    name = CharField(max_length=100, null=True, blank=True, verbose_name='CPU')

    def __str__(self):
        return f"{self.name}"


class RAM(Model):
    name = CharField(max_length=100, null=True, blank=True, verbose_name='RAM')

    def __str__(self):
        return f"{self.name}"


class GPU(Model):
    name = CharField(max_length=100, null=True, blank=True, verbose_name='GPU')

    def __str__(self):
        return f"{self.name}"


class HDD(Model):
    name = CharField(max_length=164, null=True, blank=True, verbose_name='HDD')

    def __str__(self):
        return f"{self.name}"


class AdditionalNotes(Model):
    note = TextField(null=True, blank=True, verbose_name='Dodatečné poznámky')

    def __str__(self):
        return f"{self.note}"


class InsufficientQuantityException(Exception):
    def __init__(self, message="Nedostatek zboží skladem"):
        self.message = message
        super().__init__(self.message)


class InvalidPurchaseAmountException(Exception):
    def __init__(self, message="Špatně zadané množství"):
        self.message = message
        super().__init__(self.message)


class Game(Model):
    name = CharField(max_length=300, null=False, blank=False, verbose_name='Název')
    platform = ManyToManyField(Platform, blank=True, related_name='games_by_developer',
                               verbose_name='Platforma')
    genres = ManyToManyField(Genre, blank=True, related_name='games_by_genre',
                             verbose_name='Žánr')
    game_mode = ManyToManyField(GameMode, blank=True, related_name='games_by_mode',
                                verbose_name='Herní mód')
    release_date = DateField(null=True, blank=True, verbose_name='Datum vydání')
    developer = ManyToManyField(Developer, blank=True, related_name='games_by_developer',
                                verbose_name='Vývojář')
    publisher = ManyToManyField(Publisher, blank=True, related_name='games_by_publisher',
                                verbose_name='Vydavatel')
    min_configuration_os = ForeignKey(OS, on_delete=SET_NULL, null=True, blank=True, related_name='min_os',
                                      verbose_name='Minimální operační systém')
    min_configuration_cpu = ManyToManyField(CPU, blank=True, related_name='min_cpus',
                                       verbose_name='CPU (Minimální')
    min_configuration_ram = ForeignKey(RAM, on_delete=SET_NULL, null=True, blank=True, related_name='min_ram',
                                       verbose_name='RAM (Minimální)')
    min_configuration_gpu = ManyToManyField(GPU, blank=True, related_name='min_gpus',
                                       verbose_name='GPU (Minimální')
    min_configuration_hdd = ForeignKey(HDD, on_delete=SET_NULL, null=True, blank=True, related_name='min_hdd',
                                       verbose_name='HDD (Minimální)')
    min_additional_notes = ForeignKey(AdditionalNotes, on_delete=SET_NULL, null=True, blank=True,
                                      related_name='min_game_notes', verbose_name='Dodatečné poznámky')
    recommended_configuration_os = ForeignKey(OS, on_delete=SET_NULL, null=True, blank=True,
                                              related_name='recommended_os', verbose_name='Doporučený operační systém')
    recommended_configuration_cpu = ManyToManyField(CPU, blank=True,
                                               related_name='recommended_cpus', verbose_name='CPU (Dporučené)')
    recommended_configuration_ram = ForeignKey(RAM, on_delete=SET_NULL, null=True, blank=True,
                                               related_name='recommended_ram', verbose_name='RAM (Doporučené)')
    recommended_configuration_gpu = ManyToManyField(GPU, blank=True,
                                               related_name='recommended_gpus', verbose_name='GPU (Dporučené)')
    recommended_configuration_hdd = ForeignKey(HDD, on_delete=SET_NULL, null=True, blank=True,
                                               related_name='recommended_hdd', verbose_name='HDD (Doporučené)')
    recommended_configuration_additional_notes = ForeignKey(AdditionalNotes, on_delete=SET_NULL, null=True, blank=True,
                                                            related_name='recommended_game_notes',
                                                            verbose_name='Dodatečné poznámky')
    description = TextField(null=True, blank=True, verbose_name='Popis')

    def get_images(self):
        return GameImage.objects.filter(game=self)

    def __str__(self):
        return f"{self.name} - {self.platform}"


class GameImage(Model):
    game = ForeignKey(Game, related_name='images', on_delete=CASCADE)
    image = ImageField(upload_to='viewer/static/game_images/')

    def save(self, *args, **kwargs):
        self.image.name = self.image.name.lower().replace(" ", "")
        super().save(*args, **kwargs)


class GameVideo(Model):
    game = ForeignKey(Game, related_name='videos', on_delete=models.CASCADE)
    video_url = URLField(verbose_name='YouTube URL')
    title = CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.game.name} Video - {self.title or 'Untitled'}"


class Wishlist(Model):
    user = ForeignKey(User, on_delete=CASCADE, related_name='wishlist')
    games = ManyToManyField('Game', related_name='wishlists')

    def __str__(self):
        return f"{self.user.username} Wishlist"


class Rating(Model):
    game = ForeignKey(Game, on_delete=DO_NOTHING, null=False, blank=False)
    user = ForeignKey(User, null=True, on_delete=SET_NULL)
    rating = IntegerField(null=False, blank=False,  verbose_name='Hodnocení')

    def __str__(self):
        return f"{self.game}: {self.rating} od {self.user}"


class Comment(Model):
    game = ForeignKey(Game, on_delete=DO_NOTHING, null=False, blank=False)
    user = ForeignKey(User, null=True, on_delete=SET_NULL)
    comment = TextField(null=False, blank=False, verbose_name='Komentář')
    created = DateTimeField(auto_now_add=True, verbose_name='Vytvořeno')
    updated = DateTimeField(auto_now=True, verbose_name='Změněno')

    def __str__(self):
        return f"{self.game} ({self.user}): {self.comment[:50]}"


class DLC(Model):
    name = CharField(max_length=300, null=False, blank=False, verbose_name='Název')
    game = ForeignKey(Game, on_delete=CASCADE, related_name='dlcs')
    release_date = DateField(null=True, blank=True, verbose_name='Datum vydání')
    price = DecimalField(max_digits=10, decimal_places=2, null=False, blank=False, default=0, verbose_name='Cena')
    description = TextField(null=True, blank=True, verbose_name='Popis')

    def __str__(self):
        return f"{self.name}"


class Cart(Model):
    user = ForeignKey(User, on_delete=models.CASCADE, related_name='user_cart_items')
    created_at = DateTimeField(auto_now_add=True)

    def add_game_platform(self, game_platform, quantity=1):
        cart_item, created = CartItem.objects.get_or_create(cart=self, game_platform=game_platform)
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        else:
            cart_item.quantity = quantity
            cart_item.save()

        game_platform.decrease_quantity(quantity)

    def remove_game_platform(self, game_platform, quantity=1):
        cart_item = CartItem.objects.filter(cart=self, game_platform=game_platform).first()
        if cart_item:
            if cart_item.quantity <= quantity:
                game_platform.increase_quantity(cart_item.quantity)
                cart_item.delete()
            else:
                cart_item.quantity -= quantity
                cart_item.save()
                game_platform.increase_quantity(quantity)

    def clear_cart(self):
        for item in self.cart_items.all():
            item.game_platform.increase_quantity(item.quantity)
        self.cart_items.all().delete()

    def __str__(self):
        return f'{self.user.username} - {self.game.name} - {self.quantity}'


class Purchase(Model):
    user = ForeignKey(User, on_delete=CASCADE, related_name='user_purchases', verbose_name='Zákazník')
    purchase_date = DateTimeField(auto_now_add=True, verbose_name='Datum nákupu')
    total_price = DecimalField(max_digits=10, decimal_places=2, default=0.0)
    payment_id = CharField(max_length=100, blank=True, null=True)
    is_paid = BooleanField(default=False)

    def calculate_total(self):
        total = sum(item.get_total_price() for item in self.purchase_items.all())
        self.total_price = total
        self.save()

    def remove_purchased_items(self):
        removed = False
        if not self.is_paid:
            for item in self.purchase_items.all():
                if PurchaseItem.objects.filter(purchase__user=self.user, is_paid=True).exists():
                    item.delete()
                    removed = True
            self.calculate_total()
        return removed

    def __str__(self):
        return f'{self.user.username} - {self.game.name} - {self.quantity}'


class GamePlatform(Model):
    game = ForeignKey(Game, on_delete=CASCADE, related_name='platform_versions')
    platform = ForeignKey(Platform, on_delete=CASCADE, related_name='game_versions')
    price = DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Cena')
    quantity = PositiveIntegerField(default=0, verbose_name='Množství na skladu')

    def __str__(self):
        return f"{self.game.name} - {self.platform}"

    def get_price(self):
        active_discount = self.discounts.filter(
            start_date__lte=timezone.now().date(),
            end_date__gte=timezone.now().date()
        ).first()

        if active_discount:
            return active_discount.discount_price
        return self.price

    def decrease_quantity(self, amount):
        if amount > self.quantity:
            raise InsufficientQuantityException("Nedostatek zboží skladem.")
        self.quantity -= amount
        self.save()

    def increase_quantity(self, amount):
        if amount <= 0:
            raise InvalidPurchaseAmountException("Naskladněné množství musí být větší než 0.")
        self.quantity += amount
        self.save()


class DLCPlatform(Model):
    dlc = ForeignKey('DLC', on_delete=CASCADE, related_name='platform_versions')
    platform = ForeignKey(Platform, on_delete=CASCADE, related_name='dlc_versions')
    price = DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Cena')
    quantity = PositiveIntegerField(default=0, verbose_name='Množství na skladu')

    def __str__(self):
        return f"{self.dlc.name} - {self.platform}"

    def get_price(self):
        active_discount = self.discounts.filter(
            start_date__lte=timezone.now().date(),
            end_date__gte=timezone.now().date()
        ).first()

        if active_discount:
            return active_discount.discount_price
        return self.price

    def purchase(self, amount):
        if amount > self.quantity:
            raise InsufficientQuantityException("Nedostatek zboží skladem.")
        self.quantity -= amount
        self.save()

    def restock(self, amount):
        if amount <= 0:
            raise InvalidPurchaseAmountException("Množství musí být větší než 0.")
        self.quantity += amount
        self.save()


class Discount(models.Model):
    game_platform = models.ForeignKey(GamePlatform, on_delete=models.CASCADE, related_name='discounts', null=True, blank=True)
    dlc_platform = models.ForeignKey(DLCPlatform, on_delete=models.CASCADE, related_name='discounts', null=True, blank=True)
    discount_price = DecimalField(max_digits=10, decimal_places=2)
    start_date = DateField()
    end_date = DateField(null=True, blank=True)

    def is_active(self):
        now = timezone.now().date()
        return self.start_date <= now and (not self.end_date or self.end_date >= now)

    def get_discount_percent(self):
        if self.game_platform:
            return round((self.game_platform.price - self.discount_price) / self.game_platform.price * 100, 2)
        elif self.dlc_platform:
            return round((self.dlc_platform.price - self.discount_price) / self.dlc_platform.price * 100, 2)
        return 0

    def __str__(self):
        if self.game_platform:
            return f"{self.game_platform} - Sleva {self.discount_price} Kč"
        elif self.dlc_platform:
            return f"{self.dlc_platform} - Sleva {self.discount_price} Kč"


class CartItem(Model):
    cart = ForeignKey(Cart, on_delete=CASCADE, related_name='cart_items')
    game_platform = ForeignKey(GamePlatform, on_delete=CASCADE, related_name='cart_items')
    quantity = PositiveIntegerField(default=1)

    def get_price(self):
        return self.game_platform.get_price()

    def get_total_price(self):
        return self.get_price() * self.quantity

    def __str__(self):
        return f"{self.game_platform.game.name} ({self.game_platform.platform}) x {self.quantity}"


class PurchaseItem(Model):
    purchase = ForeignKey(Purchase, on_delete=CASCADE, related_name='purchase_items')
    game_platform = ForeignKey(GamePlatform, on_delete=CASCADE)
    quantity = PositiveIntegerField()

    def get_price(self):
        return self.game_platform.get_price()

    def get_total_price(self):
        return self.get_price() * self.quantity

    def __str__(self):
        return f"{self.game_platform.name} ({self.game_platform.platform}) x {self.quantity}"


class GameKey(Model):
    game_platform = ForeignKey(GamePlatform, on_delete=CASCADE, related_name='keys')
    key = CharField(max_length=50, unique=True)
    is_used = BooleanField(default=False)
