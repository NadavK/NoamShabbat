from abc import ABC
from itertools import chain

from django.contrib import admin
from django.contrib.admin import TabularInline
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models import FilteredRelation, Prefetch, F, Value, CharField, BigIntegerField
from django.forms import BaseInlineFormSet
from django.http import HttpResponseRedirect
from django.template.defaulttags import url
from django.template.response import TemplateResponse
from django.urls import reverse, path, resolve
from django.utils.html import format_html_join, format_html
from django.utils.safestring import mark_safe
#from nonrelated_inlines.admin import NonrelatedTabularInline
#from nested_inline.admin import NestedStackedInline, NestedModelAdmin, NestedTabularInline
from nested_admin.nested import NestedModelAdmin, NestedStackedInline, NestedTabularInline

from devices.forms import DeviceRealtimeForm
from devices.models import Device, DeviceGroup
from library.models import File, DeviceFile, DeviceGroupFile, Holiday, InheritDeviceGroupFilesPerHoliday, \
    DeviceGroupHoliday


class DeviceGroupInline(TabularInline):
    model = DeviceGroup
    extra = 1


class DeviceGroupFileInline(TabularInline):
    model = DeviceGroupFile
    extra = 1
    # def get_formset(self, request, obj=None, **kwargs):
    #     return super().get_formset(request, obj, kwargs)


class DeviceFileInlineFormSet(BaseInlineFormSet):

    def get_queryset(self):
        #return super().get_queryset()
        #return qs.filter(<custom query filters>)
        # j = Holiday.objects.annotate(
        #     files=FilteredRelation('name')  )#.values('file__name'))  # e.g. 'user__id', 'filtered_foo__id'
        # return j

        b_qs = DeviceFile.objects.all()
        a_qs = Holiday.objects.all().prefetch_related(
            Prefetch('b_set',
                            # NOTE: no need to filter with OuterRef (it wont work anyway)
                            # Django automatically filter and matches B objects to A
                            queryset=b_qs,
                            to_attr='b_records'
                            )
        )
        xx = a_qs.values()


        from django.db.models import OuterRef, Subquery
        devicefiles = DeviceFile.objects.filter(holiday__pk=OuterRef('pk'))
        extended_holidays = Holiday.objects.annotate(devicefiles=Subquery(devicefiles.values('file')))
        x = extended_holidays.values()
        return extended_holidays


class DeviceFileInline(TabularInline):
    model = DeviceFile
    extra = 1
    show_change_link = True
    # def get_formset(self, request, obj=None, **kwargs):
    #     return super().get_formset(request, obj, kwargs)
    #fields = ('groupfile', 'file', 'description', 'notes', 'holiday', 'placement', 'active', 'override')
    fields = ('holiday', 'placement', 'groupfile', 'file', 'active')
    readonly_fields = ('groupfile', 'holiday', 'placement')
    #formset = DeviceFileInlineFormSet

    def groupfile(self, obj):
        devicefiles = DeviceFile.objects.filter(holiday=obj.holiday, placement=obj.placement)
        return devicefiles.values_list('file')

# class MergedFileInline(admin.TabularInline):
#     model = File




# class ModelNameInlineFormSet(BaseInlineFormSet):
#     def __init__(self, **kwargs):
#         super(ModelNameInlineFormSet, self).__init__(**kwargs)
#         self.queryset = File.objects.none()

# class ModelNameInline(admin.TabularInline):
#     formset = inlineformset_factory(Device, File,
#                                     formset=ModelNameInlineFormSet)



class DeviceGroupFileInlineNonRelated(NestedTabularInline):
    model = DeviceGroupFile
    extra = 0
    exclude = ('group', 'holiday')

    def get_form_queryset(self, obj):
        return self.model.objects.filter(holiday=obj, group__pk=obj.devicegroup_pk)

    def save_new_instance(self, parent, instance):
        # instance.email = parent.email
        pass


# class DeviceFileInlineNonRelated(NestedTabularInline, NonrelatedTabularInline):
#     model = DeviceFile
#     extra = 0
#     exclude = ('device', 'holiday')
#
#     def get_form_queryset(self, obj):
#         return self.model.objects.filter(holiday=obj, device__pk=obj.device_pk)
#
#     def save_new_instance(self, parent, instance):
#         # instance.email = parent.email
#         pass


class InheritDeviceGroupFilesPerHolidayInlineNested(NestedStackedInline):
    model = InheritDeviceGroupFilesPerHoliday
    extra = 1
    max_num = 1
    exclude = ('device',)

    def has_add_permission(self, request, obj=None):
        return True

    def get_form_queryset(self, obj):
        return self.model.objects.filter(holiday=obj, device__pk=obj.device_pk)

    def save_new_instance(self, parent, instance):
        # instance.email = parent.email
        pass


class HolidayInline(NestedStackedInline):
    model = DeviceGroupHoliday


class HolidayInline(NestedStackedInline):
    model = Holiday
    exclude = ('name', 'english_name')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def save_new_instance(self, parent, instance):
        # instance.email = parent.email
        pass

class DeviceGroupHoliday2(DeviceGroupHoliday):
    class Meta:
        proxy = True
        verbose_name = ''
        verbose_name_plural = ''

