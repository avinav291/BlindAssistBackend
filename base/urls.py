from django.conf.urls import url
import base.views
urlpatterns = [
    url(r'^getImageCaption/', base.views.getImageCaption, name="getImageCaption"),
]
