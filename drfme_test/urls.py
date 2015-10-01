from django.conf.urls import patterns, include, url
from django.contrib import admin

from widgetapp.api import ExtendedMongoRouter, WidgetViewSet, SpecialWidgetViewSet, ThingViewSet, VehicleViewSet, TruckViewSet, CarViewSet, SemiViewSet

router = ExtendedMongoRouter()
router.register(r'widgets', WidgetViewSet)
router.register(r'specialwidgets', SpecialWidgetViewSet)
router.register(r'things', ThingViewSet)

router.register(r'vehicles', VehicleViewSet)
router.register(r'trucks', TruckViewSet)
router.register(r'sermis', SemiViewSet)
router.register(r'cars', CarViewSet)

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'drfme_test.views.home', name='home'),
    url(r'^api/', include(router.urls)),

    url(r'^admin/', include(admin.site.urls)),
)
