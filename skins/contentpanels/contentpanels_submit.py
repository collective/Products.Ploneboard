## Script (Python) "contentpanels_submit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=pageIndex=0, pageInfo, columnInfos=[], CPI0=[], CPI1=[], CPI2=[], CPI3=[], CPI4=[], CPI5=[], CPI6=[], CPI7=[], CPI8=[], CPI9=[]
##title=edit the submitted config data

# what is parameter CPIX (CPI0, CPI1, ..)
# CPI = Column Panels Info
# now we alow only 10 columns for simplify, it is enough, right?

request = container.REQUEST
RESPONSE =  request.RESPONSE

pageIndex=int(pageIndex)
columnCount=len(columnInfos)
CPIs=[CPI0, CPI1, CPI2, CPI3, CPI4, CPI5, CPI6, CPI7, CPI8, CPI9]

context.changePageInfo(pageIndex=pageIndex, 
                       pageTitle=pageInfo.pageTitle, 
                       pageWidth=pageInfo.pageWidth, 
                       pageCellSpace=pageInfo.pageCellSpace, 
                       pageCellPad=pageInfo.pageCellPad, 
                       pageAlign=pageInfo.pageAlign)

for columnIndex in range(columnCount):
    context.changeColumnWidth(pageIndex=pageIndex, columnIndex=columnIndex, columnWidth=columnInfos[columnIndex].columnWidth)
    panelCount = len(CPIs[columnIndex])
    for panelIndex in range(panelCount):
        panelInfo = CPIs[columnIndex][panelIndex]
        context.changePanel(pageIndex=pageIndex, 
                            columnIndex=columnIndex, 
                            panelIndex=panelIndex,
                            panelObjectViewlet=panelInfo.panelObjectViewlet, 
                            panelObjectPath=panelInfo.panelObjectPath, 
                            panelSkin=panelInfo.panelSkin)

context.REQUEST.RESPONSE.redirect('%s/contentpanels_config_form' 
    	  % context.absolute_url() + '?pageIndex=%d'%pageIndex )
