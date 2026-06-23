from django.db import migrations
from django.db.models import Q
from django.utils.text import slugify


def backfill_content_slugs(apps, schema_editor):
    models = (
        apps.get_model('core', 'Solution'),
        apps.get_model('core', 'Event'),
        apps.get_model('core', 'Project'),
        apps.get_model('core', 'Article'),
    )

    for model in models:
        used_slugs = set(
            model.objects.exclude(Q(slug='') | Q(slug__isnull=True))
            .values_list('slug', flat=True)
        )
        missing_slugs = model.objects.filter(
            Q(slug='') | Q(slug__isnull=True)
        ).order_by('pk')

        for item in missing_slugs:
            fallback = f'{model._meta.model_name}-{item.pk}'
            base_slug = slugify(getattr(item, 'title', '')) or fallback
            candidate = base_slug[:200]
            counter = 2

            while candidate in used_slugs:
                suffix = f'-{counter}'
                candidate = f'{base_slug[:200 - len(suffix)]}{suffix}'
                counter += 1

            model.objects.filter(pk=item.pk).update(slug=candidate)
            used_slugs.add(candidate)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_article_canonical_url_article_meta_description_and_more'),
    ]

    operations = [
        migrations.RunPython(backfill_content_slugs, migrations.RunPython.noop),
    ]
