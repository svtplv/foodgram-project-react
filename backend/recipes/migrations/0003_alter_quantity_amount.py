# Generated by Django 4.2.10 on 2024-03-06 10:31

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0002_alter_quantity_amount_alter_recipe_cooking_time_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="quantity",
            name="amount",
            field=models.PositiveSmallIntegerField(
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(3000),
                ],
                verbose_name="Количество",
            ),
        ),
    ]
