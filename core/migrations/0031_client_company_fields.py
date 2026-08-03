from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_event_meta_title_og_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='company_name',
            field=models.CharField(blank=True, max_length=200, default=''),
        ),
        migrations.AddField(
            model_name='customuser',
            name='company_logo',
            field=models.ImageField(blank=True, null=True, upload_to='client_logos/'),
        ),
    ]
