from unidecode import unidecode
from django.db import models
from django.template.defaultfilters import slugify


# Manifest provides basic item metadata for all open context items that get a URI
class Manifest(models.Model):
    uuid = models.CharField(max_length=50, primary_key=True)
    project_uuid = models.CharField(max_length=50, db_index=True)
    source_id = models.CharField(max_length=50, db_index=True)
    item_type = models.CharField(max_length=50)
    repo = models.CharField(max_length=200)
    class_uri = models.CharField(max_length=200)
    slug = models.SlugField(max_length=60, blank=True, null=True)
    label = models.CharField(max_length=200)
    des_predicate_uuid = models.CharField(max_length=50)
    views = models.IntegerField()
    indexed = models.DateTimeField(blank=True, null=True)
    vcontrol = models.DateTimeField(blank=True, null=True)
    archived = models.DateTimeField(blank=True, null=True)
    published = models.DateTimeField(db_index=True)
    revised = models.DateTimeField(db_index=True)
    record_updated = models.DateTimeField(auto_now=True)

    def make_slug(self):
        """
        creates a unique slug for a label with a given type
        """
        man_gen = ManifestGeneration()
        slug = man_gen.make_manifest_slug(self.label, self.item_type)
        return slug

    def save(self):
        """
        saves a manifest item with a good slug
        """
        self.slug = self.make_slug()
        super(Manifest, self).save()

    class Meta:
        db_table = 'oc_manifest'


class ManifestGeneration():

    def make_manifest_slug(self, label, item_type):
        """
        gets the most recently updated Subject date
        """
        raw_slug = slugify(unidecode(label[:52]))
        slug = raw_slug
        try:
            slug_in = Manifest.objects.get(item_type=item_type, slug=raw_slug)
            slug_exists = True
        except Manifest.DoesNotExist:
            slug_exists = False
        if(slug_exists):
            try:
                slug_count = Manifest.objects.filter(item_type=item_type, slug__startswith=raw_slug).count()
            except Manifest.DoesNotExist:
                slug_count = 0
            if(slug_count > 0):
                slug = raw_slug + "--" + item_type[:3] + "-" + str(slug_count + 1)
        return slug

    def fix_blank_slugs(self):
        cc = 0
        try:
            no_slugs = Manifest.objects.all().exclude(slug__isnull=False)
        except Manifest.DoesNotExist:
            no_slugs = False
        if(no_slugs is not False):
            for nslug in no_slugs:
                nslug.save()
                cc += 1
        return cc