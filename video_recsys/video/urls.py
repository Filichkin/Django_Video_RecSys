from django.urls import path

from . import views


app_name = 'video'

urlpatterns = [
    path('', views.upload_video, name='upload'),
    path('videos/', views.videos_list, name='index'),
    path(
        'recommended_videos/<uuid:uuid>/',
        views.recommended_videos,
        name='recommended_videos'
    ),
]
