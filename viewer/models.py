from django.contrib.auth.models import User
from django.db import models
from django.db.models import Model, CharField, ManyToManyField, ForeignKey, CASCADE, DateField, DecimalField, TextField, \
    DO_NOTHING, SET_NULL, IntegerField, DateTimeField, PositiveIntegerField
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
    platform = ManyToManyField(Platform, blank=True, related_name='platform_games',
                               verbose_name='Platforma')
    genres = ManyToManyField(Genre, blank=True, related_name='genres_of_game',
                             verbose_name='Žánr')
    game_mode = ManyToManyField(GameMode, blank=True, related_name='mode_of_game',
                                verbose_name='Herní mód')
    release_date = DateField(null=True, blank=True, verbose_name='Datum vydání')
    developer = ManyToManyField(Developer, blank=True, related_name='developer_of_game',
                                verbose_name='Vývojář')
    publisher = ManyToManyField(Publisher, blank=True, related_name='publisher_of_game',
                                verbose_name='Vydavatel')
    images = MultiFileField(min_num=1, max_num=10, max_file_size=1920 * 1080 * 5, required=False)
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

    def __str__(self):
        return self.name


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
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)

    def update_quantity(self, amount):
        if amount < 0:
            raise InvalidPurchaseAmountException("Množství musí být větší než 0")
        if amount == 0:
            self.delete()
        else:
            self.quantity = amount
            self.save()

    def __str__(self):
        return f'{self.user.username} - {self.game.name} - {self.quantity}'


class Purchase(Model):
    game = ForeignKey(Game, on_delete=CASCADE, related_name='purchases', verbose_name='Hra')
    user = ForeignKey(User, on_delete=CASCADE, related_name='user_purchases', verbose_name='Zákazník')
    quantity = PositiveIntegerField(verbose_name='Množství')
    purchase_date = DateTimeField(auto_now_add=True, verbose_name='Datum nákupu')

    def __str__(self):
        return f'{self.user.username} - {self.game.name} - {self.quantity}'
