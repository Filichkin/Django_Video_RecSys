import uuid as uu

from django.db import models
from django.urls import reverse
from pgvector.django import VectorField

from .utils import get_embedding


class VectorEmbeddings(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        default=uu.uuid4
        )
    name = models.CharField(max_length=500)
    videofile = models.FileField(upload_to='video/%y')
    embedding = VectorField(
        dimensions=512,
        null=True,
        blank=True,
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.embedding = get_embedding(self.videofile.path)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('posts:recommended_videos', args=[self.uuid])

    class Meta:
        managed = True
        ordering = ['name']
