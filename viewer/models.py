from django.utils import timezone
from email.policy import default

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Model, CharField, ManyToManyField, ForeignKey, CASCADE, DateField, DecimalField, TextField, \
    DO_NOTHING, SET_NULL, IntegerField, DateTimeField, PositiveIntegerField, ImageField, BooleanField
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
    name = CharField(max_length=36, null=False, blank=False, unique=True)

    def __str__(self):
        return f"{self.name}"


class GameMode(Model):
    name = CharField(max_length=36, null=False, blank=False, unique=True)

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
    min_configuration_cpu = ForeignKey(CPU, on_delete=SET_NULL, null=True, blank=True, related_name='min_cpu',
                                       verbose_name='CPU (Minimální')
    min_configuration_ram = ForeignKey(RAM, on_delete=SET_NULL, null=True, blank=True, related_name='min_ram',
                                       verbose_name='RAM (Minimální)')
    min_configuration_gpu = ForeignKey(GPU, on_delete=SET_NULL, null=True, blank=True, related_name='min_gpu',
                                       verbose_name='GPU (Minimální')
    min_configuration_hdd = ForeignKey(HDD, on_delete=SET_NULL, null=True, blank=True, related_name='min_hdd',
                                       verbose_name='HDD (Minimální)')
    min_additional_notes = ForeignKey(AdditionalNotes, on_delete=SET_NULL, null=True, blank=True,
                                      related_name='min_game_notes', verbose_name='Dodatečné poznámky')
    recommended_configuration_os = ForeignKey(OS, on_delete=SET_NULL, null=True, blank=True,
                                              related_name='recommended_os', verbose_name='Doporučený operační systém')
    recommended_configuration_cpu = ForeignKey(CPU, on_delete=SET_NULL, null=True, blank=True,
                                               related_name='recommended_cpu', verbose_name='CPU (Dporučené)')
    recommended_configuration_ram = ForeignKey(RAM, on_delete=SET_NULL, null=True, blank=True,
                                               related_name='recommended_ram', verbose_name='RAM (Doporučené)')
    recommended_configuration_gpu = ForeignKey(GPU, on_delete=SET_NULL, null=True, blank=True,
                                               related_name='recommended_gpu', verbose_name='GPU (Dporučené)')
    recommended_configuration_hdd = ForeignKey(HDD, on_delete=SET_NULL, null=True, blank=True,
                                               related_name='recommended_hdd', verbose_name='HDD (Doporučené)')
    recommended_configuration_additional_notes = ForeignKey(AdditionalNotes, on_delete=SET_NULL, null=True, blank=True,
                                                            related_name='recommended_game_notes',
                                                            verbose_name='Dodatečné poznámky')
    description = TextField(null=True, blank=True, verbose_name='Popis')
    price = DecimalField(max_digits=10, decimal_places=2, null=False, blank=False, default=0, verbose_name='Cena')
    quantity = models.PositiveIntegerField(default=0, verbose_name='Množství')

    def purchase(self, user, amount):
        if amount <= 0:
            raise InvalidPurchaseAmountException("Objednávka musí mít minimálně 1ks.")
        if amount > self.quantity:
            raise InsufficientQuantityException("Nedostatek zboží skladem.")

        self.quantity -= amount
        self.save()
        Purchase.objects.create(user=user, game=self, quantity=amount)

    def restock(self, amount):
        if amount <= 0:
            raise InvalidPurchaseAmountException("Naskladněné zboží musí být více než 0")

        self.quantity += amount
        self.save()

    def get_images(self):
        return GameImage.objects.filter(game=self)

    def __str__(self):
        return self.name


class GameImage(Model):
    game = ForeignKey(Game, related_name='images', on_delete=DO_NOTHING)
    image = ImageField(upload_to='viewer/static/game_images/')

    def save(self, *args, **kwargs):
        self.image.name = self.image.name.lower().replace(" ", "")
        super().save(*args, **kwargs)


class GameVideo(models.Model):
    game = models.ForeignKey(Game, related_name='videos', on_delete=models.CASCADE)
    video_url = models.URLField(verbose_name='YouTube URL')
    title = models.CharField(max_length=255, blank=True, null=True)


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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_cart_items')
    created_at = DateTimeField(auto_now_add=True)

    def add_game(self, game):
        cart_item, created = CartItem.objects.get_or_create(cart=self, game=game)
        if not created:
            cart_item.quantity += 1
            cart_item.save()

    def remove_game(self, game):
        cart_item = CartItem.objects.filter(cart=self, game=game).first()
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

    def clear_cart(self):
        CartItem.objects.filter(cart=self).delete()

    def __str__(self):
        return f'{self.user.username} - {self.game.name} - {self.quantity}'


class CartItem(Model):
    cart = ForeignKey(Cart, on_delete=CASCADE, related_name='CartItem')
    game = ForeignKey(Game, on_delete=CASCADE, related_name='GameItem')
    quantity = PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.game.name} x {self.quantity}"


class Purchase(Model):
    user = ForeignKey(User, on_delete=CASCADE, related_name='user_purchases', verbose_name='Zákazník')
    purchase_date = DateTimeField(auto_now_add=True, verbose_name='Datum nákupu')
    total_price = DecimalField(max_digits=10, decimal_places=2, default=0.0)
    payment_id = CharField(max_length=100, blank=True, null=True)
    is_paid = BooleanField(default=False)

    def calculate_total(self):
        total = sum(item.game.price * item.quantity for item in self.purchase_items.all())
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


class PurchaseItem(Model):
    purchase = ForeignKey(Purchase, on_delete=CASCADE, related_name='purchase_items')
    game = ForeignKey(Game, on_delete=CASCADE)
    quantity = PositiveIntegerField()

    def __str__(self):
        return f"{self.game.name} x {self.quantity}"


class Discount(Model):
    game = ForeignKey(Game, on_delete=CASCADE, related_name='discounts')
    discount_price = DecimalField(max_digits=10, decimal_places=2)
    start_date = DateField()
    end_date = DateField(null=True, blank=True)

    def is_active(self):
        now = timezone.now().date()
        return self.start_date <= now and (not self.end_date or self.end_date >= now)

    def get_discount_percent(self):
        if self.game.price > 0:
            return round((self.game.price - self.discount_price) / self.game.price * 100, 2)
        return 0

