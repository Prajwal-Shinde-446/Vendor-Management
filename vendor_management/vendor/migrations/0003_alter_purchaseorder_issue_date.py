# Generated by Django 4.2.7 on 2023-11-25 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0002_alter_purchaseorder_quality_rating_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaseorder',
            name='issue_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
