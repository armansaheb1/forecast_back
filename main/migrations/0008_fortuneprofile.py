# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_alter_customuser_language'),
    ]

    operations = [
        migrations.CreateModel(
            name='FortuneProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='نام')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='تاریخ تولد')),
                ('age', models.IntegerField(blank=True, null=True, verbose_name='سن')),
                ('gender', models.CharField(blank=True, choices=[('male', 'مرد'), ('female', 'زن'), ('other', 'سایر')], max_length=10, null=True, verbose_name='جنسیت')),
                ('relationship_status', models.CharField(blank=True, choices=[('single', 'مجرد'), ('married', 'متأهل'), ('divorced', 'مطلقه'), ('widowed', 'بیوه'), ('in_relationship', 'در رابطه')], max_length=20, null=True, verbose_name='وضعیت رابطه')),
                ('job_status', models.CharField(blank=True, choices=[('employed', 'شاغل'), ('unemployed', 'بیکار'), ('student', 'دانشجو'), ('retired', 'بازنشسته'), ('self_employed', 'خویش‌فرما'), ('freelancer', 'فریلنسر')], max_length=20, null=True, verbose_name='وضعیت شغلی')),
                ('city', models.CharField(blank=True, max_length=100, null=True, verbose_name='شهر')),
                ('country', models.CharField(blank=True, max_length=100, null=True, verbose_name='کشور')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='یادداشت‌ها')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاریخ به‌روزرسانی')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='fortune_profiles', to='main.customuser', verbose_name='کاربر')),
            ],
            options={
                'verbose_name': 'پروفایل فال',
                'verbose_name_plural': 'پروفایل‌های فال',
                'ordering': ['-created_at'],
            },
        ),
    ]
