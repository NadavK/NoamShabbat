from django.contrib import admin
from django.contrib.admin import StackedInline, TabularInline
from library.models import File, DeviceFile, GroupFile, Holiday, GroupHoliday, DeviceHoliday


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


# class DeviceHolidayInline(StackedInline):
#     model = DeviceHoliday
#     fields = ('holiday',)
#     #readonly_fields = ('device', )
#     can_delete = False


# class GroupHolidayInline(StackedInline):
#     model = GroupHoliday
#     fields = ('holiday',)
#     #readonly_fields = ('group', )
#     can_delete = False
#
#     # list_display = ('pk', 'file', 'description', 'device_holiday__device', 'device_holiday__holiday', 'placement', 'active', 'deleted', 'created_time', 'changed_time')
#     # ordering = ('device_holiday__device', 'device_holiday__holiday', 'placement')
#
#     # @admin.display(description='בקר', ordering='device_holiday__device')
#     # def device_holiday__device(self, obj):
#     #     return obj.device_holiday.device.name
#     #
#     # @admin.display(description='חג', ordering='device_holiday__holiday')
#     # def device_holiday__holiday(self, obj):
#     #     return obj.device_holiday.holiday.name


@admin.register(Holiday)
class HolidayAdmin(OnlySuperModelAdmin):
    list_display = ('name',)
    ordering = ('pk',)


@admin.register(DeviceFile)
class DeviceFileAdmin(OnlySuperModelAdmin):
    class Media:
        css = {
            'all': ('admin/css/admin-inline-notitle.css', )     # Hide title
        }
    list_display = ('pk', 'file', 'description', 'device_holiday__device', 'device_holiday__holiday', 'placement', 'active', 'deleted', 'created_time', 'changed_time')
    ordering = ('device_holiday__device', 'device_holiday__holiday', 'placement')
    #readonly_fields = ('device_holiday',)

    @admin.display(description='בקר', ordering='device_holiday__device')
    def device_holiday__device(self, obj):
        try:
            return obj.device_holiday.device.name
        except:
            return 'Missing'

    @admin.display(description='חג', ordering='device_holiday__holiday')
    def device_holiday__holiday(self, obj):
        try:
            return obj.device_holiday.holiday.name
        except:
            return 'Missing'


@admin.register(GroupFile)
class GroupFileAdmin(OnlySuperModelAdmin):
    class Media:
        css = {
            'all': ('admin/css/admin-inline-notitle.css', )     # Hide title
        }
    list_display = ('pk', 'file', 'description', 'group_holiday__group', 'group_holiday__holiday', 'placement', 'active', 'deleted', 'created_time', 'changed_time')
    ordering = ('group_holiday__group', 'group_holiday__holiday', 'placement')
    #readonly_fields = ('group_holiday',)

    @admin.display(description='קבוצה', ordering='group_holiday__group')
    def group_holiday__group(self, obj):
        return obj.group_holiday.group.name

    @admin.display(description='חג', ordering='group_holiday__holiday')
    def group_holiday__holiday(self, obj):
        return obj.group_holiday.holiday.name

    #readonly_fields = ('content_type', 'object_id')
    # form = FileAdmindForm  # <- ADDED FORM

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "content_type":
    #         return CustomContentTypeChoiceField(queryset=Device.objects, **kwargs)
    #     return super(FileAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class DeviceFileInline(TabularInline):
    model = DeviceFile
    can_delete = False
    extra = 1


@admin.register(DeviceHoliday)
class DeviceHolidayAdmin(OnlySuperModelAdmin):
    list_display = ('__str__', 'device', 'holiday', 'has_file')
    ordering = ('device', 'holiday')
    inlines = [DeviceFileInline]

    @admin.display(description='קבצים', ordering='devicefile__file')
    def has_file(self, obj):
        return obj.devicefile_set.count()


class GroupFileInline(TabularInline):
    model = GroupFile
    can_delete = False
    extra = 1


@admin.register(GroupHoliday)
class GroupHolidayAdmin(OnlySuperModelAdmin):
    list_display = ('__str__', 'group', 'holiday', 'has_file')
    ordering = ('group', 'holiday')
    inlines = [GroupFileInline]

    @admin.display(description='קבצים', ordering='groupfile__file')
    def has_file(self, obj):
        return obj.groupfile_set.count()
