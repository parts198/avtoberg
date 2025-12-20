from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='BootstrapState',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('executed', models.BooleanField(default=False)),
                ('executed_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]
