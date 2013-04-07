import os
from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase
from django.utils.translation import ugettext_lazy as _
import models
from django.conf import settings

from image_cropping import widgets
from filer.settings import FILER_STATICMEDIA_PREFIX

class FilerImagePlugin(CMSPluginBase):
    module = 'Filer'
    model = models.FilerImage
    name = _("Image")
    render_template = "cmsplugin_filer_image/image.html"
    text_enabled = True
    raw_id_fields = ('image',)
    admin_preview = False
    fieldsets = (
        (None, {
            'fields': ('caption_text', ('image', 'image_url',), 'cropping', 'alt_text',)
        }),
        (_('Image resizing options'), {
            'classes': ('collapse',),
            'fields': (
                'use_original_image',
                ('width', 'height'),
                ('crop', 'upscale'),
            )
        }),
        (None, {
            'classes': ('collapse',),
            'fields': ('alignment',)
        }),
        (_('More'), {
            'classes': ('collapse',),
            'fields': (('free_link', 'page_link', 'file_link', 'original_link', 'target_blank'), 'description',)
        }),

    )

    def formfield_for_dbfield(self, db_field, **kwargs):
        # print "formfield_for_dbfield"
        # print "db_field", db_field
        crop_fields = getattr(self.model, 'crop_fields', {})
        if db_field.name in crop_fields:
            print "IN IF....", db_field.name
            target = crop_fields[db_field.name]
            if target['fk_field']:
                print "IN IF.... 2"
                # it's a ForeignKey
                kwargs['widget'] = widgets.CropForeignKeyWidget(
                    db_field.rel,
                    field_name=target['fk_field'],
                    admin_site=self.admin_site,
    )
            elif target['hidden']:
                print "IN IF.... 3"
                # it's a hidden ImageField
                kwargs['widget'] = widgets.HiddenImageCropWidget
            else:
                print "IN IF.... 4"
                # it's a regular ImageField
                kwargs['widget'] = widgets.ImageCropWidget

        return super(CMSPluginBase, self).formfield_for_dbfield(db_field, **kwargs)


    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        """
        We just need the popup interface here
        """
        context.update({
            'preview': not "no_preview" in request.GET,
            'is_popup': True,
            'plugin': self.cms_plugin_instance,
            'CMS_MEDIA_URL': settings.CMS_MEDIA_URL,
        })

        return super(CMSPluginBase, self).render_change_form(request, context, add, change, form_url, obj)

    def _get_thumbnail_options(self, context, instance):
        """
        Return the size and options of the thumbnail that should be inserted
        """
        width, height = None, None
        crop, upscale = False, False
        subject_location = False
        placeholder_width = context.get('width', None)
        placeholder_height = context.get('height', None)
        if instance.thumbnail_option:
            # thumbnail option overrides everything else
            if instance.thumbnail_option.width:
                width = instance.thumbnail_option.width
            if instance.thumbnail_option.height:
                height = instance.thumbnail_option.height
            crop = instance.thumbnail_option.crop
            upscale = instance.thumbnail_option.upscale
        else:
            if instance.use_autoscale and placeholder_width:
                # use the placeholder width as a hint for sizing
                width = int(placeholder_width)
            elif instance.width:
                width = instance.width
            if instance.use_autoscale and placeholder_height:
                height = int(placeholder_height)
            elif instance.height:
                height = instance.height
            crop = instance.crop
            upscale = instance.upscale
        if instance.image:
            if instance.image.subject_location:
                subject_location = instance.image.subject_location
            if not height and width:
                # height was not externally defined: use ratio to scale it by the width
                height = int( float(width)*float(instance.image.height)/float(instance.image.width) )
            if not width and height:
                # width was not externally defined: use ratio to scale it by the height
                width = int( float(height)*float(instance.image.width)/float(instance.image.height) )
            if not width:
                # width is still not defined. fallback the actual image width
                width = instance.image.width
            if not height:
                # height is still not defined. fallback the actual image height
                height = instance.image.height
        return {'size': (width, height),
                'crop': crop,
                'upscale': upscale,
                'subject_location': subject_location}

    def get_thumbnail(self, context, instance):
        if instance.image:
            return instance.image.image.file.get_thumbnail(self._get_thumbnail_options(context, instance))

    def render(self, context, instance, placeholder):
        options = self._get_thumbnail_options(context, instance)

        # Calculate size based on cropped area
        if instance.cropping and len(instance.cropping.split(',')) == 4:
            values = [int(float(x)) for x in instance.cropping.split(',')]
            width = abs(values[2] - values[0])
            height = abs(values[3] - values[1])
            size = (width, height,)
        else:
            size = options.get('size')

        context.update({
            'instance': instance,
            'link': instance.link,
            'opts': options,
            # 'size': options.get('size', None),
            'size': size,
            'placeholder': placeholder
        })
        return context

    def icon_src(self, instance):
        if instance.image:
            if getattr(settings, 'FILER_IMAGE_USE_ICON', False) and '32' in instance.image.icons:
                return instance.image.icons['32']
            else:
                # Fake the context with a reasonable width value because it is not
                # available at this stage
                thumbnail = self.get_thumbnail({'width':200}, instance)
                return thumbnail.url
        else:
            return os.path.normpath(u"%s/icons/missingfile_%sx%s.png" % (FILER_STATICMEDIA_PREFIX, 32, 32,))

    class Media:
        js = (
            getattr(settings, 'JQUERY_URL',
                    'https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js'),
            "image_cropping/js/jquery.Jcrop.min.js",
            "image_cropping/image_cropping.js",
        )
        css = {'all': ("image_cropping/css/jquery.Jcrop.min.css",)}


plugin_pool.register_plugin(FilerImagePlugin)