class DeviceGroupHolidayInline(NestedStackedInline):
    @admin.display(description='')
    def holiday_nolink(self, obj):
        return format_html(
            '<b style="font-weight: bold;font-size: large;">{}</b>',
            obj.holiday.name
        )

    model = DeviceGroupHoliday2
    inlines = [DeviceGroupFileInlineNonRelated]
    can_delete = False
    #readonly_fields = ('holiday_nolink', )
    exclude = ('holiday',)
    list_display_links = ('None',)
    is_sortable = False


    # def get_list_display_links(self, request, list_display):
    #     return (None,)
    #
    # def has_add_permission(self, request, obj=None):
    #     return False

    # def get_form_queryset(self, obj):
    #     return self.model.objects.all().annotate(devicegroup_pk=Value(obj.pk, output_field=BigIntegerField()))

    def get_parent_object_from_request(self, request):
        """
        Returns the parent object from the request or None.

        Note that this only works for Inlines, because the `parent_model`
        is not available in the regular admin.ModelAdmin as an attribute.
        """
        resolved = resolve(request.path_info)
        if resolved.kwargs:
            return self.parent_model.objects.get(pk=resolved.kwargs["object_id"])
        return None

    def get_queryset(self, request):
        if request.method == 'POST':
            return super().get_queryset(request)

        parent = self.get_parent_object_from_request(request)
        existing_holidays = DeviceGroupHoliday.objects.values('holiday').distinct()
        device_group_holidays = []
        for holiday in Holiday.objects.all():
            if holiday not in existing_holidays:
                device_group_holiday = DeviceGroupHoliday(holiday=holiday, group=parent)
                device_group_holidays.append(device_group_holiday)
        device_group_holidays = DeviceGroupHoliday.objects.bulk_create(device_group_holidays)

        # files = []
        # for file in DeviceGroupFile.objects.filter(group=parent):
        #     file.device_group_holiday = DeviceGroupHoliday.objects.get(holiday=file.holiday, group=parent)
        #     files.append(file)
        # DeviceGroupFile.objects.bulk_update(files, ['device_group_holiday'])

        return DeviceGroupHoliday.objects.all()
        #return device_group_holidays
        # super().get_queryset(request)

    # def get_search_results(self, request, queryset, search_term):
    #     queryset, may_have_duplicates = super().get_search_results(
    #         request, queryset, search_term,
    #     )
    #     try:
    #         search_term_as_int = int(search_term)
    #     except ValueError:
    #         pass
    #     else:
    #         queryset |= self.model.objects.filter(age=search_term_as_int)
    #     return queryset, may_have_duplicates


# class HolidayDeviceInline(HolidayInline):
#     inlines = [DeviceGroupFileInlineNonRelated, InheritDeviceGroupFilesPerHolidayInlineNested, DeviceFileInlineNonRelated]
#
#     def get_form_queryset(self, obj):
#         return self.model.objects.all().annotate(device_pk=Value(obj.pk, output_field=BigIntegerField())).annotate(devicegroup_pk=Value(obj.group.pk, output_field=BigIntegerField()))


@admin.register(DeviceGroup)
class DeviceGroupAdmin(NestedModelAdmin):
    model = DeviceGroup
    list_display = ('name', 'description')
    inlines = [DeviceGroupHolidayInline]
    #readonly_fields = ('created_time', 'changed_time')


    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)
    #     return qs



