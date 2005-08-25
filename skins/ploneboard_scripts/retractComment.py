## Script (Python) "retractComment"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=comment=None, redirect=1, REQUEST=None
##title=
##

if comment is None:
    comment = context

from Products.CMFCore.utils import getToolByName
wftool = getToolByName(context, 'portal_workflow')

try:
    wftool.doActionFor(comment, 'retract')
except:
    # XXX Bare except! Should only really catch Workflow exceptions
    pass

if redirect:
    if REQUEST is None:
       REQUEST = context.REQUEST
    REQUEST.RESPONSE.redirect( REQUEST['HTTP_REFERER'] )
