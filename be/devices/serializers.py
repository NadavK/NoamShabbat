from django.contrib.auth.models import User, Group
from rest_framework import serializers

from be import settings
from devices.models import Device


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = settings.AUTH_USER_MODEL
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class DeviceSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Device
        lookup_field = 'sn'
        fields = ['sn', 'ip', 'name']
        #read_only_fields = ['sn']


    def validate_sn(self, value):
        """
        Check that sn is not empty.
        """
        if not value:
            raise serializers.ValidationError("SN must not be empty.")
        return value


class DeviceHealthSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Device
        lookup_field = 'sn'
        fields = ['sn', 'ip', 'device_config_time', 'last_health_time']
        read_only = ['last_health_time']

    def validate_sn(self, value):
        """
        Check that sn is not empty.
        """
        if not value:
            raise serializers.ValidationError("SN must not be empty.")
        return value

    # def validate_ip(self, value):
    #     # Not called. Not sure why.
    #     """
    #     Check that ip is not empty.
    #     """
    #     if not value:
    #         raise serializers.ValidationError("IP must not be empty.")
    #     return value