@admin.register(Device)
class DeviceAdmin(NestedModelAdmin):
    list_display = ('sn', 'name', 'button', 'ip', 'active', 'created_time', 'config_time', 'device_config_time', 'reported_device_config_time', 'last_health_time')
    #fields = ('sn', 'name')
    #inlines = [HolidayDeviceInline]#, DeviceFileInlineNonRelated]#[DeviceFileInline]#, FileInline]#, DeviceGroupInline]
    readonly_fields = ('created_time', 'changed_time', 'config_time', 'device_config_time', 'reported_device_config_time', 'last_health_time')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                r'<path:object_id>/realtime/',
                self.admin_site.admin_view(self.process_realtime),
                name='device-realtime',
            ),
        ]
        return custom_urls + urls

    def button(self, obj):
        # return format_html(mark_safe(
        #     "<button onclick=`doSomething({})`>{}</button>"),
        #     obj.id,
        #     'פרטים'
        # )
        return format_html(mark_safe(
            '<a class="button" href="{}">פרטים</a>&nbsp;'),
            reverse('admin:device-realtime', args=[obj.pk]),
        )
    button.short_description = 'פרטים'

    def process_realtime(self, request, object_id, *args, **kwargs):
        device = self.get_object(request, object_id)

        if request.method != 'POST':
            form = DeviceRealtimeForm
        else:
            form = DeviceRealtimeForm(request.POST)
            if form.is_valid():
                # try:
                    form.save(device, request.user)
                # except errors.Error as e:
                #     # If save() raised, the form will a have a non
                #     # field error containing an informative message.
                #     pass
                # else:
                    self.message_user(request, 'Success')
                    url = reverse(
                        'admin:device_list',
                        args=[device.pk],
                        current_app=self.admin_site.name,
                    )
                    return HttpResponseRedirect(url)

        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta
        context['form'] = form
        context['device'] = device
        context['title'] = 'realtime'

        #json_str = '''{"2022-06-17":{"candlelight":"2022-06-17T19:28:56","folders":["Shelah Leha","Shabbat"],"start_music":"2022-06-17T19:08:56","sunset":"2022-06-17T19:48:56"},"2022-06-24":{"candlelight":"2022-06-24T19:30:29","folders":["Korah","Shabbat"],"start_music":"2022-06-24T19:10:29","sunset":"2022-06-24T19:50:29"},"2022-07-01":{"candlelight":"2022-07-01T19:30:53","folders":["Hukath","Shabbat"],"start_music":"2022-07-01T19:10:53","sunset":"2022-07-01T19:50:53"},"2022-07-08":{"candlelight":"2022-07-08T19:30:02","folders":["Balak","Shabbat"],"start_music":"2022-07-08T19:10:02","sunset":"2022-07-08T19:50:02"},"2022-07-15":{"candlelight":"2022-07-15T19:27:56","folders":["ShloshetShavuot","Pinhas","Shabbat"],"start_music":"2022-07-15T19:07:56","sunset":"2022-07-15T19:47:56"},"2022-07-22":{"candlelight":"2022-07-22T19:24:34","folders":["ShloshetShavuot","Matoth","Shabbat"],"start_music":"2022-07-22T19:04:34","sunset":"2022-07-22T19:44:34"},"2022-07-29":{"candlelight":"2022-07-29T19:20:01","folders":["ShloshetShavuot","Maseh","Shabbat"],"start_music":"2022-07-29T19:00:01","sunset":"2022-07-29T19:40:01"},"2022-08-05":{"candlelight":"2022-08-05T19:14:22","folders":["Tisha BAv","Debarim, Shabbat Hazon","Shabbat"],"start_music":"2022-08-05T18:54:22","sunset":"2022-08-05T19:34:22"},"2022-08-12":{"candlelight":"2022-08-12T19:07:45","folders":["Vaethanan, Shabbat Nahamu","Shabbat"],"start_music":"2022-08-12T18:47:45","sunset":"2022-08-12T19:27:45"},"2022-08-19":{"candlelight":"2022-08-19T19:00:18","folders":["Ekeb","Shabbat"],"start_music":"2022-08-19T18:40:18","sunset":"2022-08-19T19:20:18"},"2022-08-26":{"candlelight":"2022-08-26T18:52:09","folders":["Reeh","Shabbat"],"start_music":"2022-08-26T18:32:09","sunset":"2022-08-26T19:12:09"},"2022-09-02":{"candlelight":"2022-09-02T18:43:29","folders":["Shofetim","Shabbat"],"start_music":"2022-09-02T18:23:29","sunset":"2022-09-02T19:03:29"},"2022-09-09":{"candlelight":"2022-09-09T18:34:26","folders":["Ki Tetse","Shabbat"],"start_music":"2022-09-09T18:14:26","sunset":"2022-09-09T18:54:26"},"2022-09-16":{"candlelight":"2022-09-16T18:25:09","folders":["Ki Tabo","Shabbat"],"start_music":"2022-09-16T18:05:09","sunset":"2022-09-16T18:45:09"},"2022-09-23":{"candlelight":"2022-09-23T18:15:49","folders":["Nitsabim","Shabbat"],"start_music":"2022-09-23T17:55:49","sunset":"2022-09-23T18:35:49"},"2022-09-25":{"candlelight":"2022-09-25T18:13:09","folders":["Rosh Hashana","Shabbat Shuva","Hag","Shabbat"],"start_music":"2022-09-25T17:53:09","sunset":"2022-09-25T18:33:09"},"2022-09-30":{"candlelight":"2022-09-30T18:06:34","folders":["Shabbat Shuva","Vayeleh, Shabbat Shuva","Shabbat"],"start_music":"2022-09-30T17:46:34","sunset":"2022-09-30T18:26:34"},"2022-10-04":{"candlelight":"2022-10-04T18:01:23","folders":["Yom Kippur","Shabbat Shuva","Hag","Shabbat"],"start_music":"2022-10-04T17:41:23","sunset":"2022-10-04T18:21:23"},"2022-10-07":{"candlelight":"2022-10-07T17:57:34","folders":["Haazinu","Shabbat"],"start_music":"2022-10-07T17:37:34","sunset":"2022-10-07T18:17:34"},"2022-10-09":{"candlelight":"2022-10-09T17:55:04","folders":["Sukkot","Hag","Shabbat"],"start_music":"2022-10-09T17:35:04","sunset":"2022-10-09T18:15:04"},"2022-10-14":{"candlelight":"2022-10-14T17:48:59","folders":["Sukkot","Shabbat"],"start_music":"2022-10-14T17:28:59","sunset":"2022-10-14T18:08:59"},"2022-10-16":{"candlelight":"2022-10-16T17:46:38","folders":["Simchat Torah","Hag","Shabbat"],"start_music":"2022-10-16T17:26:38","sunset":"2022-10-16T18:06:38"},"2022-10-21":{"candlelight":"2022-10-21T17:41:00","folders":["Bereshith","Shabbat"],"start_music":"2022-10-21T17:21:00","sunset":"2022-10-21T18:01:00"},"2022-10-28":{"candlelight":"2022-10-28T17:33:47","folders":["Noah","Shabbat"],"start_music":"2022-10-28T17:13:47","sunset":"2022-10-28T17:53:47"},"2022-11-04":{"candlelight":"2022-11-04T16:27:31+02:00","folders":["Le'h Leha","Shabbat"],"start_music":"2022-11-04T16:07:31+02:00","sunset":"2022-11-04T16:47:31+02:00"},"2022-11-11":{"candlelight":"2022-11-11T16:22:22+02:00","folders":["Vayera","Shabbat"],"start_music":"2022-11-11T16:02:22+02:00","sunset":"2022-11-11T16:42:22+02:00"},"2022-11-18":{"candlelight":"2022-11-18T16:18:28+02:00","folders":["Haye Sarah","Shabbat"],"start_music":"2022-11-18T15:58:28+02:00","sunset":"2022-11-18T16:38:28+02:00"},"2022-11-25":{"candlelight":"2022-11-25T16:15:57+02:00","folders":["Toledoth","Shabbat"],"start_music":"2022-11-25T15:55:57+02:00","sunset":"2022-11-25T16:35:57+02:00"},"2022-12-02":{"candlelight":"2022-12-02T16:14:52+02:00","folders":["Vayetse","Shabbat"],"start_music":"2022-12-02T15:54:52+02:00","sunset":"2022-12-02T16:34:52+02:00"},"2022-12-09":{"candlelight":"2022-12-09T16:15:15+02:00","folders":["Vayishlah","Shabbat"],"start_music":"2022-12-09T15:55:15+02:00","sunset":"2022-12-09T16:35:15+02:00"},"2022-12-16":{"candlelight":"2022-12-16T16:17:05+02:00","folders":["Vayesheb","Shabbat"],"start_music":"2022-12-16T15:57:05+02:00","sunset":"2022-12-16T16:37:05+02:00"},"2022-12-23":{"candlelight":"2022-12-23T16:20:14+02:00","folders":["Chanukka","Mikkets","Shabbat"],"start_music":"2022-12-23T16:00:14+02:00","sunset":"2022-12-23T16:40:14+02:00"},"2022-12-30":{"candlelight":"2022-12-30T16:24:32+02:00","folders":["Vayiggash","Shabbat"],"start_music":"2022-12-30T16:04:32+02:00","sunset":"2022-12-30T16:44:32+02:00"},"2023-01-06":{"candlelight":"2023-01-06T16:29:47+02:00","folders":["Vayhee","Shabbat"],"start_music":"2023-01-06T16:09:47+02:00","sunset":"2023-01-06T16:49:47+02:00"},"2023-01-13":{"candlelight":"2023-01-13T16:35:42+02:00","folders":["Shemoth","Shabbat"],"start_music":"2023-01-13T16:15:42+02:00","sunset":"2023-01-13T16:55:42+02:00"},"2023-01-20":{"candlelight":"2023-01-20T16:42:02+02:00","folders":["Vaera","Shabbat"],"start_music":"2023-01-20T16:22:02+02:00","sunset":"2023-01-20T17:02:02+02:00"},"2023-01-27":{"candlelight":"2023-01-27T16:48:34+02:00","folders":["Bo","Shabbat"],"start_music":"2023-01-27T16:28:34+02:00","sunset":"2023-01-27T17:08:34+02:00"},"2023-02-03":{"candlelight":"2023-02-03T16:55:05+02:00","folders":["Tu BShvat","Beshallah, Shabbat Shirah","Shabbat"],"start_music":"2023-02-03T16:35:05+02:00","sunset":"2023-02-03T17:15:05+02:00"},"2023-02-10":{"candlelight":"2023-02-10T17:01:27+02:00","folders":["Yithro","Shabbat"],"start_music":"2023-02-10T16:41:27+02:00","sunset":"2023-02-10T17:21:27+02:00"},"2023-02-17":{"candlelight":"2023-02-17T17:07:33+02:00","folders":["Mishpatim, Shabbat Shekalim","Shabbat"],"start_music":"2023-02-17T16:47:33+02:00","sunset":"2023-02-17T17:27:33+02:00"},"2023-02-24":{"candlelight":"2023-02-24T17:13:22+02:00","folders":["Purim","Terumah","Shabbat"],"start_music":"2023-02-24T16:53:22+02:00","sunset":"2023-02-24T17:33:22+02:00"},"2023-03-03":{"candlelight":"2023-03-03T17:18:53+02:00","folders":["Purim","Tetsavveh, Shabbat Za'hor","Shabbat"],"start_music":"2023-03-03T16:58:53+02:00","sunset":"2023-03-03T17:38:53+02:00"},"2023-03-10":{"candlelight":"2023-03-10T17:24:08+02:00","folders":["Purim","Ki Tissa, Shabbat Parah","Shabbat"],"start_music":"2023-03-10T17:04:08+02:00","sunset":"2023-03-10T17:44:08+02:00"},"2023-03-17":{"candlelight":"2023-03-17T17:29:11+02:00","folders":["Vayakhel, Pekude, Shabbat Hahodesh","Shabbat"],"start_music":"2023-03-17T17:09:11+02:00","sunset":"2023-03-17T17:49:11+02:00"},"2023-03-24":{"candlelight":"2023-03-24T18:34:06","folders":["Vayikra","Shabbat"],"start_music":"2023-03-24T18:14:06","sunset":"2023-03-24T18:54:06"},"2023-03-31":{"candlelight":"2023-03-31T18:38:56","folders":["Tsav","Shabbat"],"start_music":"2023-03-31T18:18:56","sunset":"2023-03-31T18:58:56"},"2023-04-05":{"candlelight":"2023-04-05T18:42:23","folders":["Pesach","Hag","Shabbat"],"start_music":"2023-04-05T18:22:23","sunset":"2023-04-05T19:02:23"},"2023-04-07":{"candlelight":"2023-04-07T18:43:46","folders":["Pesach","HOmer","Shabbat"],"start_music":"2023-04-07T18:23:46","sunset":"2023-04-07T19:03:46"},"2023-04-11":{"candlelight":"2023-04-11T18:46:32","folders":["Pesach","Hag","Shabbat"],"start_music":"2023-04-11T18:26:32","sunset":"2023-04-11T19:06:32"},"2023-04-14":{"candlelight":"2023-04-14T18:48:37","folders":["Yom Hashoah","HOmer","Shemini","Shabbat"],"start_music":"2023-04-14T18:28:37","sunset":"2023-04-14T19:08:37"},"2023-04-21":{"candlelight":"2023-04-21T18:53:33","folders":["HOmer","Yom Hazikaron","Tazria, Metsora","Shabbat"],"start_music":"2023-04-21T18:33:33","sunset":"2023-04-21T19:13:33"},"2023-04-28":{"candlelight":"2023-04-28T18:58:33","folders":["HOmer","Aharemoth, Kedoshim","Shabbat"],"start_music":"2023-04-28T18:38:33","sunset":"2023-04-28T19:18:33"},"2023-05-05":{"candlelight":"2023-05-05T19:03:35","folders":["Lag BOmer","HOmer","Emor","Shabbat"],"start_music":"2023-05-05T18:43:35","sunset":"2023-05-05T19:23:35"},"2023-05-12":{"candlelight":"2023-05-12T19:08:36","folders":["Behar, Behukkothai","Shabbat"],"start_music":"2023-05-12T18:48:36","sunset":"2023-05-12T19:28:36"},"2023-05-19":{"candlelight":"2023-05-19T19:13:29","folders":["Bemidbar","Shabbat"],"start_music":"2023-05-19T18:53:29","sunset":"2023-05-19T19:33:29"},"2023-05-25":{"candlelight":"2023-05-25T19:17:28","folders":["Shavuot","Hag","Shabbat"],"start_music":"2023-05-25T18:57:28","sunset":"2023-05-25T19:37:28"},"2023-06-02":{"candlelight":"2023-06-02T19:22:17","folders":["Naso","Shabbat"],"start_music":"2023-06-02T19:02:17","sunset":"2023-06-02T19:42:17"},"2023-06-09":{"candlelight":"2023-06-09T19:25:49","folders":["Behaaloteha","Shabbat"],"start_music":"2023-06-09T19:05:49","sunset":"2023-06-09T19:45:49"},"2023-06-16":{"candlelight":"2023-06-16T19:28:33","folders":["Shelah Leha","Shabbat"],"start_music":"2023-06-16T19:08:33","sunset":"2023-06-16T19:48:33"},"2023-06-23":{"candlelight":"2023-06-23T19:30:17","folders":["Korah","Shabbat"],"start_music":"2023-06-23T19:10:17","sunset":"2023-06-23T19:50:17"},"2023-06-30":{"candlelight":"2023-06-30T19:30:54","folders":["ShloshetShavuot","Hukath, Balak","Shabbat"],"start_music":"2023-06-30T19:10:54","sunset":"2023-06-30T19:50:54"},"2023-07-07":{"candlelight":"2023-07-07T19:30:17","folders":["ShloshetShavuot","Pinhas","Shabbat"],"start_music":"2023-07-07T19:10:17","sunset":"2023-07-07T19:50:17"}}'''
        json_str='''{"2022-06-17": {"candlelight": "2022-06-17T19:28:56", "folders": {"name": "\u05e9\u05dc\u05da-\u05dc\u05da", "songs": ["\u05e9\u05dc\u05da-\u05dc\u05da", "Shabbat"]}, "start_music": "2022-06-17T19:08:56", "sunset": "2022-06-17T19:48:56"}, "2022-06-24": {"candlelight": "2022-06-24T19:30:29", "folders": {"name": "\u05e7\u05e8\u05d7", "songs": ["\u05e7\u05e8\u05d7", "Shabbat"]}, "start_music": "2022-06-24T19:10:29", "sunset": "2022-06-24T19:50:29"}, "2022-07-01": {"candlelight": "2022-07-01T19:30:53", "folders": {"name": "\u05d7\u05e7\u05ea", "songs": ["\u05d7\u05e7\u05ea", "Shabbat"]}, "start_music": "2022-07-01T19:10:53", "sunset": "2022-07-01T19:50:53"}, "2022-07-08": {"candlelight": "2022-07-08T19:30:02", "folders": {"name": "\u05d1\u05dc\u05e7", "songs": ["\u05d1\u05dc\u05e7", "Shabbat"]}, "start_music": "2022-07-08T19:10:02", "sunset": "2022-07-08T19:50:02"}, "2022-07-15": {"candlelight": "2022-07-15T19:27:56", "folders": {"name": "\u05e4\u05d9\u05e0\u05d7\u05e1", "songs": ["ShloshetShavuot", "\u05e4\u05d9\u05e0\u05d7\u05e1", "Shabbat"]}, "start_music": "2022-07-15T19:07:56", "sunset": "2022-07-15T19:47:56"}, "2022-07-22": {"candlelight": "2022-07-22T19:24:34", "folders": {"name": "\u05de\u05d8\u05d5\u05ea", "songs": ["ShloshetShavuot", "\u05de\u05d8\u05d5\u05ea", "Shabbat"]}, "start_music": "2022-07-22T19:04:34", "sunset": "2022-07-22T19:44:34"}, "2022-07-29": {"candlelight": "2022-07-29T19:20:01", "folders": {"name": "\u05de\u05e1\u05e2\u05d9", "songs": ["ShloshetShavuot", "\u05de\u05e1\u05e2\u05d9", "Shabbat"]}, "start_music": "2022-07-29T19:00:01", "sunset": "2022-07-29T19:40:01"}, "2022-08-05": {"candlelight": "2022-08-05T19:14:22", "folders": {"name": "\u05d3\u05d1\u05e8\u05d9\u05dd", "songs": ["Tisha BAv", "\u05d3\u05d1\u05e8\u05d9\u05dd", "Shabbat"]}, "start_music": "2022-08-05T18:54:22", "sunset": "2022-08-05T19:34:22"}, "2022-08-12": {"candlelight": "2022-08-12T19:07:45", "folders": {"name": "\u05d5\u05d0\u05ea\u05d7\u05e0\u05df", "songs": ["\u05d5\u05d0\u05ea\u05d7\u05e0\u05df", "Shabbat"]}, "start_music": "2022-08-12T18:47:45", "sunset": "2022-08-12T19:27:45"}, "2022-08-19": {"candlelight": "2022-08-19T19:00:18", "folders": {"name": "\u05e2\u05e7\u05d1", "songs": ["\u05e2\u05e7\u05d1", "Shabbat"]}, "start_music": "2022-08-19T18:40:18", "sunset": "2022-08-19T19:20:18"}, "2022-08-26": {"candlelight": "2022-08-26T18:52:09", "folders": {"name": "\u05e8\u05d0\u05d4", "songs": ["\u05e8\u05d0\u05d4", "Shabbat"]}, "start_music": "2022-08-26T18:32:09", "sunset": "2022-08-26T19:12:09"}, "2022-09-02": {"candlelight": "2022-09-02T18:43:29", "folders": {"name": "\u05e9\u05d5\u05e4\u05d8\u05d9\u05dd", "songs": ["\u05e9\u05d5\u05e4\u05d8\u05d9\u05dd", "Shabbat"]}, "start_music": "2022-09-02T18:23:29", "sunset": "2022-09-02T19:03:29"}, "2022-09-09": {"candlelight": "2022-09-09T18:34:26", "folders": {"name": "\u05db\u05d9-\u05ea\u05e6\u05d0", "songs": ["\u05db\u05d9-\u05ea\u05e6\u05d0", "Shabbat"]}, "start_music": "2022-09-09T18:14:26", "sunset": "2022-09-09T18:54:26"}, "2022-09-16": {"candlelight": "2022-09-16T18:25:09", "folders": {"name": "\u05db\u05d9-\u05ea\u05d1\u05d5\u05d0", "songs": ["\u05db\u05d9-\u05ea\u05d1\u05d5\u05d0", "Shabbat"]}, "start_music": "2022-09-16T18:05:09", "sunset": "2022-09-16T18:45:09"}, "2022-09-23": {"candlelight": "2022-09-23T18:15:49", "folders": {"name": "\u05e0\u05e6\u05d1\u05d9\u05dd", "songs": ["\u05e0\u05e6\u05d1\u05d9\u05dd", "Shabbat"]}, "start_music": "2022-09-23T17:55:49", "sunset": "2022-09-23T18:35:49"}, "2022-09-25": {"candlelight": "2022-09-25T18:13:09", "folders": {"name": "Rosh Hashana", "songs": ["Rosh Hashana", "Shabbat Shuva", "Hag", "Shabbat"]}, "start_music": "2022-09-25T17:53:09", "sunset": "2022-09-25T18:33:09"}, "2022-09-30": {"candlelight": "2022-09-30T18:06:34", "folders": {"name": "\u05d5\u05d9\u05dc\u05da", "songs": ["Shabbat Shuva", "\u05d5\u05d9\u05dc\u05da", "Shabbat"]}, "start_music": "2022-09-30T17:46:34", "sunset": "2022-09-30T18:26:34"}, "2022-10-04": {"candlelight": "2022-10-04T18:01:23", "folders": {"name": "Yom Kippur", "songs": ["Yom Kippur", "Shabbat Shuva", "Hag", "Shabbat"]}, "start_music": "2022-10-04T17:41:23", "sunset": "2022-10-04T18:21:23"}, "2022-10-07": {"candlelight": "2022-10-07T17:57:34", "folders": {"name": "\u05d4\u05d0\u05d6\u05d9\u05e0\u05d5", "songs": ["\u05d4\u05d0\u05d6\u05d9\u05e0\u05d5", "Shabbat"]}, "start_music": "2022-10-07T17:37:34", "sunset": "2022-10-07T18:17:34"}, "2022-10-09": {"candlelight": "2022-10-09T17:55:04", "folders": {"name": "Sukkot", "songs": ["Sukkot", "Hag", "Shabbat"]}, "start_music": "2022-10-09T17:35:04", "sunset": "2022-10-09T18:15:04"}, "2022-10-14": {"candlelight": "2022-10-14T17:48:59", "folders": {"name": "", "songs": ["Sukkot", "Shabbat"]}, "start_music": "2022-10-14T17:28:59", "sunset": "2022-10-14T18:08:59"}, "2022-10-16": {"candlelight": "2022-10-16T17:46:38", "folders": {"name": "Simchat Torah", "songs": ["Simchat Torah", "Hag", "Shabbat"]}, "start_music": "2022-10-16T17:26:38", "sunset": "2022-10-16T18:06:38"}, "2022-10-21": {"candlelight": "2022-10-21T17:41:00", "folders": {"name": "\u05d1\u05e8\u05d0\u05e9\u05d9\u05ea", "songs": ["\u05d1\u05e8\u05d0\u05e9\u05d9\u05ea", "Shabbat"]}, "start_music": "2022-10-21T17:21:00", "sunset": "2022-10-21T18:01:00"}, "2022-10-28": {"candlelight": "2022-10-28T17:33:47", "folders": {"name": "\u05e0\u05d7", "songs": ["\u05e0\u05d7", "Shabbat"]}, "start_music": "2022-10-28T17:13:47", "sunset": "2022-10-28T17:53:47"}, "2022-11-04": {"candlelight": "2022-11-04T16:27:31+02:00", "folders": {"name": "\u05dc\u05da \u05dc\u05da", "songs": ["\u05dc\u05da \u05dc\u05da", "Shabbat"]}, "start_music": "2022-11-04T16:07:31+02:00", "sunset": "2022-11-04T16:47:31+02:00"}, "2022-11-11": {"candlelight": "2022-11-11T16:22:22+02:00", "folders": {"name": "\u05d5\u05d9\u05e8\u05d0", "songs": ["\u05d5\u05d9\u05e8\u05d0", "Shabbat"]}, "start_music": "2022-11-11T16:02:22+02:00", "sunset": "2022-11-11T16:42:22+02:00"}, "2022-11-18": {"candlelight": "2022-11-18T16:18:28+02:00", "folders": {"name": "\u05d7\u05d9\u05d9 \u05e9\u05e8\u05d4", "songs": ["\u05d7\u05d9\u05d9 \u05e9\u05e8\u05d4", "Shabbat"]}, "start_music": "2022-11-18T15:58:28+02:00", "sunset": "2022-11-18T16:38:28+02:00"}, "2022-11-25": {"candlelight": "2022-11-25T16:15:57+02:00", "folders": {"name": "\u05ea\u05d5\u05dc\u05d3\u05d5\u05ea", "songs": ["\u05ea\u05d5\u05dc\u05d3\u05d5\u05ea", "Shabbat"]}, "start_music": "2022-11-25T15:55:57+02:00", "sunset": "2022-11-25T16:35:57+02:00"}, "2022-12-02": {"candlelight": "2022-12-02T16:14:52+02:00", "folders": {"name": "\u05d5\u05d9\u05e6\u05d0", "songs": ["\u05d5\u05d9\u05e6\u05d0", "Shabbat"]}, "start_music": "2022-12-02T15:54:52+02:00", "sunset": "2022-12-02T16:34:52+02:00"}, "2022-12-09": {"candlelight": "2022-12-09T16:15:15+02:00", "folders": {"name": "\u05d5\u05d9\u05e9\u05dc\u05d7", "songs": ["\u05d5\u05d9\u05e9\u05dc\u05d7", "Shabbat"]}, "start_music": "2022-12-09T15:55:15+02:00", "sunset": "2022-12-09T16:35:15+02:00"}, "2022-12-16": {"candlelight": "2022-12-16T16:17:05+02:00", "folders": {"name": "\u05d5\u05d9\u05e9\u05d1", "songs": ["\u05d5\u05d9\u05e9\u05d1", "Shabbat"]}, "start_music": "2022-12-16T15:57:05+02:00", "sunset": "2022-12-16T16:37:05+02:00"}, "2022-12-23": {"candlelight": "2022-12-23T16:20:14+02:00", "folders": {"name": "\u05de\u05e7\u05e5", "songs": ["Chanukka", "\u05de\u05e7\u05e5", "Shabbat"]}, "start_music": "2022-12-23T16:00:14+02:00", "sunset": "2022-12-23T16:40:14+02:00"}, "2022-12-30": {"candlelight": "2022-12-30T16:24:32+02:00", "folders": {"name": "\u05d5\u05d9\u05d2\u05e9", "songs": ["\u05d5\u05d9\u05d2\u05e9", "Shabbat"]}, "start_music": "2022-12-30T16:04:32+02:00", "sunset": "2022-12-30T16:44:32+02:00"}, "2023-01-06": {"candlelight": "2023-01-06T16:29:47+02:00", "folders": {"name": "\u05d5\u05d9\u05d7\u05d9", "songs": ["\u05d5\u05d9\u05d7\u05d9", "Shabbat"]}, "start_music": "2023-01-06T16:09:47+02:00", "sunset": "2023-01-06T16:49:47+02:00"}, "2023-01-13": {"candlelight": "2023-01-13T16:35:42+02:00", "folders": {"name": "\u05e9\u05de\u05d5\u05ea", "songs": ["\u05e9\u05de\u05d5\u05ea", "Shabbat"]}, "start_music": "2023-01-13T16:15:42+02:00", "sunset": "2023-01-13T16:55:42+02:00"}, "2023-01-20": {"candlelight": "2023-01-20T16:42:02+02:00", "folders": {"name": "\u05d5\u05d0\u05e8\u05d0", "songs": ["\u05d5\u05d0\u05e8\u05d0", "Shabbat"]}, "start_music": "2023-01-20T16:22:02+02:00", "sunset": "2023-01-20T17:02:02+02:00"}, "2023-01-27": {"candlelight": "2023-01-27T16:48:34+02:00", "folders": {"name": "\u05d1\u05d5", "songs": ["\u05d1\u05d5", "Shabbat"]}, "start_music": "2023-01-27T16:28:34+02:00", "sunset": "2023-01-27T17:08:34+02:00"}, "2023-02-03": {"candlelight": "2023-02-03T16:55:05+02:00", "folders": {"name": "\u05d1\u05e9\u05dc\u05d7", "songs": ["Tu BShvat", "\u05d1\u05e9\u05dc\u05d7", "Shabbat"]}, "start_music": "2023-02-03T16:35:05+02:00", "sunset": "2023-02-03T17:15:05+02:00"}, "2023-02-10": {"candlelight": "2023-02-10T17:01:27+02:00", "folders": {"name": "\u05d9\u05ea\u05e8\u05d5", "songs": ["\u05d9\u05ea\u05e8\u05d5", "Shabbat"]}, "start_music": "2023-02-10T16:41:27+02:00", "sunset": "2023-02-10T17:21:27+02:00"}, "2023-02-17": {"candlelight": "2023-02-17T17:07:33+02:00", "folders": {"name": "\u05de\u05e9\u05e4\u05d8\u05d9\u05dd", "songs": ["\u05de\u05e9\u05e4\u05d8\u05d9\u05dd", "Shabbat"]}, "start_music": "2023-02-17T16:47:33+02:00", "sunset": "2023-02-17T17:27:33+02:00"}, "2023-02-24": {"candlelight": "2023-02-24T17:13:22+02:00", "folders": {"name": "\u05ea\u05e8\u05d5\u05de\u05d4", "songs": ["Purim", "\u05ea\u05e8\u05d5\u05de\u05d4", "Shabbat"]}, "start_music": "2023-02-24T16:53:22+02:00", "sunset": "2023-02-24T17:33:22+02:00"}, "2023-03-03": {"candlelight": "2023-03-03T17:18:53+02:00", "folders": {"name": "\u05ea\u05e6\u05d5\u05d5\u05d4", "songs": ["Purim", "\u05ea\u05e6\u05d5\u05d5\u05d4", "Shabbat"]}, "start_music": "2023-03-03T16:58:53+02:00", "sunset": "2023-03-03T17:38:53+02:00"}, "2023-03-10": {"candlelight": "2023-03-10T17:24:08+02:00", "folders": {"name": "\u05db\u05d9-\u05ea\u05e9\u05d0", "songs": ["Purim", "\u05db\u05d9-\u05ea\u05e9\u05d0", "Shabbat"]}, "start_music": "2023-03-10T17:04:08+02:00", "sunset": "2023-03-10T17:44:08+02:00"}, "2023-03-17": {"candlelight": "2023-03-17T17:29:11+02:00", "folders": {"name": "\u05d5\u05d9\u05e7\u05d4\u05dc - \u05e4\u05e7\u05d5\u05d3\u05d9", "songs": ["\u05d5\u05d9\u05e7\u05d4\u05dc - \u05e4\u05e7\u05d5\u05d3\u05d9", "Shabbat"]}, "start_music": "2023-03-17T17:09:11+02:00", "sunset": "2023-03-17T17:49:11+02:00"}, "2023-03-24": {"candlelight": "2023-03-24T18:34:06", "folders": {"name": "\u05d5\u05d9\u05e7\u05e8\u05d0", "songs": ["\u05d5\u05d9\u05e7\u05e8\u05d0", "Shabbat"]}, "start_music": "2023-03-24T18:14:06", "sunset": "2023-03-24T18:54:06"}, "2023-03-31": {"candlelight": "2023-03-31T18:38:56", "folders": {"name": "\u05e6\u05d5", "songs": ["\u05e6\u05d5", "Shabbat"]}, "start_music": "2023-03-31T18:18:56", "sunset": "2023-03-31T18:58:56"}, "2023-04-05": {"candlelight": "2023-04-05T18:42:23", "folders": {"name": "Pesach", "songs": ["Pesach", "Hag", "Shabbat"]}, "start_music": "2023-04-05T18:22:23", "sunset": "2023-04-05T19:02:23"}, "2023-04-07": {"candlelight": "2023-04-07T18:43:46", "folders": {"name": "", "songs": ["Pesach", "HOmer", "Shabbat"]}, "start_music": "2023-04-07T18:23:46", "sunset": "2023-04-07T19:03:46"}, "2023-04-11": {"candlelight": "2023-04-11T18:46:32", "folders": {"name": "Pesach", "songs": ["Pesach", "Hag", "Shabbat"]}, "start_music": "2023-04-11T18:26:32", "sunset": "2023-04-11T19:06:32"}, "2023-04-14": {"candlelight": "2023-04-14T18:48:37", "folders": {"name": "\u05e9\u05de\u05d9\u05e0\u05d9", "songs": ["Yom Hashoah", "HOmer", "\u05e9\u05de\u05d9\u05e0\u05d9", "Shabbat"]}, "start_music": "2023-04-14T18:28:37", "sunset": "2023-04-14T19:08:37"}, "2023-04-21": {"candlelight": "2023-04-21T18:53:33", "folders": {"name": "\u05ea\u05d6\u05e8\u05d9\u05e2 - \u05de\u05e6\u05d5\u05e8\u05e2", "songs": ["HOmer", "Yom Hazikaron", "\u05ea\u05d6\u05e8\u05d9\u05e2 - \u05de\u05e6\u05d5\u05e8\u05e2", "Shabbat"]}, "start_music": "2023-04-21T18:33:33", "sunset": "2023-04-21T19:13:33"}, "2023-04-28": {"candlelight": "2023-04-28T18:58:33", "folders": {"name": "\u05d0\u05d7\u05e8\u05d9-\u05de\u05d5\u05ea - \u05e7\u05d3\u05d5\u05e9\u05d9\u05dd", "songs": ["HOmer", "\u05d0\u05d7\u05e8\u05d9-\u05de\u05d5\u05ea - \u05e7\u05d3\u05d5\u05e9\u05d9\u05dd", "Shabbat"]}, "start_music": "2023-04-28T18:38:33", "sunset": "2023-04-28T19:18:33"}, "2023-05-05": {"candlelight": "2023-05-05T19:03:35", "folders": {"name": "\u05d0\u05de\u05d5\u05e8", "songs": ["Lag BOmer", "HOmer", "\u05d0\u05de\u05d5\u05e8", "Shabbat"]}, "start_music": "2023-05-05T18:43:35", "sunset": "2023-05-05T19:23:35"}, "2023-05-12": {"candlelight": "2023-05-12T19:08:36", "folders": {"name": "\u05d1\u05d4\u05e8 - \u05d1\u05d7\u05e7\u05d5\u05ea\u05d9", "songs": ["\u05d1\u05d4\u05e8 - \u05d1\u05d7\u05e7\u05d5\u05ea\u05d9", "Shabbat"]}, "start_music": "2023-05-12T18:48:36", "sunset": "2023-05-12T19:28:36"}, "2023-05-19": {"candlelight": "2023-05-19T19:13:29", "folders": {"name": "\u05d1\u05de\u05d3\u05d1\u05e8", "songs": ["\u05d1\u05de\u05d3\u05d1\u05e8", "Shabbat"]}, "start_music": "2023-05-19T18:53:29", "sunset": "2023-05-19T19:33:29"}, "2023-05-25": {"candlelight": "2023-05-25T19:17:28", "folders": {"name": "Shavuot", "songs": ["Shavuot", "Hag", "Shabbat"]}, "start_music": "2023-05-25T18:57:28", "sunset": "2023-05-25T19:37:28"}, "2023-06-02": {"candlelight": "2023-06-02T19:22:17", "folders": {"name": "\u05e0\u05e9\u05d0", "songs": ["\u05e0\u05e9\u05d0", "Shabbat"]}, "start_music": "2023-06-02T19:02:17", "sunset": "2023-06-02T19:42:17"}, "2023-06-09": {"candlelight": "2023-06-09T19:25:49", "folders": {"name": "\u05d1\u05d4\u05e2\u05dc\u05d5\u05ea\u05da", "songs": ["\u05d1\u05d4\u05e2\u05dc\u05d5\u05ea\u05da", "Shabbat"]}, "start_music": "2023-06-09T19:05:49", "sunset": "2023-06-09T19:45:49"}, "2023-06-16": {"candlelight": "2023-06-16T19:28:33", "folders": {"name": "\u05e9\u05dc\u05da-\u05dc\u05da", "songs": ["\u05e9\u05dc\u05da-\u05dc\u05da", "Shabbat"]}, "start_music": "2023-06-16T19:08:33", "sunset": "2023-06-16T19:48:33"}, "2023-06-23": {"candlelight": "2023-06-23T19:30:17", "folders": {"name": "\u05e7\u05e8\u05d7", "songs": ["\u05e7\u05e8\u05d7", "Shabbat"]}, "start_music": "2023-06-23T19:10:17", "sunset": "2023-06-23T19:50:17"}, "2023-06-30": {"candlelight": "2023-06-30T19:30:54", "folders": {"name": "\u05d7\u05e7\u05ea - \u05d1\u05dc\u05e7", "songs": ["ShloshetShavuot", "\u05d7\u05e7\u05ea - \u05d1\u05dc\u05e7", "Shabbat"]}, "start_music": "2023-06-30T19:10:54", "sunset": "2023-06-30T19:50:54"}, "2023-07-07": {"candlelight": "2023-07-07T19:30:17", "folders": {"name": "\u05e4\u05d9\u05e0\u05d7\u05e1", "songs": ["ShloshetShavuot", "\u05e4\u05d9\u05e0\u05d7\u05e1", "Shabbat"]}, "start_music": "2023-07-07T19:10:17", "sunset": "2023-07-07T19:50:17"}}'''
        import json
        data = json.loads(json_str)
        # for k,v in data.items:
        #     v.sunset = v.sunset
        context['dates_data'] = data

        return TemplateResponse(
            request,
            'device_realtime.html',
            context,
        )
    #'songs_report',
    # description functions like a model field's verbose_name
    # @admin.display(description='Address')
    # def songs_report(self, instance):
    #     # assuming get_full_address() returns a list of strings
    #     # for each line of the address and you want to separate each
    #     # line by a linebreak
    #     # return format_html_join(
    #     #     mark_safe('a'),'b','c')
    #     device_files = instance.files.all()
    #     group_files = instance.group.files.all()
    #
    #
    #     return format_html_join(
    #         mark_safe('a<br>'),
    #         'a{}',
    #         ((line,) for line in files.file.name),
    #     ) or mark_safe("<span class='errors'>I can't determine this address.</span>")

