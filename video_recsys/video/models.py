import uuid as uu

from django.db import models
from django.urls import reverse
from pgvector.django import VectorField

from .constants import EMBEDDING_DIM, NAME_MAX_LENGTH
from .utils import get_embedding


class VideoEmbeddings(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        default=uu.uuid4
        )
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    videofile = models.FileField(upload_to='original_videos/%y')
    embedding = VectorField(
        dimensions=EMBEDDING_DIM,
        null=True,
        blank=True,
    )

    class Meta:
        managed = True
        ordering = ['name']

    def save(self, *args, **kwargs):
        self.embedding = get_embedding(self.videofile)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('video:recommended_videos', args=[self.uuid])
