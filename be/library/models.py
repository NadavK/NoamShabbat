from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.forms import forms
from django.utils.translation import gettext_lazy as _

from devices.models import Group, Device
from library import managers


class Holiday(models.Model):
    class Meta:
        verbose_name = 'חג'
        verbose_name_plural = 'חגים'
    name = models.CharField(max_length=255, verbose_name='חג', help_text='שם החג')
    english_name = models.CharField(max_length=255, verbose_name='Holiday', help_text='In English')

    def __str__(self):
        return self.name


class InheritGroupFilesPerHoliday(models.Model):
    class Meta:
        verbose_name = 'השמעת שירים מהקבוצה'
        verbose_name_plural = 'השמעת שירים מהקבוצה'

    holiday = models.ForeignKey(Holiday, on_delete=models.PROTECT, verbose_name='חג', help_text='מתי לנגן')
    device = models.ForeignKey(Device, on_delete=models.PROTECT, verbose_name='בקר', help_text='בקר')
    inherit = models.BooleanField(default=True, verbose_name='לכלול שירי קבוצה', help_text='לשהשמיע שירים מהקבוצה')


class File(models.Model):
    class Meta:
        # indexes = [
        #     models.Index(fields=['content_type', 'object_id']),
        # ]
        verbose_name = 'שיר'
        verbose_name_plural = 'שירים'


    class Placement(models.TextChoices):
        FIRST = '1', _('ראשון')
        SECOND = '2', _('שני')
        MIDDLE = '3', _('הכרזה')

    file = models.FileField(verbose_name='שם', help_text='שם הקובץ')#, related_name="disclaimer_company")
    #name = models.CharField(unique=True, max_length=255, verbose_name='שם', help_text='שם הבקר')
    description = models.CharField(blank=True, max_length=255, verbose_name='תיאור', help_text='תיאור הבקר')
    notes = models.CharField(blank=True, max_length=255, verbose_name='הערות', help_text='הערות על הבקר')
    #holiday = models.ForeignKey(Holiday, on_delete=models.PROTECT, verbose_name='חג', help_text='מתי לנגן')
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

    #group = models.ForeignKey(Group, on_delete=models.PROTECT, verbose_name='קבוצה', help_text='שיוך לקבוצה')
    group_holiday = models.OneToOneField('GroupHolidayFile', blank=True, null=True, on_delete=models.SET_NULL)


class DeviceFile(File):
    class Meta:
        verbose_name = 'שיר-בקר'
        verbose_name_plural = 'שירי-בקר'

    objects = managers.DeviceFileManager()

    #device = models.ForeignKey(Device, on_delete=models.PROTECT, verbose_name='בקר', help_text='שיוך לבקר')
    device_holiday = models.OneToOneField('DeviceHolidayFile', blank=True, null=True, on_delete=models.SET_NULL, verbose_name='חג-בקר')#, help_text='שיוך לבקר')


class GroupHolidayFile(models.Model):
    class Meta:
        verbose_name = 'קבוצה-שיר-חג'
        verbose_name_plural = 'קבוצה-שיר-חג'

    objects = managers.GroupHolidayManager()

    group = models.ForeignKey(Group, on_delete=models.PROTECT, verbose_name='קבוצה', help_text='שיוך לקבוצה')
    holiday = models.ForeignKey(Holiday, on_delete=models.PROTECT, verbose_name='חג', help_text='מתי לנגן')
    #group_file = models.OneToOneField(GroupFile, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='שיר-בקר')#, help_text='שיוך לבקר')

    def __str__(self):
        return "%s - %s" % (self.group, self.holiday)


class DeviceHolidayFile(models.Model):
    class Meta:
        verbose_name = 'בקר-שיר-חג'
        verbose_name_plural = 'בקר-שיר-חג'

    #unique_together = ['device', 'holiday']

    objects = managers.DeviceHolidayManager()

    device = models.ForeignKey(Device, on_delete=models.PROTECT, verbose_name='בקר', help_text='שיוך לבקר')
    holiday = models.ForeignKey(Holiday, on_delete=models.PROTECT, verbose_name='חג', help_text='מתי לנגן')
    #device_file = models.OneToOneField(DeviceFile, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='שיר-בקר')#, help_text='שיוך לבקר')

    def __str__(self):
        return "%s - %s" % (self.device, self.holiday)


