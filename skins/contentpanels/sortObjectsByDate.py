## Script (Python) "sortObjectsByDate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=objVals=[]
##title=sorts objects by date
##


# modify to sort by date

sorted=()

if objVals:
    objVals.sort( lambda x, y: cmp(y.ModificationDate() , x.ModificationDate()) )

sorted=objVals[:]

return sorted
