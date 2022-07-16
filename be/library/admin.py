from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.contenttypes.models import ContentType
from django import forms
from django.forms import ModelChoiceField

from devices.models import DeviceGroup, Device
from library.models import File, DeviceFile, DeviceGroupFile, Holiday, InheritDeviceGroupFilesPerHoliday, \
    DeviceGroupHoliday, DeviceHoliday


class OnlySuperModelAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        if request.user.is_superuser:
            return super().get_model_perms(request)
        else:
            return {}

# class FileAdmindForm(forms.ModelForm):
#     ct_place_type = ContentType.objects.get_for_model(File)
#
#     object_id = 11#forms.ModelChoiceField(File.objects.all(), label='places')
#     content_type = forms.ModelChoiceField(ContentType.objects.all(), initial=ct_place_type, widget=forms.HiddenInput())
#
#     def clean_object_id(self):
#         return self.cleaned_data['object_id'].pk + 1
#
#     def clean_content_type(self):
#         return self.ct_place_type

# class CustomContentTypeChoiceField(ModelChoiceField):
#     def label_from_instance(self, obj):
#         return obj.name


@admin.register(File)
class FileAdmin(OnlySuperModelAdmin):
    list_display = ('pk', 'file', 'description', 'placement', 'active', 'deleted', 'created_time', 'changed_time')
    pass


@admin.register(Holiday)
class HolidayAdmin(OnlySuperModelAdmin):
    list_display = ('name',)
    ordering = ('pk',)


@admin.register(DeviceFile)
class DeviceFileAdmin(OnlySuperModelAdmin):
    list_display = ('pk', 'file', 'description', 'device_holiday__device', 'device_holiday__holiday', 'placement', 'active', 'deleted', 'created_time', 'changed_time')
    ordering = ('device_holiday__device', 'device_holiday__holiday', 'placement')

    @admin.display(description='בקר', ordering='device_holiday__device')
    def device_holiday__device(self, obj):
        return obj.device_holiday.device.name

    @admin.display(description='חג', ordering='device_holiday__holiday')
    def device_holiday__holiday(self, obj):
        return obj.device_holiday.holiday.name


@admin.register(DeviceGroupFile)
class DeviceGroupFileAdmin(OnlySuperModelAdmin):
    list_display = ('pk', 'file', 'description', 'group_holiday__group', 'group_holiday__holiday', 'placement', 'active', 'deleted', 'created_time', 'changed_time')
    ordering = ('device_group_holiday__group', 'device_group_holiday__holiday', 'placement')

    @admin.display(description='קבוצה', ordering='device_group_holiday__group')
    def group_holiday__group(self, obj):
        return obj.device_group_holiday.group.name

    @admin.display(description='חג', ordering='device_group_holiday__holiday')
    def group_holiday__holiday(self, obj):
        return obj.device_group_holiday.holiday.name



    #readonly_fields = ('content_type', 'object_id')
    # form = FileAdmindForm  # <- ADDED FORM

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "content_type":
    #         return CustomContentTypeChoiceField(queryset=Device.objects, **kwargs)
    #     return super(FileAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)



@admin.register(DeviceHoliday)
class DeviceHolidayAdmin(OnlySuperModelAdmin):
    pass


@admin.register(DeviceGroupHoliday)
class DeviceGroupHolidayAdmin(OnlySuperModelAdmin):
    pass


@admin.register(InheritDeviceGroupFilesPerHoliday)
class DeviceFileAdmin(OnlySuperModelAdmin):
    pass
