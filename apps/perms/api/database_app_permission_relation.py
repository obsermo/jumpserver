# coding: utf-8
#

from rest_framework import generics
from django.db.models import F, Value
from django.shortcuts import get_object_or_404

from orgs.mixins.api import OrgBulkModelViewSet
from orgs.utils import current_org
from common.permissions import IsOrgAdmin
from .. import models, serializers

__all__ = [
    'DatabaseAppPermissionUserRelationViewSet',
    'DatabaseAppPermissionUserGroupRelationViewSet',
    'DatabaseAppPermissionAllUserListApi',
]


class RelationMixin(OrgBulkModelViewSet):
    def get_queryset(self):
        queryset = self.model.objects.all()
        org_id = current_org.org_id()
        if org_id is not None:
            queryset = queryset.filter(databaseapppermission__org_id=org_id)
        queryset = queryset.annotate(databaseapppermission_display=F('databaseapppermission__name'))
        return queryset


class DatabaseAppPermissionUserRelationViewSet(RelationMixin):
    serializer_class = serializers.DatabaseAppPermissionUserRelationSerializer
    model = models.DatabaseAppPermission.users.through
    permission_classes = (IsOrgAdmin,)
    filterset_fields = [
        'id', 'user', 'databaseapppermission'
    ]
    search_fields = ('user__name', 'user__username', 'databaseapppermission__name')

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(user_display=F('user__name'))
        return queryset


class DatabaseAppPermissionUserGroupRelationViewSet(RelationMixin):
    serializer_class = serializers.DatabaseAppPermissionUserGroupRelationSerializer
    model = models.DatabaseAppPermission.user_groups.through
    permission_classes = (IsOrgAdmin,)
    filterset_fields = [
        'id', "usergroup", "databaseapppermission"
    ]
    search_fields = ["usergroup__name", "databaseapppermission__name"]

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset \
            .annotate(usergroup_display=F('usergroup__name'))
        return queryset


class DatabaseAppPermissionAllUserListApi(generics.ListAPIView):
    permission_classes = (IsOrgAdmin,)
    serializer_class = serializers.DatabaseAppPermissionAllUserSerializer
    filter_fields = ("username", "name")
    search_fields = filter_fields

    def get_queryset(self):
        pk = self.kwargs.get("pk")
        perm = get_object_or_404(models.DatabaseAppPermission, pk=pk)
        users = perm.get_all_users().only(
            *self.serializer_class.Meta.only_fields
        )
        return users
