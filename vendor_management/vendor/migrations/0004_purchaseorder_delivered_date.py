# Generated by Django 4.2.7 on 2023-11-26 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0003_alter_purchaseorder_issue_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorder',
            name='delivered_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
