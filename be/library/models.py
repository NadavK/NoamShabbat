import os

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _
from gdstorage.storage import GoogleDriveStorage

from devices.models import Group, Device
from library import managers

# Define Google Drive Storage
gd_storage = GoogleDriveStorage()


class Holiday(models.Model):
    class Meta:
        verbose_name = 'חג'
        verbose_name_plural = 'חגים'
    name = models.CharField(max_length=255, verbose_name='חג', help_text='שם החג')
    english_name = models.CharField(max_length=255, verbose_name='Holiday', help_text='In English')

    def __str__(self):
        return self.name


def static_get_upload_path(instance, filename):
    return instance.get_upload_path(filename)


class File(models.Model):
    class Meta:
        # indexes = [
        #     models.Index(fields=['content_type', 'object_id']),
        # ]
        # verbose_name = 'שיר'
        # verbose_name_plural = 'שירים'
        abstract = True

    class Placement(models.TextChoices):
        FIRST = '1', _('ראשון')
        SECOND = '2', _('שני')
        MIDDLE = '3', _('הכרזה')

    #@staticmethod
    def get_upload_path(self, filename):
        return os.path.join('NoamShabbat') #, filename)     # Base path


    file = models.FileField(verbose_name='שם', help_text='שם הקובץ', upload_to=static_get_upload_path, storage=gd_storage)#, related_name="disclaimer_company")
    #name = models.CharField(unique=True, max_length=255, verbose_name='שם', help_text='שם הבקר')
    description = models.CharField(blank=True, max_length=255, verbose_name='תיאור', help_text='תיאור הבקר')
    notes = models.CharField(blank=True, max_length=255, verbose_name='הערות', help_text='הערות על הבקר')
    placement = models.CharField(max_length=1, choices=Placement.choices, verbose_name='מיקום', help_text='מיקום ברשימת נגינה')
    active = models.BooleanField(default=True, verbose_name='פעיל', help_text='פעיל או מושהה')
    deleted = models.BooleanField(default=False, verbose_name='מחוקה', help_text='הבקר מחוקה')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='זמן הוספה',
                                      help_text='הזמן שהבקר התווספה למערכת')
    changed_time = models.DateTimeField(auto_now=True, verbose_name='זמן הגדרות בבקר',
                                              help_text='הזמן האחרון שהגדרות שונו בבקר עצמה')
    # Link to group or device
    # limit = models.Q(app_label='devices', model='devicegroup') | models.Q(app_label='devices', model='device')
    # content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=limit, verbose_name='שיוך', help_text='בקר או קבוצה')
    # object_id = models.PositiveIntegerField()
    # link = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.file.name


class GroupFile(File):
    class Meta:
        verbose_name = 'שיר-קבוצה'
        verbose_name_plural = 'שירי-קבוצה'

    objects = managers.GroupFileManager()

    group_holiday = models.ForeignKey('GroupHoliday', blank=True, null=True, on_delete=models.SET_NULL)

    def get_upload_path(self, filename):
        return os.path.join(super().get_upload_path(filename), 'Groups', str(self.group_holiday.group.pk), filename)


class DeviceFile(File):
    class Meta:
        verbose_name = 'שיר-בקר'
        verbose_name_plural = 'שירי-בקר'

    objects = managers.DeviceFileManager()

    device_holiday = models.ForeignKey('DeviceHoliday', blank=True, null=True, on_delete=models.SET_NULL, verbose_name='חג-בקר')#, help_text='שיוך לבקר')

    def get_upload_path(self, filename):
        return os.path.join(super().get_upload_path(filename), 'Devices', str(self.device_holiday.device.pk), filename)


class GroupHoliday(models.Model):
    class Meta:
        verbose_name = 'קבוצה-חג'
        verbose_name_plural = 'קבוצה-חג'
        constraints = [
            models.UniqueConstraint(fields=['group', 'holiday'], name='unique_group_holiday')
        ]

    objects = managers.GroupHolidayManager()

    group = models.ForeignKey(Group, on_delete=models.PROTECT, verbose_name='קבוצה', help_text='שיוך לקבוצה')
    holiday = models.ForeignKey(Holiday, on_delete=models.PROTECT, verbose_name='חג', help_text='מתי לנגן')

    def __str__(self):
        return "%s - %s" % (self.group, self.holiday)


class DeviceHoliday(models.Model):
    class Meta:
        verbose_name = 'בקר-חג'
        verbose_name_plural = 'בקר-חג'
        constraints = [
            models.UniqueConstraint(fields=['device', 'holiday'], name='unique_device_holiday')
        ]

    objects = managers.DeviceHolidayManager()

    device = models.ForeignKey(Device, on_delete=models.PROTECT, verbose_name='בקר', help_text='שיוך לבקר')
    holiday = models.ForeignKey(Holiday, on_delete=models.PROTECT, verbose_name='חג', help_text='מתי לנגן')
    inherit = models.BooleanField(default=True, verbose_name='לכלול שירי קבוצה', help_text='לשהשמיע שירים מהקבוצה')

    def __str__(self):
        return "%s - %s" % (self.device, self.holiday)