def create_modeladmin(modeladmin, model, name = None):
    class Meta:
        proxy = True
        app_label = model._meta.app_label

    attrs = {'__module__': '', 'Meta': Meta}

    newmodel = type(name, (model,), attrs)

    admin.site.register(newmodel, modeladmin)
    return modeladmin


class Device2(Device):
    class Meta:
        proxy = True

class Device2Admin(admin.ModelAdmin):
    # def get_queryset(self, request):
    #     return self.model.objects.filter(user = request.user)
    pass


create_modeladmin(Device2Admin, model=Device, name='device2a')






from django.db import models

class TopLevel(models.Model):
    name = models.CharField(max_length=200)

class LevelOne(models.Model):
    name = models.CharField(max_length=200)
    level = models.ForeignKey('TopLevel', on_delete=models.PROTECT)

class LevelTwo(models.Model):
    name = models.CharField(max_length=200)
    level = models.ForeignKey('LevelOne', on_delete=models.PROTECT)

class LevelThree(models.Model):
    name = models.CharField(max_length=200)
    level = models.ForeignKey('LevelTwo', on_delete=models.PROTECT)

from django.contrib import admin
#from example.models import *

class LevelThreeInline(NestedStackedInline):
    model = LevelThree
    extra = 1
    #fk_name = 'level'


class LevelTwoInline(NestedStackedInline):
    model = LevelTwo
    extra = 1
    #fk_name = 'level'
    inlines = [LevelThreeInline]


class LevelOneInline(NestedStackedInline):
    model = LevelOne
    extra = 1
    #fk_name = 'level'
    inlines = [LevelTwoInline]


class TopLevelAdmin(NestedModelAdmin):
    model = TopLevel
    inlines = [LevelOneInline]


admin.site.register(TopLevel, TopLevelAdmin)
