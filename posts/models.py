from __future__ import unicode_literals

from django.db import models


class Posts(models.Model):
    posts = models.CharField(max_length=200)
