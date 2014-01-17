from zope.schema import Tuple, Bool
from zope.schema import Choice
from zope.interface import implements
from zope.interface import Interface
from zope.formlib.form import FormFields
from zope.component import adapts
from plone.app.controlpanel.form import ControlPanelForm
from plone.app.controlpanel.widgets import MultiCheckBoxVocabularyWidget
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Ploneboard.utils import PloneboardMessageFactory as _


class ITransformSchema(Interface):
    enabled_transforms = Tuple(
            title=_(u"label_transforms",
                default=u"Transforms"),
            description=_(u"help_transforms",
                default=u"Select the text transformations that should be "
                        u"used for comments posted in Ploneboard "
                        u"conversations. Text transformations alter the "
                        u"text entered by the user, either to remove "
                        u"potentially malicious HTML tags, or to add "
                        u"additional functionality, such as making links "
                        u"clickable."),
            required=True,
            missing_value=set(),
            value_type=Choice(
                vocabulary="Products.Ploneboard.AvailableTransforms"))

    enable_anon_name = Bool(
            title=_(u"label_anon_nick",
                default=u"Anonymous name"),
            description=_(u"help_anon_nick",
                default=u"If selected, anonymous users can insert a name in their comments."),
            required=False)


class ControlPanelAdapter(SchemaAdapterBase):
    adapts(IPloneSiteRoot)
    implements(ITransformSchema)

    def __init__(self, context):
        super(ControlPanelAdapter, self).__init__(context)
        self.tool = getToolByName(self.context, "portal_ploneboard")

    def get_enabled_transforms(self):
        return self.tool.getEnabledTransforms()

    def set_enabled_transforms(self, value):
        for t in self.tool.getTransforms():
            self.tool.enableTransform(t, t in value)

    def get_enable_anon_name(self):
        return self.tool.getEnableAnonName()

    def set_enable_anon_name(self, value):
        self.tool.setEnableAnonName(value)

    enabled_transforms = property(get_enabled_transforms, set_enabled_transforms)
    enable_anon_name = property(get_enable_anon_name, set_enable_anon_name)


class ControlPanel(ControlPanelForm):
    form_fields = FormFields(ITransformSchema)
    form_fields["enabled_transforms"].custom_widget = MultiCheckBoxVocabularyWidget

    label = _(u"ploneboard_configuration",
            default=u"Ploneboard configuration")
    description = _(u"description_ploneboard_config",
            default=u"Here you can configure site settings for Ploneboard.")

    form_name = _(u"ploneboard_transform_panel",
            default=u"Text transformations")
