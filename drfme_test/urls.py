from django.conf.urls import patterns, include, url
from django.contrib import admin

from widgetapp.api import ExtendedMongoRouter, WidgetViewSet, SpecialWidgetViewSet, ThingViewSet

router = ExtendedMongoRouter()
router.register(r'widgets', WidgetViewSet)
router.register(r'specialwidgets', SpecialWidgetViewSet)
router.register(r'things', ThingViewSet)

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'drfme_test.views.home', name='home'),
    url(r'^api/', include(router.urls)),

    url(r'^admin/', include(admin.site.urls)),
)
