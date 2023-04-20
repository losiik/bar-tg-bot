from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class BaseClass(models.Model):
    data = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')


class Menu(BaseClass):
    CATEGORY_CHOICES = (
        ('ALCO', 'Алкогольные напитки'),
        ('NONALCO', 'Безалкогольные напитки'),
        ('SNACK', 'Закуски'),
        ('MAIN', 'Основные блюда'),
    )

    UNITS = (
        ('N', '-'),
        ('G', 'гр.'),
        ('M', 'мл.'),
    )

    category = models.CharField(max_length=7, choices=CATEGORY_CHOICES,
                                default='MAIN',
                                verbose_name='Категория позиции')
    title = models.CharField(max_length=255, verbose_name='Название позиции')
    weight_volume = models.CharField(max_length=255, default=0, verbose_name='Объем/Вес')
    units = models.CharField(max_length=1, choices=UNITS, default='N', verbose_name='Единицы измерения')
    energy_value = models.CharField(max_length=255, default=0, verbose_name='Энергетическая ценность в кКл')
    price = models.CharField(max_length=255, verbose_name='Цена')
    description = models.TextField(verbose_name='Описание', blank=True)
    photo = models.ImageField(upload_to='imgs', verbose_name='Фото')

    def __str__(self):
        name_object = self.title + ' ' + f'({str(self.id)})'
        return name_object


class Promo(BaseClass):
    title = models.CharField(max_length=255, verbose_name='Название акции')
    description = models.TextField(verbose_name='Условия акции', blank=True)

    def __str__(self):
        name_object = self.title + ' ' + f'({str(self.id)})'
        return name_object


class Review(BaseClass):
    from_username = models.CharField(max_length=255, verbose_name='Отзыв от')
    review_content = models.TextField(verbose_name='Отзыв')

    def __str__(self):
        name_object = f'({str(self.data)})' + ' ' + self.from_username
        return name_object


class ClientData(BaseClass):
    user_id = models.CharField(max_length=255, verbose_name='User_id пользователя')
    bonus_amount = models.FloatField(verbose_name='Количество бонусов')

    def __str__(self):
        name_object = self.user_id
        return name_object


class Orders(BaseClass):
    user_id = models.CharField(max_length=255)
    amount = models.FloatField()
    order_data = models.TextField()


@receiver(post_save, sender=Orders)
def add_data_to_avito_accounts(sender, instance, **kwargs):
    client_in_base = False
    clients = ClientData.objects.values()
    for client in clients:
        if client['user_id'] == instance.user_id:
            bonus_amount = client['bonus_amount'] + instance.amount * 0.05
            ClientData.objects.update(user_id=instance.user_id,
                                      bonus_amount=bonus_amount)
            client_in_base = True

    if not client_in_base:
        ClientData.objects.create(user_id=instance.user_id,
                                  bonus_amount=instance.amount * 0.05)
