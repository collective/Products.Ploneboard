## Controller Python Script "addI18NLanguageObject"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj_language=None, obj_type_name=None
##title=
##

if obj_language is None:
    raise Exception

if obj_type_name is None:
    obj_type_name=context.getTypeInfo().getId()

context.createLanguageObject(id=obj_language, type_name=obj_type_name)

