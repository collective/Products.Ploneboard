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
ploneboard_time=None

format = '%A %H:%M'
oldformat = '%B %d. %Y'

if not time:
    return 'Unknown date'

try:
    if not isinstance(time, DateTime):
        time = DateTime(str(time))
    if time.greaterThan(DateTime()-7):
        ploneboard_time = time.strftime(format)
    else:
        ploneboard_time=time.strftime(oldformat)
except IndexError:
    pass 

return ploneboard_time

