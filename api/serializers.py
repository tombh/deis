"""
Classes to serialize the RESTful representation of Deis API models.
"""

from __future__ import unicode_literals

import re

from django.contrib.auth.models import User
from rest_framework import serializers

from api import models
from api import utils


class OwnerSlugRelatedField(serializers.SlugRelatedField):
    """Filter queries by owner as well as slug_field."""

    def from_native(self, data):
        """Fetch model object from its 'native' representation.
        TODO: request.user is not going to work in a team environment...
        """
        self.queryset = self.queryset.filter(owner=self.context['request'].user)
        return serializers.SlugRelatedField.from_native(self, data)


class UserSerializer(serializers.ModelSerializer):
    """Serialize a :class:`~api.models.User` model."""

    class Meta:
        """Metadata options for a UserSerializer."""
        model = User
        read_only_fields = ('is_superuser', 'is_staff', 'groups',
                            'user_permissions', 'last_login', 'date_joined')

    @property
    def data(self):
        """Custom data property that removes secure user fields"""
        d = super(UserSerializer, self).data
        for f in ('password',):
            if f in d:
                del d[f]
        return d


class AdminUserSerializer(serializers.ModelSerializer):
    """Serialize admin status for a :class:`~api.models.User` model."""

    class Meta:
        model = User
        fields = ('username', 'is_superuser')
        read_only_fields = ('username',)


class KeySerializer(serializers.ModelSerializer):
    """Serialize a :class:`~api.models.Key` model."""

    owner = serializers.Field(source='owner.username')

    class Meta:
        """Metadata options for a KeySerializer."""
        model = models.Key
        read_only_fields = ('created', 'updated')


class ProviderSerializer(serializers.ModelSerializer):
    """Serialize a :class:`~api.models.Provider` model."""

    owner = serializers.Field(source='owner.username')

    class Meta:
        """Metadata options for a ProviderSerializer."""
        model = models.Provider
        read_only_fields = ('created', 'updated')


class FlavorSerializer(serializers.ModelSerializer):
    """Serialize a :class:`~api.models.Flavor` model."""

    owner = serializers.Field(source='owner.username')
    provider = OwnerSlugRelatedField(slug_field='id')

    class Meta:
        """Metadata options for a :class:`FlavorSerializer`."""
        model = models.Flavor
        read_only_fields = ('created', 'updated')


class PushSerializer(serializers.ModelSerializer):
    """Serialize a :class:`~api.models.Push` model."""

    owner = serializers.Field(source='owner.username')
    app = serializers.SlugRelatedField(slug_field='id')

    class Meta:
        """Metadata options for a :class:`PushSerializer`."""
        model = models.Push
        read_only_fields = ('uuid', 'created', 'updated')


class ConfigSerializer(serializers.ModelSerializer):
    """Serialize a :class:`~api.models.Config` model."""

    owner = serializers.Field(source='owner.username')
    app = serializers.SlugRelatedField(slug_field='id')
    values = serializers.ModelField(
        model_field=models.Config()._meta.get_field('values'), required=False)

    class Meta:
        """Metadata options for a :class:`ConfigSerializer`."""
        model = models.Config
        read_only_fields = ('uuid', 'created', 'updated')


class BuildSerializer(serializers.ModelSerializer):
    """Serialize a :class:`~api.models.Build` model."""

    owner = serializers.Field(source='owner.username')
    app = serializers.SlugRelatedField(slug_field='id')

    class Meta:
        """Metadata options for a :class:`BuildSerializer`."""
        model = models.Build
        read_only_fields = ('uuid', 'created', 'updated')


class ReleaseSerializer(serializers.ModelSerializer):
    """Serialize a :class:`~api.models.Release` model."""

    owner = serializers.Field(source='owner.username')
    app = serializers.SlugRelatedField(slug_field='id')
    config = serializers.SlugRelatedField(slug_field='uuid')
    build = serializers.SlugRelatedField(slug_field='uuid', required=False)

    class Meta:
        """Metadata options for a :class:`ReleaseSerializer`."""
        model = models.Release
        read_only_fields = ('uuid', 'created', 'updated')


