## Script (Python) "formatHistoryDiff"
##title=Formats the history diff
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=lines

lst = []

map = {
#    '+' : '<span class="diffPlus">%s</span><br />',
#    '-' : '<span class="diffMinus">%s</span><br />',
    '+' : '<ins class="atcontenttypes-ins">%s</ins><br />',
    '-' : '<del class="atcontenttypes-del">%s</del><br />',
    ' ' : '&nbsp;%s<br />',
    '@' : '<strong>%s</strong><br />',
}

for line in lines:
    first = len(line) and line[0] or ''
    mapping =map.get(first, '%s')
    print mapping % line
    
return printed
