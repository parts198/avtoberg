from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [('stores', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='Warehouse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('external_id', models.CharField(max_length=255)),
                ('type', models.CharField(choices=[('FBO', 'FBO'), ('FBS', 'FBS'), ('rFBS', 'rFBS')], default='FBS', max_length=10)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='warehouses', to='stores.store')),
            ],
            options={'unique_together': {('store', 'external_id')}},
        ),
    ]
