from datetime import datetime
from dateutil.parser import parse as dateparse
from zope.i18n import translate
from DateTime.DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _plone
from Products.CMFPlone import PloneLocalesMessageFactory as _locales
from Products.Ploneboard.interfaces import IConversation, IComment
import time


class defer(object):
    """Defer function call until actually used. Useful for date components in translations"""
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        return self.func(*self.args, **self.kwargs)


def toPloneboardTime(context, request, time_=None):
    """Return time formatted for Ploneboard"""
    ploneboard_time=None
    ts = getToolByName(context, 'translation_service')

    format = '%Y;%m;%d;%w;%H;%M;%S'

    # fallback formats, english
    young_format_en = '%A %H:%M' 
    old_format_en = '%B %d. %Y'


    if not time_:
        return 'Unknown date'

    try:
        if isinstance(time_, DateTime):
            time_ = datetime.fromtimestamp(time_.timeTime())
        else:
            time_ = dateparse(str(time_))

        (year, month, day, hours, minutes, seconds, wday, _, dst) = time_.timetuple()
        translated_date_elements = { 'year'   : year
                                   , 'month'  : unicode(defer(translate, _locales(ts.month_msgid(month)), context=request))
                                   , 'day'    : day
                                   , 'wday'   : unicode(defer(translate, _locales(ts.day_msgid((wday+1)%7)), context=request))
                                   , 'hours'  : "%02i" % hours
                                   , 'minutes': "%02i" % minutes
                                   , 'seconds': "%02i" % seconds
                                   }

        if time.time() - time.mktime(time_.timetuple()) < 604800: # 60*60*24*7
            ploneboard_time = translate('${wday} ${hours}:${minutes}',
                                        mapping=translated_date_elements,
                                        context=request)

        else:
            ploneboard_time = translate( _plone( 'old_date_format: ${year} ${month} ${day} ${hours}:${minutes}'
                                               , default = unicode(time_.strftime(old_format_en).decode('utf-8'))
                                               , mapping = translated_date_elements)
                                        , context=request
                                        )

    except IndexError:
        pass 

    return ploneboard_time

def getNumberOfComments(node, catalog=None):
    """Returns the number of comments to this forum."""
    if catalog is None:
        catalog = getToolByName(node, 'portal_catalog')
    return len(catalog(
        object_provides=IComment.__identifier__,
        path='/'.join(node.getPhysicalPath())))

def getNumberOfConversations(node, catalog=None):
    """Returns the number of conversations in this forum."""
    if catalog is None:
        catalog = getToolByName(node, 'portal_catalog')
    return len(catalog(
        object_provides=IConversation.__identifier__,
        path='/'.join(node.getPhysicalPath())))
