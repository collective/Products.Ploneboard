##########################################################################
#                                                                        #
#    copyright (c) 2004 Royal Belgian Institute for Natural Sciences     #
#                       and contributors                                 #
##########################################################################

from Minimal import MinimalBibrefStyle, manage_addMinimalBibrefStyle
from Chicago import ChicagoBibrefStyle, manage_addChicagoBibrefStyle
from MLA import MLABibrefStyle, manage_addMLABibrefStyle
from APA import APABibrefStyle, manage_addAPABibrefStyle
from Harvard import HarvardBibrefStyle, manage_addHarvardBibrefStyle


def initialize(context):
    context.registerClass(MinimalBibrefStyle,
                          constructors = (manage_addMinimalBibrefStyle,),
                          ) 
    context.registerClass(ChicagoBibrefStyle,
                          constructors = (manage_addChicagoBibrefStyle,),
                          ) 
    context.registerClass(MLABibrefStyle,
                          constructors = (manage_addMLABibrefStyle,),
                          ) 
    context.registerClass(APABibrefStyle,
                          constructors = (manage_addAPABibrefStyle,),
                          ) 
    context.registerClass(HarvardBibrefStyle,
                          constructors = (manage_addHarvardBibrefStyle,),
                          ) 
