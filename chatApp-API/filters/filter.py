import django_filters
from userApp.models import User


class UserSearchFilter(django_filters.FilterSet):
    print("Filter called")
    username = django_filters.CharFilter(
        field_name='username', lookup_expr='icontains')

    class Meta:
        model = User
        fields = []
