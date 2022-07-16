import logging
from django.utils import timezone

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.http import Http404
from rest_framework import viewsets, mixins
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.viewsets import GenericViewSet

from devices.models import Device
from devices.serializers import UserSerializer, GroupSerializer, DeviceSerializer, DeviceHealthSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = get_user_model().objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class DeviceViewSet(mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    GenericViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'sn'

    def __init__(self, *args, **kwargs):
        # this never seems to get called.
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)
        self.logger.info('************ DeviceViewSet __init__ **********************************')

    def create(self, request):
        raise MethodNotAllowed(request.method)

    def update(self, request, sn=None):
        raise MethodNotAllowed(request.method)

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed(request.method)

    def perform_create(self, serializer):
        serializer.validated_data['last_health_time'] = timezone.now()

        # Set default name
        serializer.validated_data['name'] = 'חדש ' + serializer.validated_data['sn']

        super().perform_create(serializer)

    def perform_update(self, serializer):
        serializer.validated_data['last_health_time'] = timezone.now()
        super().perform_update(serializer)

    # /devices/health with sn in payload
    @action(detail=False, methods=['post'], serializer_class=DeviceHealthSerializer, permission_classes=[permissions.IsAuthenticated])
    def health(self, request, *args, **kwargs):
        try:
            self.kwargs['sn'] = request.data['sn']
            response = super().update(request, *args, **kwargs)
            self.logger.info('Updated: %s', response)
        except Http404:
        #except Device.DoesNotExist:
            self.logger.info('Failed to update, so trying to add: %s', request.data)
            try:
                response = super().create(request, *args, **kwargs)
                self.logger.info('Created %s: %s', response.status_code, response.data['sn'])
            except Exception as e:
                self.logger.exception('Failed to create: %s', request.data)
                raise e
        except Exception as e:
            self.logger.exception('Failed to update: %s', request.data)
            raise e
        return response


from django.shortcuts import render
def geeks_view(request):
    # create a dictionary to pass
    # data to the template
    context ={
        "data":"Gfg is the best",
        "list":[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    }
    # return response with template and context
    return render(request, "geeks.html", context)
