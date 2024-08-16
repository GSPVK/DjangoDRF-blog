from ckeditor.widgets import CKEditorWidget
from django_bleach.forms import BleachField as BleachFormField
from django_bleach.models import BleachField


class RichBleachTextField(BleachField):
    """
    A merge of ckeditor.fields.RichTextField and BleachField.

    This class can be used instead of models.TextField. For more details, refer to the
    django-ckeditor and django-bleach documentation.
    """

    # After implementing this class, I realized that it is preferable to use django-bleach in the template,
    # while keeping RichTextField from django-ckeditor in the model (in this case, referring to blog.models.Comment),
    # as it simply works better. The differences are as follows:
    # - Tags not specified in settings.BLEACH_ALLOWED_TAGS are not removed from the database, but simply not
    #   displayed in the template.
    # - This prevents cases where there are objects in the database with a tag that we decided to remove from
    #   settings.BLEACH_ALLOWED_TAGS. In such cases, tags are not automatically removed from objects and continue
    #   to be displayed until the user edits the comment.

    def __init__(self, *args, **kwargs):
        self.config_name = kwargs.pop("config_name", "default")
        self.extra_plugins = kwargs.pop("extra_plugins", [])
        self.external_plugin_resources = kwargs.pop("external_plugin_resources", [])
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            "form_class": RichTextFormField,
            "config_name": self.config_name,
            "extra_plugins": self.extra_plugins,
            "external_plugin_resources": self.external_plugin_resources,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)


class RichTextFormField(BleachFormField):
    widget = CKEditorWidget

    def __init__(
            self,
            config_name="default",
            extra_plugins=None,
            external_plugin_resources=None,
            *args,
            **kwargs
    ):
        kwargs["widget"] = self.widget(
            config_name=config_name,
            extra_plugins=extra_plugins,
            external_plugin_resources=external_plugin_resources,
        )
        super().__init__(*args, **kwargs)
