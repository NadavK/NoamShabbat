from django.db import models
import logging


class DeviceGroupFileManager(models.Manager):
    logger = logging.getLogger(__name__)


class DeviceFileManager(models.Manager):
    logger = logging.getLogger(__name__)


class DeviceGroupHolidayManager(models.Manager):
    logger = logging.getLogger(__name__)


class DeviceHolidayManager(models.Manager):
    logger = logging.getLogger(__name__)
