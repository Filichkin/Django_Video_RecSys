from django.shortcuts import (
    get_object_or_404,
    redirect,
    render
    )
from pgvector.django import L2Distance

from .forms import VideoForm
from .models import VideoEmbeddings


VIDEOS_LIST_VIEW = 30
RECOMENDED_COUNT = 3


def upload_video(request):
    if request.method == 'POST':
        form = VideoForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            form.save()
            return redirect('video:index')
    else:
        form = VideoForm()
    return render(request, 'uploader.html', {'form': form})


def videos_list(request):
    videos = VideoEmbeddings.objects.all()[:VIDEOS_LIST_VIEW]
    return render(
        request,
        'index.html',
        {'videos': videos}
    )


def recommended_videos(request, uuid):
    video = get_object_or_404(
        VideoEmbeddings, uuid=uuid
    )
    field_name = 'embedding'
    embedding = getattr(video, field_name)
    recommended_videos = VideoEmbeddings.objects.exclude(uuid=uuid).order_by(
        L2Distance('embedding', embedding)
    )[:RECOMENDED_COUNT]
    return render(
        request,
        'recommendations.html',
        {'recommended_videos': recommended_videos}
    )
