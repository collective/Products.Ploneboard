from MinimalFormat import MinimalFormat, manage_addMinimalFormat


def initialize(context):
    context.registerClass(MinimalFormat,
                          constructors = (manage_addMinimalFormat,),
                          ) 
