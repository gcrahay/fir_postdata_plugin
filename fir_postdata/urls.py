from django.conf.urls import patterns, url

from fir_postdata import views

urlpatterns = patterns('',
	url(r'^$', views.postdata_landing, name='landing'),
)
