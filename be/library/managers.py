from django.db import models
import logging


class GroupFileManager(models.Manager):
    logger = logging.getLogger(__name__)


class DeviceFileManager(models.Manager):
    logger = logging.getLogger(__name__)


class GroupHolidayManager(models.Manager):
    logger = logging.getLogger(__name__)


class DeviceHolidayManager(models.Manager):
    logger = logging.getLogger(__name__)
