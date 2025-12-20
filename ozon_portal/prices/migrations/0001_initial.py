from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL), ('catalog', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='ExpensePolicySettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('policy', models.CharField(choices=[('USE_MIN', 'Использовать минимум'), ('USE_MAX', 'Использовать максимум')], default='USE_MAX', max_length=16)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PriceExpenseSnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marketing_seller_price', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('net_price', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('acquiring', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('commissions_percent_fbo', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('commissions_percent_fbs', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('total_ozon_expenses', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('markup_ratio', models.DecimalField(decimal_places=4, default=0, max_digits=12)),
                ('desired_marketing_seller_price', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('recalculated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.product')),
            ],
            options={'unique_together': {('product',)}},
        ),
    ]
