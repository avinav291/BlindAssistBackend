from django.conf.urls import url
import base.views
urlpatterns = [
    url(r'^getImageCaption/', base.views.getImageCaption, name="getImageCaption"),
    url(r'^uploadImages/', base.views.uploadImages, name="uploadImages"),
    url(r'^uploadImage/', base.views.uploadImage, name="uploadImages"),
    url(r'^ping/', base.views.ping, name="uploadImages"),
]
