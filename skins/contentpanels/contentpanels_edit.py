## Script (Python) "contentpanels_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=pageIndex=0, panelIndex=0, columnIndex=0, pageTitle='', pageWidth='', pageCellSpace='', pageCellPad='', pageAlign='',columnWidth='', panelObjectPath='', panelObjectType='object', panelSkin=''
##title=edit the content panels config data

# Example code:

# Import a standard function, and get the HTML request and response objects.
from Products.PythonScripts.standard import html_quote
request = container.REQUEST
RESPONSE =  request.RESPONSE

pageIndex=int(pageIndex)
columnIndex=int(columnIndex)
panelIndex=int(panelIndex)
if request.has_key('changePageInfo'):
  context.changePageInfo(pageIndex=pageIndex, 
                         pageTitle=pageTitle, 
                         pageWidth=pageWidth, 
                         pageCellSpace=pageCellSpace, 
                         pageCellPad=pageCellPad, 
                         pageAlign=pageAlign)
elif request.has_key('addColumn'):
  context.addColumn(pageIndex=pageIndex)
elif request.has_key('addPage'):
  pageIndex = context.addPage()
elif request.has_key('deletePage'):
  pageIndex = context.deletePage(pageIndex=pageIndex)
elif request.has_key('deleteColumn'):
  context.deleteColumn(pageIndex=pageIndex, columnIndex=columnIndex)
elif request.has_key('insertPanel'):
  context.insertPanel(pageIndex=pageIndex, columnIndex=columnIndex, panelIndex=panelIndex, 
                   panelObjectType=panelObjectType, panelObjectPath=panelObjectPath, panelSkin=panelSkin)
elif request.has_key('changePanel'):
  context.changePanel(pageIndex=pageIndex, columnIndex=columnIndex, panelIndex=panelIndex, 
                   panelObjectType=panelObjectType, panelObjectPath=panelObjectPath, panelSkin=panelSkin)
elif request.has_key('deletePanel'):
  context.deletePanel(pageIndex=pageIndex, columnIndex=columnIndex, panelIndex=panelIndex)
else:  # request.has_key('changeColumnWidth'): # i found change wolumn width with 'enter' keyin will not set the param :-(
  context.changeColumnWidth(pageIndex=pageIndex, columnIndex=columnIndex, columnWidth=columnWidth)

context.REQUEST.RESPONSE.redirect('%s/contentpanels_edit_form' 
    	  % context.absolute_url() + '?pageIndex=%d'%pageIndex )
