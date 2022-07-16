import logging

from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MinLengthValidator
from django.db import models
from devices import managers


class DeviceGroup(models.Model):
    class Meta:
        verbose_name = 'קבוצה'
        verbose_name_plural = 'קבוצות'

    name = models.CharField(unique=True, max_length=255, verbose_name='שם', help_text='שם הקבוצה')
    description = models.CharField(blank=True, max_length=255, verbose_name='תיאור', help_text='תיאור הקבוצה')
    notes = models.CharField(blank=True, max_length=255, verbose_name='הערות', help_text='הערות על הקבוצה')
    # created_time = models.DateTimeField(blank=True, null=True, auto_now_add=True, verbose_name='זמן הוספה', help_text='הזמן שהבקר התווספה למערכת')
    # changed_time = models.DateTimeField(auto_now=True, verbose_name='זמן שינוי', help_text='הזמן האחרון ששונו הגדרות')
    #files = GenericRelation(File)

    def __str__(self):
        return self.name


class Device(models.Model):
    class Meta:
        verbose_name = 'בקר'
        verbose_name_plural = 'בקרים'

    objects = managers.DeviceManager()

    sn = models.CharField(null=False, blank=False, max_length=255, verbose_name='מס\'', help_text='מספר סידורי', validators=[MinLengthValidator(1)])
    name = models.CharField(unique=True, max_length=255, verbose_name='שם', help_text='שם הבקר')
    description = models.CharField(blank=True, max_length=255, verbose_name='תיאור', help_text='תיאור הבקר')
    notes = models.CharField(blank=True, max_length=255, verbose_name='הערות', help_text='הערות על הבקר')
    ip = models.GenericIPAddressField(blank=True, null=True, verbose_name='אי.פי.', help_text='כתובת IP של הבקר')
    active = models.BooleanField(default=True, verbose_name='פעיל', help_text='פעיל או מושהה')
    deleted = models.BooleanField(default=False, verbose_name='מחוקה', help_text='הבקר מחוקה')
    created_time = models.DateTimeField(blank=True, null=True, auto_now_add=True, verbose_name='זמן הוספה', help_text='הזמן שהבקר התווספה למערכת')
    changed_time = models.DateTimeField(auto_now=True, verbose_name='זמן שינוי', help_text='הזמן האחרון ששונו הגדרות')
    config_time = models.DateTimeField(blank=True, null=True, verbose_name='זמן הגדרות', help_text='הזמן האחרון ששונו הגדרות המשפיות על הבקר')
    device_config_time = models.DateTimeField(blank=True, null=True, verbose_name='זמן הגדרות בבקר', help_text='הזמן של הגדרות בבקר עצמה')
    reported_device_config_time = models.DateTimeField(blank=True, null=True, verbose_name='זמן קבלה אחרון', help_text='הזמן שהבקר דיווחה על קבלת ההגדרות')
    last_health_time = models.DateTimeField(blank=True, null=True, verbose_name='זמן דיווח אחרון', help_text='הזמן האחרון שהבקר דווחה על חיבוריות')
    group = models.ForeignKey(DeviceGroup, blank=True, null=True, on_delete=models.PROTECT, verbose_name='קבוצה', help_text='קבוצה של בקרים')
    #files = models.ForeignKey(DeviceGroup, blank=True, null=True, on_delete=models.PROTECT, verbose_name='קבוצה', help_text='קבוצה של בקרים')

    #files = GenericRelation(File)

    @property
    def id(self):
        return self.sn

    def __str__(self):
        return "%s (#%s)" % (self.name, self.sn)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)

    @property
    def merged_files(self):
        return self.files | self.group.files

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

    @classmethod
    def realtime(cls, id, user, amount, deposited_by, reference, reference_type, comment):
        pass
