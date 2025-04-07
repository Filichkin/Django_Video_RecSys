from django import forms

from .models import VideoEmbeddings


class VideoForm(forms.ModelForm):
    class Meta:
        model = VideoEmbeddings
        fields = ['name', 'videofile']
