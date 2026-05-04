from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rh', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='conge',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
