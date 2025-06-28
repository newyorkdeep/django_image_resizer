from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('nuke', views.nuke, name='nuke'),
    path('resize_all_images', views.resize_all_images, name='resize_all_images'),
    path('number_input', views.number_input, name='number_input'),
    path('download_all_images', views.download_all_images, name='download_all_images'),
    path('download_image/<int:image_id>', views.download_image, name='download_image'),
    path('convert_all_images_to_jpg', views.convert_all_images_to_jpg, name='convert_all_images_to_jpg'),
    path('convert_all_images_to_png', views.convert_all_images_to_png, name='convert_all_images_to_png'),
    path('group_name', views.group_name, name='group_name'),
]