from django.db import models
import logging


class DeviceManager(models.Manager):
    logger = logging.getLogger(__name__)
