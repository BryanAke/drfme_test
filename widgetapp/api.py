from rest_framework_extensions.routers import ExtendedDefaultRouter
from rest_framework_mongoengine.routers import MongoRouterMixin

from rest_framework_mongoengine.serializers import DocumentSerializer, PolymorphicDocumentSerializer
from rest_framework_mongoengine.fields import ReferenceField
from rest_framework_mongoengine.viewsets import ModelViewSet

from rest_framework_extensions.mixins import NestedViewSetMixin, PaginateByMaxMixin

from models import Widget, SpecialWidget, Thing

#######
#Serializers
#######

class WidgetSerializer(PolymorphicDocumentSerializer):

    class Meta:
        model = Widget
        extra_kwargs = {
            'parent': {
                'required': False
            }

        }

class SpecialWidgetSerializer(DocumentSerializer):
    class Meta:
        model = SpecialWidget

class ThingSerializer(DocumentSerializer):
    class Meta:
        model = Thing


#######
#ViewSets
#######
class WidgetViewSet(ModelViewSet):

    serializer_class = WidgetSerializer

    model = Widget
    queryset = Widget.objects

    def get_queryset(self):
        qs = super(WidgetViewSet, self).get_queryset()
        return qs.no_dereference()

class SpecialWidgetViewSet(ModelViewSet):
    #_auto_dereference = True
    serializer_class = SpecialWidgetSerializer

    model = SpecialWidget
    queryset = SpecialWidget.objects

class ThingViewSet(ModelViewSet):
    #_auto_dereference = True
    serializer_class = ThingSerializer

    model = Thing
    queryset = Thing.objects


#######
#Router
#######
class ExtendedMongoRouter(MongoRouterMixin, ExtendedDefaultRouter):
    pass