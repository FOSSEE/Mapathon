import os

from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.conf import settings
from django.dispatch import receiver


# Create your models here.

class Nav(models.Model):
    name = models.CharField(max_length=128)
    link = models.CharField(max_length=255)
    position = models.IntegerField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class SubNav(models.Model):
    nav = models.ForeignKey(Nav, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    link = models.CharField(max_length=255)
    position = models.IntegerField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Page(models.Model):
    permalink = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=50)
    imports = models.TextField(
        help_text='External imports like css,js files, will be placed in <head> tag (already '
                  'includes bootstrap4 and jQuery)', null=True, blank=True
    )
    content = models.TextField(help_text='Body of the page')
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Footer(models.Model):
    title = models.CharField(max_length = 128)
    content = models.TextField(help_text='Body of the footer')
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Banner(models.Model):
    title = models.CharField(max_length = 128)
    content = models.TextField(help_text='Body of the banner')
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    

def get_filename(instance, _):
    extension = os.path.splitext(instance.filename)[1]
    subdir = ''
    if extension in ['.jpg', '.png', '.jpeg']:
        subdir = 'images'
    elif extension == '.pdf':
        subdir = 'pdf'
    elif extension == '.css':
        subdir = 'css'
    elif extension == '.js':
        subdir = 'js'
    elif extension == '.ttf':
        subdir = 'fonts'
    # Add more
    print(extension, subdir)
    return os.path.join('static/cms/uploads', subdir, str(instance.filename))


def validate_filename(value):
    if os.path.exists('static/cms/uploads/' + value):
        raise ValidationError('Static file with that name already exists! Please choose a unique name. You may use '
                              'foldername/filename to upload to a folder')


class StaticFile(models.Model):
    filename = models.CharField(max_length=70, unique=True, validators=[validate_filename])
    file = models.FileField(upload_to=get_filename, storage=FileSystemStorage(),
                            blank=False,
                            help_text='Please upload static file (image, css, js, etc). This file will be accessible '
                                      'at static/cms/filename')

    def __str__(self):
        return self.filename


@receiver(models.signals.post_delete, sender=StaticFile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `StaticFile` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)

@receiver(models.signals.pre_save, sender=StaticFile)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `StaticFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = StaticFile.objects.get(pk=instance.pk).file
    except StaticFile.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)

