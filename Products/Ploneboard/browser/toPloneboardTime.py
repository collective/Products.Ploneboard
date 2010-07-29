from zope.i18n import translate
from DateTime.DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _plone
from Products.CMFPlone import PloneLocalesMessageFactory as _locales
from Products.Five import BrowserView

class defer(object):
    """Defer function call until actually used. Useful for date components in translations."""
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        return self.func(*self.args, **self.kwargs)


class ToPloneboardTimeView(BrowserView):
    """Given a time string convert it into a DateTime and then format it appropriately."""

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)

    def toPloneboardTime(self, time_=None):
        """Return time formatted for Ploneboard"""
        
        context = self.context
        request = self.request

        ploneboard_time=None
        
        ts = getToolByName(context, 'translation_service')

        format = '%Y;%m;%d;%w;%H;%M;%S'

        young_format_en = '%A %H:%M' 
        old_format_en = '%B %d. %Y'

        if not time_:
            return 'Unknown date'

        try:
            if not isinstance(time_, DateTime):
                time_ = DateTime(str(time_))
            (year, month, day, wday, hours, minutes, seconds) = time_.strftime(format).split(';')
            
            translated_date_elements = {'year':year,
                                        'month':defer(translate, _locales(ts.month_msgid(month)), context=request),
                                        'day':day,
                                        'hours':hours,
                                        'minutes':minutes}
               
            ploneboard_time = translate(_plone('old_date_format: ${year} ${month} ${day} ${hours}:${minutes}',
                                                default = unicode(time_.strftime(old_format_en)),
                                                mapping = translated_date_elements),
                                         context=request)
        
        except IndexError:
            pass 
        
        return ploneboard_time