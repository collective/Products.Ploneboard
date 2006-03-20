## Script (Python) "toPloneboardTime"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=time=None
##title=
##
#given a time string convert it into a DateTime and then format it appropariately
from DateTime import DateTime
translation_tool = context.translation_service
ploneboard_time = None

format = '%H:%M'
oldformat = '%d. %Y'

if not time:
    return 'Unknown date'

try:
    if not isinstance(time, DateTime):
        time = DateTime(str(time))
    if time.greaterThan(DateTime()-7):
        weekday = time.strftime('%A')
        weekday_msgid = 'weekday_%s' % weekday.lower()[:3]
        weekday_translated = translation_tool.utranslate('plone',
                                                         weekday_msgid,
                                                         context=context,
                                                         default=weekday)
        ploneboard_time = '%s %s' % (weekday_translated, time.strftime(format)) # i.e. Monday 13:20
    else:
        month = time.strftime('%B')
        month_msgid = 'month_%s' % month.lower()[:3]
        month_translated = translation_tool.utranslate('plone',
                                                       month_msgid,
                                                       context=context,
                                                       default=month)
        ploneboard_time = '%s %s' % (month_translated, time.strftime(oldformat)) # i.e. December 25. 2006
except IndexError:
    pass 

return ploneboard_time

