from Products.Archetypes.public import *
from config import PROJECTNAME, BANNER_THUMB_SIZE

class BannerImage(BaseContent):
    """A banner image"""

    meta_type = 'BannerImage'
    archetype_name = 'Banner Image'
    content_icon = 'bannerimage_icon.gif'
    global_allow = 0

    schema = BaseSchema + Schema((
            ImageField('image',
                    sizes={'thumb': BANNER_THUMB_SIZE},
                    widget=ImageWidget(     label='Image',
                                            label_msgid='label_image',
                                            description='Image file for the banner',
                                            description_msgid='help_image',
                                            i18n_domain='bannermanager',
                                            )),
            StringField('alttext',
                    widget = TextAreaWidget(description = "Alternate text for the banner image.",
                                            description_msgid = 'help_alttext',
                                            label = 'Alternate text',
                                            label_msgid = 'label_alttext',
                                            i18n_domain = 'bannermanager',
                                            rows = 3)),
            StringField('remoteUrl',
                    required = 1,
                    validators = ('isURL',),
                    widget = StringWidget(  description="The web address of the banner.",
                                            description_msgid = 'help_url',
                                            label = 'URL',
                                            label_msgid = 'label_url',
                                            i18n_domain = 'bannermanager',
                                            )),
            BooleanField('linkTarget',
                    widget = BooleanWidget( description="If checked, the link will open in a new window, if supported by the browser.",
                                            description_msgid = 'help_target',
                                            label = 'Open in new window',
                                            label_msgid = 'label_target',
                                            i18n_domain = 'bannermanager',
                                            )),
            IntegerField('maxViews',
                    validators = ('isInt',),
                    widget = StringWidget(  description="Maximum number of views. After this many views, the banner will disappear. If not set, there is no limit.",
                                            description_msgid = 'help_maxviews',
                                            label = 'Max views',
                                            label_msgid = 'label_maxviews',
                                            i18n_domain = 'bannermanager',
                                            )),
            IntegerField('maxClicks',
                    validators = ('isInt',),
                    widget = StringWidget(  description="Maximum number of clicks. After this many clicks, the banner will disappear. If not set, there is no limit.",
                                            description_msgid = 'help_maxclicks',
                                            label = 'Max clicks',
                                            label_msgid = 'label_maxclicks',
                                            i18n_domain = 'bannermanager',
                                            )),
            IntegerField('weight',
                    validators = ('isInt',),
                    default = 1,
                    required = 1,
                    widget = StringWidget(  description="A banner with a higher weight will be shown more frequently. E.g. a banner with weight 2 will be shown twice as often as one with weight 1.",
                                            description_msgid = 'help_weight',
                                            label = 'Weight',
                                            label_msgid = 'label_weight',
                                            i18n_domain = 'bannermanager',
                                            )),
            IntegerField('views',
                    mode = 'r',
                    default = 0,
                    widget = StringWidget(  description="Number of views so far.",
                                            description_msgid = 'help_views',
                                            label = 'Views',
                                            label_msgid = 'label_views',
                                            i18n_domain = 'bannermanager',
                                            )),
            IntegerField('clicks',
                    mode = 'r',
                    default = 0,
                    widget = StringWidget(  description="Number of clicks so far.",
                                            description_msgid = 'help_clicks',
                                            label = 'Clicks',
                                            label_msgid = 'label_clicks',
                                            i18n_domain = 'bannermanager',
                                            )),
    ))

    def getAlttext(self):
        return self.Description()

    def setAlttext(self, val):
        return self.setDescription(val)

    def tag(self):
        """Return a string of HTML tags that represent this banner"""
        views = self.getViews() + 1
        self.Schema()['views'].set(self, views)

        target = ''
        if self.getLinkTarget():
            target = ' target="_blank"'

        imgtag = self.getImage().tag(alt=self.Description(),title=self.Description())

        return '<a href="%s/redirect"%s>%s</a>' % \
                (self.absolute_url(), target, imgtag)

    def redirect(self, REQUEST, RESPONSE):
        """Redirect the client browser to the URL of this banner"""
        clicks = self.getClicks() + 1
        self.Schema()['clicks'].set(self, clicks)
        RESPONSE.redirect(self.getRemoteUrl())

registerType(BannerImage, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] in ('view', 'references'):
            a['condition'] = 'nothing'
    return fti
