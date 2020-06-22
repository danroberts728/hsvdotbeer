# Generated by Django 3.0.4 on 2020-06-02 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beers', '0033_auto_20200124_2044'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='beer',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('color_srm__gte', 1), ('color_srm__lte', 500)), ('color_srm__isnull', True), _connector='OR'), name='srm_not_unrealistic'),
        ),
    ]
