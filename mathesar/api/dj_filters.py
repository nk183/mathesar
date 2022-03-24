from django_filters import BooleanFilter, DateTimeFromToRangeFilter, OrderingFilter
from django_property_filter import PropertyFilterSet, PropertyBaseInFilter, PropertyCharFilter, PropertyOrderingFilter

from mathesar.database.types import MathesarType
from mathesar.models import Schema, Table, Database

FILTER_OPTIONS_BY_TYPE_IDENTIFIER = {
    MathesarType.BOOLEAN.value:
    {
        "db_type": "BOOLEAN",
        "options": [{
            "op": "eq",
            "value": {
                "allowed_types": ["BOOLEAN"],
            }
        }, {
            "op": "is_null",
            "value": "null",
        }]
    }
}


class CharInFilter(PropertyBaseInFilter, PropertyCharFilter):
    pass


class SchemaFilter(PropertyFilterSet):
    database = CharInFilter(field_name='database__name', lookup_expr='in')
    name = CharInFilter(field_name='name', lookup_expr='in')

    sort_by = PropertyOrderingFilter(
        fields=(
            ('id', 'id'),
            ('name', 'name'),
        ),
        label="Sort By",
    )

    class Meta:
        model = Schema
        fields = ['name']


class TableFilter(PropertyFilterSet):
    name = CharInFilter(field_name='name', lookup_expr='in')
    created = DateTimeFromToRangeFilter(field_name='created_at')
    updated = DateTimeFromToRangeFilter(field_name='updated_at')
    not_imported = BooleanFilter(lookup_expr="isnull", field_name='import_verified')

    sort_by = PropertyOrderingFilter(
        fields=(
            ('id', 'id'),
            ('name', 'name'),
        ),
        label="Sort By",
    )

    class Meta:
        model = Table
        fields = ['name', 'schema', 'created_at', 'updated_at', 'import_verified']


class DatabaseFilter(PropertyFilterSet):
    sort_by = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('name', 'name'),
        ),
        label="Sort By",
    )

    class Meta:
        model = Database
        fields = ['deleted']