#
#
#
# from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
# class Song(models.Model):
#     name = models.CharField(max_length=255)
#     content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
#     object_id = models.PositiveIntegerField()
#     content_object = GenericForeignKey()        #'content_type', 'object_id'
#
# class Album(models.Model):
#     name = models.CharField(max_length=255)
#     songs = GenericRelation(Song)
#
# class DVD(models.Model):
#     name = models.CharField(max_length=255)
#     songs = GenericRelation(Song)
#
# #from myproject.generic import GenericTabularInline
# from django.contrib import admin
# # #from django.contrib.contenttypes.admin import GenericTabularInline
# # from genericadmin.admin import GenericAdminModelAdmin, TabularInlineWithGeneric, GenericTabularInline
#
#
# # class SongInline(TabularInlineWithGeneric):
# # #class SongInline(TabularInlineWithGeneric):
# #     model = Song
# #     extra = 2
# #     ct_field_name = 'content_type'
# #     id_field_name = 'object_id'
# #
# # @admin.register(Album)
# # class AlbumAdmin(GenericAdminModelAdmin):
# #     inlines = (SongInline,)
# #
# # @admin.register(DVD)
# # class DVDAdmin(GenericAdminModelAdmin):
# #     inlines = (SongInline,)
# #
# # admin.site.register(Song)
# # class SongAdmin(GenericAdminModelAdmin):
# #     pass
# #
#
#
#
#
#
#
#
#
#
#
#
#
#
# class Org(models.Model):
#     name = models.CharField(max_length=255)
#     #student = GenericRelation(Song)
#
#
#
#
#
#
#
# from django.contrib.contenttypes import fields
# from django.contrib.contenttypes.models import ContentType
# from django.db import models
# from django.db.models import Q
#
# CONTENT_TYPE_CHOICES = (
#   Q(app_label='org', model='org') |
#   Q(app_label='institution', model='institution') |
#   Q(app_label='campus', model='campus')
# )
#
# class StudentSolution(models.Model):
#   # Dynamic relationship to either Org, Institution or Campus entities
#   # XXX https://simpleisbetterthancomplex.com/tutorial/2016/10/13/how-to-use-generic-relations.html
#   content_type = models.ForeignKey(
#     ContentType,
#     on_delete=models.CASCADE,  # TODO check if good thing
#     limit_choices_to=CONTENT_TYPE_CHOICES,
#   )
#   object_id = models.PositiveIntegerField()
#   content_object = fields.GenericForeignKey(
#     'content_type',
#     'object_id'
#   )
#
#
#
#
#
#
#
# from django import forms
# from django.contrib.contenttypes.models import ContentType
#
#
#
# class StudentSolutionAdminForm(forms.ModelForm):
#   class Meta:
#     model = StudentSolution
#     fields = '__all__'  # Keep all fields
#
# class GenericStudentSolutionOwnerChoicesFieldForm(forms.ModelForm):
#   ct_place_type = ContentType.objects.get_for_model(Org)  # TODO not sure at all about that, should be either of 3 related ContentTypes (Org | Institution | Campus)
#
#   object_id = forms.ModelChoiceField(
#     Org.objects.all(),
#     limit_choices_to=CONTENT_TYPE_CHOICES,
#     label='Student solution'
#   )
#   content_type = forms.ModelChoiceField(
#     ContentType.objects.all(),
#     initial=ct_place_type,
#     limit_choices_to=CONTENT_TYPE_CHOICES,  # should I use this here?
#     widget=forms.HiddenInput()
#   )
#
#   def clean_object_id(self):
#     return self.cleaned_data['object_id'].pk
#
#   def clean_content_type(self):
#     return self.ct_place_type
#
#
#
#
#
# from django.contrib import admin
#
# # class StudentSolutionInlineAdmin(admin.TabularInline):
# #     form = GenericStudentSolutionOwnerChoicesFieldForm
# #     model = Org  # TODO not sure at all about that, should be either of 3 related ContentTypes (Org | Institution | Campus)
# #     # This throw error "<class 'tfp_backoffice.apps.student_solution.admin.StudentSolutionInlineAdmin'>: (admin.E202) 'org.Org' has no ForeignKey to 'student_solution.StudentSolution'."
# from django.contrib import admin
# from django.contrib.contenttypes.admin import GenericTabularInline
# from django import forms
#
#
# class StudentSolutionInlineAdmin(GenericTabularInline):
#     model = StudentSolution
#     extra = 1
#
#
# class StudentSolutionAdminForm(forms.ModelForm):
#     class Meta:
#         model = StudentSolution
#         fields = '__all__'  # Keep all fields
#
#
# @admin.register(Org)
# class OrgAdmin(admin.ModelAdmin):
#     form = StudentSolutionAdminForm
#     inlines = [StudentSolutionInlineAdmin]
#
#
# class StudentSolutionAdmin(admin.ModelAdmin):
#     form = StudentSolutionAdminForm
#     inlines = [
#         StudentSolutionInlineAdmin,
#     ]
# admin.site.register(StudentSolution, StudentSolutionAdmin)
#
#
#
#
#
