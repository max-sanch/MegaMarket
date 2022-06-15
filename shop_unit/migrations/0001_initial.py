# Generated by Django 3.2.3 on 2022-06-15 14:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ShopUnit',
            fields=[
                ('uuid', models.UUIDField(primary_key=True, serialize=False, verbose_name='Уникальный идентификатор')),
                ('name', models.CharField(max_length=2048, verbose_name='Имя товара/категории')),
                ('date', models.DateTimeField(verbose_name='Время последнего обновления элемента')),
                ('type', models.IntegerField(choices=[(1, 'OFFER'), (2, 'CATEGORY')], verbose_name='Тип элемента - категория или товар')),
                ('price', models.BigIntegerField(default=None, null=True, verbose_name='Целое число, для категории - это средняя цена всех дочерних товаров')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop_unit.shopunit')),
            ],
        ),
        migrations.CreateModel(
            name='ShopUnitStatistic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=2048, verbose_name='Имя товара/категории')),
                ('date', models.DateTimeField(verbose_name='Время последнего обновления элемента')),
                ('parentId', models.UUIDField(db_index=True, default=None, null=True, verbose_name='UUID родительской категории')),
                ('type', models.IntegerField(choices=[(1, 'OFFER'), (2, 'CATEGORY')], verbose_name='Тип элемента - категория или товар')),
                ('price', models.BigIntegerField(default=None, null=True, verbose_name='Целое число, для категории - это средняя цена всех дочерних товаров')),
                ('shop_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop_unit.shopunit')),
            ],
        ),
    ]