class FormationSerializer(serializers.ModelSerializer):
    """Serialize a :class:`~api.models.Formation` model."""

    owner = serializers.Field(source='owner.username')

    class Meta:
        """Metadata options for a :class:`FormationSerializer`."""
        model = models.Formation
        read_only_fields = ('created', 'updated')


class LayerSerializer(serializers.ModelSerializer):
    """Serialize a :class:`~api.models.Layer` model."""

    owner = serializers.Field(source='owner.username')
    formation = OwnerSlugRelatedField(slug_field='id')
    flavor = OwnerSlugRelatedField(slug_field='id')

    class Meta:
        """Metadata options for a :class:`LayerSerializer`."""
        model = models.Layer
        read_only_fields = ('created', 'updated')


class NodeSerializer(serializers.ModelSerializer):
    """Serialize a :class:`~api.models.Node` model."""

    owner = serializers.Field(source='owner.username')
    formation = OwnerSlugRelatedField(slug_field='id')
    layer = OwnerSlugRelatedField(slug_field='id')

    class Meta:
        """Metadata options for a :class:`NodeSerializer`."""
        model = models.Node
        read_only_fields = ('created', 'updated')


class AppSerializer(serializers.ModelSerializer):
    """Serialize a :class:`~api.models.App` model."""

    owner = serializers.Field(source='owner.username')
    id = serializers.SlugField(default=utils.generate_app_name)
    formation = serializers.SlugRelatedField(slug_field='id', required=False)

    class Meta:
        """Metadata options for a :class:`AppSerializer`."""
        model = models.App
        read_only_fields = ('created', 'updated')

    def validate_id(self, attrs, source):
        """
        Check that the ID is all lowercase
        """
        value = attrs[source]
        match = re.match(r'^[a-z0-9-]+$', value)
        if not match:
            raise serializers.ValidationError("App IDs can only contain [a-z0-9-]")
        return attrs


class ContainerSerializer(serializers.ModelSerializer):
    """Serialize a :class:`~api.models.Container` model."""

    owner = serializers.Field(source='owner.username')
    formation = OwnerSlugRelatedField(slug_field='id')
    node = OwnerSlugRelatedField(slug_field='id')
    app = OwnerSlugRelatedField(slug_field='id')

    class Meta:
        """Metadata options for a :class:`ContainerSerializer`."""
        model = models.Container
        read_only_fields = ('created', 'updated')


class ServiceSerializer(serializers.ModelSerializer):

    owner = serializers.Field(source='owner.username')
    dashboard = serializers.CharField(required=False)
    docs = serializers.CharField(required=False)

    class Meta:
        model = models.Service
        fields = ('owner', 'type', 'enabled', 'dashboard', 'docs')

    # TODO #231: I don't like this hack. Without it object creation complains about missing
    # dashboard and docs fields.
    def get_validation_exclusions(self):
        exclusions = super(ServiceSerializer, self).get_validation_exclusions()
        return exclusions + ['dashboard', 'docs']


class AddonSerializer(serializers.ModelSerializer):

    app = OwnerSlugRelatedField(slug_field='id')
    owner = serializers.Field(source='owner.username')
    name = serializers.SlugField(default=utils.generate_service_name)
    plan = serializers.SlugField(default='free')
    uri = serializers.CharField(required=False)
    # TODO #231: This doesn't strike me as the most elegant way of including the nested provider
    # data. But using other methods 'depth=1' or 'provider=ServiceSerializer' prevent
    # writing to the AddonSerializer using the Provider type field.
    docs = serializers.CharField(source='provider.docs', required=False)
    dashboard = serializers.CharField(source='provider.dashboard', required=False)

    class Meta:
        model = models.Addon
        fields = ('uri', 'provider', 'app', 'owner', 'name', 'plan', 'docs', 'dashboard')

    # TODO #231: I don't like this hack. Without it Addon.build() can't generate the uri in the
    # pre_save() because Django reports the field as missing.
    def get_validation_exclusions(self):
        exclusions = super(AddonSerializer, self).get_validation_exclusions()
        return exclusions + ['uri']
