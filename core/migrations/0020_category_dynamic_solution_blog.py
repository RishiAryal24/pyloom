# Generated manually for dynamic admin-managed categories.

import django.db.models.deletion
from django.db import migrations, models
from django.utils.text import slugify


SOLUTION_CATEGORIES = {
    'healthcare': 'Healthcare',
    'finance': 'Finance',
    'education': 'Education',
}

BLOG_CATEGORIES = {
    'healthcare': 'Healthcare',
    'finance': 'Finance',
    'education': 'Education',
    'technology': 'Technology',
    'ethics': 'Ethics',
    'tutorial': 'Tutorial',
    'news': 'News',
}


def create_categories_and_link_content(apps, schema_editor):
    Category = apps.get_model('core', 'Category')
    Solution = apps.get_model('core', 'Solution')
    BlogPost = apps.get_model('core', 'BlogPost')

    def get_or_create_category(content_type, old_value, label_lookup):
        label = label_lookup.get(old_value) or old_value.replace('_', ' ').title()
        slug = slugify(old_value or label)
        category, _ = Category.objects.get_or_create(
            content_type=content_type,
            slug=slug,
            defaults={'name': label},
        )
        return category

    for order, (slug, name) in enumerate(SOLUTION_CATEGORIES.items()):
        Category.objects.get_or_create(
            content_type='solution',
            slug=slug,
            defaults={'name': name, 'order': order},
        )

    for order, (slug, name) in enumerate(BLOG_CATEGORIES.items()):
        Category.objects.get_or_create(
            content_type='blog',
            slug=slug,
            defaults={'name': name, 'order': order},
        )

    for solution in Solution.objects.all():
        category = get_or_create_category('solution', solution.category, SOLUTION_CATEGORIES)
        solution.category_new_id = category.id
        solution.save(update_fields=['category_new'])

    for post in BlogPost.objects.all():
        category = get_or_create_category('blog', post.category, BLOG_CATEGORIES)
        post.category_new_id = category.id
        post.save(update_fields=['category_new'])


def unlink_content(apps, schema_editor):
    Solution = apps.get_model('core', 'Solution')
    BlogPost = apps.get_model('core', 'BlogPost')

    for solution in Solution.objects.select_related('category_new'):
        solution.category = solution.category_new.slug if solution.category_new_id else ''
        solution.save(update_fields=['category'])

    for post in BlogPost.objects.select_related('category_new'):
        post.category = post.category_new.slug if post.category_new_id else ''
        post.save(update_fields=['category'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_sitesettings_maintenance_mode'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(blank=True, max_length=120)),
                ('content_type', models.CharField(choices=[('solution', 'Solution'), ('blog', 'Blog')], max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Categories',
                'ordering': ['content_type', 'order', 'name'],
                'unique_together': {('content_type', 'slug')},
            },
        ),
        migrations.AddField(
            model_name='solution',
            name='category_new',
            field=models.ForeignKey(limit_choices_to={'content_type': 'solution', 'is_active': True}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='solutions', to='core.category'),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='category_new',
            field=models.ForeignKey(limit_choices_to={'content_type': 'blog', 'is_active': True}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='blog_posts', to='core.category'),
        ),
        migrations.RunPython(create_categories_and_link_content, unlink_content),
        migrations.RemoveField(
            model_name='solution',
            name='category',
        ),
        migrations.RemoveField(
            model_name='blogpost',
            name='category',
        ),
        migrations.RenameField(
            model_name='solution',
            old_name='category_new',
            new_name='category',
        ),
        migrations.RenameField(
            model_name='blogpost',
            old_name='category_new',
            new_name='category',
        ),
        migrations.AlterField(
            model_name='solution',
            name='category',
            field=models.ForeignKey(limit_choices_to={'content_type': 'solution', 'is_active': True}, on_delete=django.db.models.deletion.PROTECT, related_name='solutions', to='core.category'),
        ),
        migrations.AlterField(
            model_name='blogpost',
            name='category',
            field=models.ForeignKey(limit_choices_to={'content_type': 'blog', 'is_active': True}, on_delete=django.db.models.deletion.PROTECT, related_name='blog_posts', to='core.category'),
        ),
    ]
