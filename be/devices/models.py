import logging

from django.core.validators import MinLengthValidator
from django.db import models
from devices import managers


class Device(models.Model):
    objects = managers.DeviceManager()

    sn = models.CharField(primary_key=True, null=False, blank=False, max_length=255, verbose_name='מס\'', help_text='מספר סידורי', validators=[MinLengthValidator(1)])
    name = models.CharField(unique=True, max_length=255, verbose_name='שם', help_text='שם היחידה')
    description = models.CharField(blank=True, max_length=255, verbose_name='תיאור', help_text='תיאור היחידה')
    notes = models.CharField(blank=True, max_length=255, verbose_name='הערות', help_text='הערות על היחידה')
    ip = models.GenericIPAddressField(blank=True, null=True, verbose_name='אי.פי.', help_text='כתובת IP של היחידה')
    active = models.BooleanField(default=True, verbose_name='פעיל', help_text='פעיל או מושהה')
    deleted = models.BooleanField(default=False, verbose_name='מחוקה', help_text='היחידה מחוקה')
    added_time = models.DateTimeField(blank=True, null=True, auto_now_add=True, verbose_name='זמן הוספה', help_text='הזמן שהיחידה התווספה למערכת')
    last_reported_time = models.DateTimeField(blank=True, null=True, verbose_name='זמן דיווח אחרון', help_text='הזמן האחרון שהיחידה דווחה על חיבוריות')
    last_config_time = models.DateTimeField(blank=True, null=True, verbose_name='זמן הגדרות אחרון', help_text='הזמן האחרון שהגדרות שונו עבור היחידה')
    device_config_time = models.DateTimeField(blank=True, null=True, verbose_name='זמן הגדרות ביחידה', help_text='הזמן האחרון שהגדרות שונו ביחידה עצמה')

    #updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s (#%s)" % (self.name, self.sn)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)

    # def get_request_id(self, request_id=None, prefix=''):
    #     # prepare request_id
    #     if getattr(local, 'request_id', None):
    #         self.need_to_del_local_request_id = False
    #     else:
    #         self.need_to_del_local_request_id = True
    #         import uuid
    #         local.request_id = request_id or (prefix + uuid.uuid4().hex) #RequestIDMiddleware()._generate_id())
    #     return local.request_id
    #
    # def clear_request_id(self):
    #     if self.need_to_del_local_request_id:
    #         if hasattr(local, 'request_id'):
    #             delattr(local, 'request_id')
    #         else:
    #             self.logger.warning('request_id was not found to clear: %s', self)
