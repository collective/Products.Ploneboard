## Script (Python) "sortObjectValues"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=objVals=[]
##title=sorts and pre-filters objects

# modify to sort by date

sorted=()

if objVals:
    objVals.sort( lambda x, y: cmp(y.ModificationDate() , x.ModificationDate()) )

sorted=objVals[:]

return sorted
