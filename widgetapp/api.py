from rest_framework_extensions.routers import ExtendedDefaultRouter
from rest_framework_mongoengine.routers import MongoRouterMixin

from rest_framework_mongoengine.serializers import DocumentSerializer, PolymorphicDocumentSerializer
from rest_framework_mongoengine.fields import ReferenceField, HyperlinkedDocumentIdentityField
from rest_framework.fields import CharField
from rest_framework_mongoengine.viewsets import ModelViewSet

from rest_framework_extensions.mixins import NestedViewSetMixin, PaginateByMaxMixin

from models import Widget, SpecialWidget, Thing, Vehicle, Truck, Car, Semi

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

class VehicleSerializer(PolymorphicDocumentSerializer):
    _cls = CharField(source='_class_name', required=False, allow_null=True)
    href = HyperlinkedDocumentIdentityField()
    class Meta:
        model = Vehicle

class TruckSerializer(DocumentSerializer):
    class Meta:
        model = Truck

class SemiSerializer(DocumentSerializer):
    class Meta:
        model = Semi

class CarSerializer(DocumentSerializer):
    class Meta:
        model = Car
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


class VehicleViewSet(ModelViewSet):

    serializer_class = VehicleSerializer

    model = Vehicle
    queryset = Vehicle.objects


class TruckViewSet(ModelViewSet):

    serializer_class = TruckSerializer

    model = Truck
    queryset = Truck.objects


class SemiViewSet(ModelViewSet):

    serializer_class = TruckSerializer

    model = Semi
    queryset = Semi.objects

class CarViewSet(ModelViewSet):

    serializer_class = CarSerializer

    model = Car
    queryset = Car.objects


#######
#Router
#######
class ExtendedMongoRouter(MongoRouterMixin, ExtendedDefaultRouter):
    pass