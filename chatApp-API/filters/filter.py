import django_filters
from userApp.models import User


class UserSearchFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(
        field_name='username', lookup_expr='icontains')

    print("username : ", username)

    class Meta:
        model = User
        fields = []
