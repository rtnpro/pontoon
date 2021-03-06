import requests

from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.db import models
from django.db.models.signals import post_save
from django.forms import ModelForm

class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User)

    # Other fields here
    transifex_username = models.CharField(max_length=40)
    transifex_password = models.CharField(max_length=128)
    svn_username = models.CharField(max_length=40)
    svn_password = models.CharField(max_length=128)

# For every newly created user
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

        # Grant permission to Mozilla localizers
        url = "https://mozillians.org/api/v1/users/"
        payload = {
            "app_name": "pontoon",
            "app_key": settings.MOZILLIANS_API_KEY,
            "groups": "l10n",
            "format": "json",
            "limit": 1000, # By default, limited to 20
            "is_vouched": True
        }

        import logging
        logger = logging.getLogger('playdoh')

        try:
            r = requests.get(url, params=payload)
            logger.debug(instance.email)
            email = instance.email

            for l in r.json["objects"]:
                logger.debug(l["email"])
                if email == l["email"]:
                    can_localize = Permission.objects.get(codename="can_localize")
                    instance.user_permissions.add(can_localize)
                    break
        except Exception:
            pass

post_save.connect(create_user_profile, sender=User)

class Locale(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=128)

    def __unicode__(self):
        return self.name

class Project(models.Model):
    name = models.CharField(max_length=128, unique=True)
    url = models.URLField("URL", unique=True)
    locales = models.ManyToManyField(Locale)

    # Repositories
    repository = models.URLField("Repository URL (SVN or HG)", blank=True)
    transifex_project = models.CharField(max_length=128, blank=True)
    transifex_resource = models.CharField(max_length=128, blank=True)

    # Campaign info
    info_brief = models.TextField("Campaign Brief", blank=True)
    info_locales = models.TextField("Intended Locales and Regions", blank=True)
    info_audience = models.TextField("Audience, Reach, and Impact", blank=True)
    info_metrics = models.TextField("Success Metrics", blank=True)

    # User interface
    external = models.BooleanField("Open project website in external window")
    links = models.BooleanField("Enable links on the project website")

    class Meta:
        permissions = (
            ("can_manage", "Can manage projects"),
            ("can_localize", "Can localize projects"),
        )

    def __unicode__(self):
        return self.name

class Subpage(models.Model):
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=128)
    url = models.URLField("URL")

    def __unicode__(self):
        return self.name

class Entity(models.Model):
    project = models.ForeignKey(Project)
    string = models.TextField()
    comment = models.TextField(blank=True)
    key = models.TextField(blank=True) # Needed for webL10n
    source = models.TextField(blank=True) # Needed for webL10n

    def __unicode__(self):
        return self.string

class Translation(models.Model):
    entity = models.ForeignKey(Entity)
    locale = models.ForeignKey(Locale)
    string = models.TextField()
    author = models.CharField(max_length=128)
    date = models.DateTimeField()

    def __unicode__(self):
        return self.string

class ProjectForm(ModelForm):
    class Meta:
        model = Project

    def clean(self):
        cleaned_data = super(ProjectForm, self).clean()
        repository = cleaned_data.get("repository")
        transifex_project = cleaned_data.get("transifex_project")
        transifex_resource = cleaned_data.get("transifex_resource")

        if transifex_project and not transifex_resource:
            self._errors["transifex_resource"] = self.error_class([u"Both fields are required."])
            del cleaned_data["transifex_project"]

        elif not transifex_project and transifex_resource:
            self._errors["transifex_project"] = self.error_class([u"Both fields are required."])
            del cleaned_data["transifex_resource"]

        elif not transifex_project and not transifex_resource and not repository:
            self._errors["repository"] = self.error_class([u"You either need to provide repository URL..."])
            self._errors["transifex_project"] = self.error_class([u"...or Transifex project and resource."])

        return cleaned_data
