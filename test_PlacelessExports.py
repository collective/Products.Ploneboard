## Script (Python) "test_PlacelessExports"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# upload this as a Script (Python) and run, to test our exports
from Products.PlacelessTranslationService import negotiate, translate, getLanguages, getLanguageName

print 'all languages:', getLanguages()
print 'Plone languages:', getLanguages('plone')
print 'negotiate, if we have pt-br and zh:', negotiate(('pt-br', 'zh'), context.REQUEST)
print 'negotiate, if we have foo-bar and %%-##:', negotiate(('foo-bar', '%%-##'), context.REQUEST)
print 'translation of "Search":', translate('plone', 'Search', context=context.REQUEST)
print 'name of pt-br:', getLanguageName('pt-br')

return printed
