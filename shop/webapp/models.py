from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
# для автоматической генерации токена
import uuid
from django.utils.timezone import now


# Токен регистрации - генерируется при первичной регистрации пользователя
# и хранится в отдельной модели с привязкой к пользователю.
class RegistrationToken(models.Model):
    token = models.UUIDField(default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def is_expired(self):
        delta = now() - self.created_at
        delta_hours = delta.total_seconds() / 3600
        return delta_hours > settings.TOKEN_EXPIRATION_HOURS

    def __str__(self):
        return "%s" % self.token



class SoftDeleteManager(models.Manager):
    def active(self):
        return self.filter(is_deleted=False)

    def deleted(self):
        return self.filter(is_deleted=True)



class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название товара")
    description = models.TextField(max_length= 2000, blank=True, null=True, verbose_name="Описание")
    date = models.DateField(verbose_name="Дата поступления")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена товара")
    categories = models.ManyToManyField('Category', blank=True, related_name='products_by_category',
                                        verbose_name='Категория товара')

    def __str__(self):
        return "%s-%s" % (self.name, self.price)


class Photo(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='photos', verbose_name="Название товара")
    photo = models.ImageField(upload_to='photos', verbose_name="Картинка")


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название категории")
    description = models.TextField(max_length= 2000, blank=True, null=True, verbose_name="Описание")

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(User,on_delete=models.PROTECT, related_name='orders', verbose_name="Заказ")
    products = models.ManyToManyField(Product, related_name="orders", verbose_name="Список товаров на заказ")
    phone = models.CharField(max_length=255, verbose_name="Телефон")
    address = models.CharField(max_length=255, blank = True, null=True, verbose_name="Адрес доставки")
    comment = models.TextField(max_length=2000, blank=True, null=True, verbose_name="Коментарии")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время создания")


    def __str__(self):
        return "%s - %s" %(self.user, self.created_date)