# Generated by Django 2.1.5 on 2019-02-02 03:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("beers", "0007_auto_20181205_1716"),
    ]

    operations = [
        migrations.AlterField(
            model_name="beerstyle",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="styles",
                to="beers.BeerStyleCategory",
            ),
        ),
    ]
