from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [('stores', '0001_initial'), ('catalog', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('posting_number', models.CharField(max_length=255)),
                ('base_order_number', models.CharField(blank=True, max_length=255)),
                ('status', models.CharField(choices=[('created', 'created'), ('awaiting_registration', 'awaiting_registration'), ('awaiting_delivery', 'awaiting_delivery'), ('cancelled', 'cancelled')], max_length=32)),
                ('schema', models.CharField(default='FBS', max_length=8)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stores.store')),
            ],
            options={'unique_together': {('store', 'posting_number')}},
        ),
        migrations.CreateModel(
            name='OrderStatusMap',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('schema', models.CharField(max_length=16)),
                ('ozon_status', models.CharField(max_length=64)),
                ('internal_status', models.CharField(choices=[('created', 'created'), ('awaiting_registration', 'awaiting_registration'), ('awaiting_delivery', 'awaiting_delivery'), ('cancelled', 'cancelled')], max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qty', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('revenue', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('expenses_allocated', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('markup_ratio_fact', models.DecimalField(decimal_places=4, default=0, max_digits=12)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='orders.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.product')),
            ],
        ),
    ]
