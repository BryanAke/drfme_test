__author__ = 'bake3'


from rest_framework import filters as drf_filters
from rest_framework.settings import api_settings

from rest_framework.exceptions import APIException

from mongoengine.queryset.transform import MATCH_OPERATORS

try:
    from django.db.models.constants import LOOKUP_SEP
except ImportError:  # pragma: nocover
    # Django < 1.5 fallback
    from django.db.models.sql.constants import LOOKUP_SEP  # noqa

class InvalidFilterError(APIException):
    """
    Raised when the end user attempts to use a filter on a field
    that has not been whitelisted in the API.
    """
    default_detail = "A field you specified does not allow filtering."
    status_code = 400

class StripCacheFilter(drf_filters.BaseFilterBackend):

    def recursive_strip(self, data):
        #pass in a thing
        if isinstance(data, dict):
            data.pop('_cache', None)
            for key in data:
                data[key] = self.recursive_strip(data[key])
            return data
        if isinstance(data, list):
            return [self.recursive_strip(e) for e in data]
        return data


    def filter_queryset(self, request, queryset, view):
        request_params = request.query_params
        if request.method in ("POST", "PUT", "PATCH"):
            self.recursive_strip(request.DATA)

            d = request.DATA

        return queryset

class MongoProjectionFilterBackend(drf_filters.BaseFilterBackend):
    """
    Provide an interface to MongoEngine's .only() method to limit which fields will be returned
    from the QuerySet.
    """
    projection_param = "fields"

    def get_projection(self, request):
        """
        retrieve the list of fields we want, if they're inclued in this request.
        """
        params = request.query_params.get(self.projection_param)

        if params:
            return [param.strip() for param in params.split(',')]

    def check_fields(self, parameters, doc_fields):
        """
        check parameters provided against dictionary of fields provided by the QuerySet.
        Remove any that don't actually exist.
        """
        return [field for field in parameters if field in doc_fields]

    def filter_queryset(self, request, queryset, view):
        #list of fields in this document
        fields = queryset._document._fields

        #list of fields for the projection in this request
        projection = self.get_projection(request)
        #filter the projection to only contain fields really in this document
        #this prevents filtering for fields that aren't in the schema,
        #so we may want to revisit this in the future.
        if projection:
            projection = self.check_fields(projection, queryset._document._fields)
            #raise undead
            return queryset.only(*projection)
        return queryset

class MongoProjectionViewsetMixin(object):
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS.append(MongoProjectionFilterBackend)
    projection_param = "fields"

    def get_serializer_class(self):
        #get serializer class from super, so we don't clobber any other get_serializer_class magics
        serializer_class = super(MongoProjectionViewsetMixin, self).get_serializer_class()

        if self.request and self.request.query_params.get(self.projection_param, False):
            #filter projection to valid field names
            projection = self.request.query_params.get(self.projection_param).split(',')
            projection = [field for field in projection if field in serializer_class.Meta.model._fields]

            if projection:
                #construct temporary class with Meta parameters set accordingly
                class serializer_klass(serializer_class):
                    class Meta(serializer_class.Meta):
                        fields = projection
                        exclude = None

                return serializer_klass

        return serializer_class


class MongoFilterBackend(drf_filters.BaseFilterBackend):

    def build_filters(self, queryset=None, filters={}, view=None):
        """
        Given a dictionary of filters, create the necessary ORM-level filters.

        Valid values are derived from MongoEngine's Match Operators, which
        mirror MongoDB's operations.

        This filter is designed to deal with filters that can be passed to
        MongoEngine directly after formatting. It will ignore filters that refer to fields it doesn't
        recognize, or operators that MongoEngine doesn't recognize.

        InvalidFilterError will be thrown if the request contains a filter on a non-whitelisted field.
        """

        qs_filters = {}

        qs_fields = queryset._document._fields

        for filter_expr, value in filters.items():
            filter_bits = filter_expr.split(LOOKUP_SEP)
            field_name = filter_bits.pop(0)
            filter_type = filter_bits.pop(0) if len(filter_bits) else 'exact'


            if not field_name in qs_fields:
                # It's not a field we know about. Move along citizen.
                continue

            if field_name in qs_fields and not len(filter_bits) and filter_type not in MATCH_OPERATORS:
                # Valid field, but we don't understand the filter.
                continue

            if len(filter_bits):
                # They passed us too many filter bits, probably for recursive lookups or something. (e.g. ?parent__name__startswith=Foo - we currently can't do that.
                continue

            lookup_bits = self.check_filtering(field_name, queryset, filter_type, filter_bits, view.filter_fields)
            value = self.filter_value_to_python(value, filters, filter_expr, filter_type)

            db_field_name = LOOKUP_SEP.join(lookup_bits)
            qs_filter = "%s%s%s" % (db_field_name, LOOKUP_SEP, filter_type)
            qs_filters[qs_filter] = value

        return qs_filters

    def check_filtering(self, field_name, queryset, filter_type='exact', filter_bits=[], filtering={}):
        """
        Given a field name, an optional filter type and an optional list of
        additional relations, determine if a field can be filtered on.

        If a filter does not meet the needed conditions, it should raise an
        ``InvalidFilterError``.

        If the filter meets the conditions, a list of attribute names (not
        field names) will be returned.
        """

        fields = queryset._document._fields

        if not field_name in filtering:
            raise InvalidFilterError("The '%s' field does not allow filtering." % field_name)

        # Check to see if it's a relational lookup and if that's allowed.
        if len(filter_bits):
            #currently not working (recursive querying necessitates additional queries, and lots of mess.
            #ref_obj = fields[field_name].document_type_obj
            #ref_fields = ref_obj._fields
            #return [fields[field_name].name]
            raise InvalidFilterError("Recursive filtering of reference fields under development.")

        return [fields[field_name].name]

    def filter_value_to_python(self, value, filters, filter_expr, filter_type):
        """
        Turn the string ``value`` into a python object.
        """
        # Simple values
        if value in ['true', 'True']:
            value = True
        elif value in ['false', 'False']:
            value = False
        elif value in ['nil', 'none', 'None']:
            value = None

        # Split on ',' if not empty string and either an in or range filter.
        if filter_type in ('in', 'range') and len(value):
            if hasattr(filters, 'getlist'):
                value = []

                for part in filters.getlist(filter_expr):
                    value.extend(part.split(','))
            else:
                value = value.split(',')

        return value


    def filter_queryset(self, request, queryset, view):
        request_filters = request.query_params
        applicable_filters = self.build_filters(queryset=queryset, filters=request_filters, view=view)
        return queryset.filter(**applicable_filters)
