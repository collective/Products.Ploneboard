from BibrefStyleExample import BibrefStyleExample, manage_addBibrefStyleExample

def initialize(context):
    context.registerClass(BibrefStyleExample,
                          constructors = (manage_addBibrefStyleExample,),
                          )