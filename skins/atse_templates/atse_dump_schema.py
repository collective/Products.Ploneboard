##parameters=schema_id

# Dump schema
#
# This code stinks but it works :-)

print "######################################################################"
print "# Schema created by ATSchemaEditorNG                                 #"
print "# (C) 2004, ZOPYX Software Development and Consulting Andreas Jung   #"
print "# Published under the Lesser GNU Public License LGPL V 2.1           #"
print "######################################################################"
print 
print "from Products.Archetypes.public import *"
print 
print 
print "schema = BaseSchema + Schema(("


schema = context.atse_getSchemaById(schema_id)

for schemata_name in context.atse_getSchemataNames(schema_id):
    schemata = context.atse_getSchemata(schema_id, schemata_name)
    for f in schemata.fields():
        widget = f.widget
        s = '\t%s("%s", \n' % (context.atse_getFieldType(f), f.getName())
        s += '\t\tschemata="%s",\n' % schemata_name 
        s += '\t\trequired=%s,\n' % f.required
        s += '\t\twidget=%s(\n' % widget.getName()
        s += '\t\t\tlabel="%s",\n' % widget.label
        s += '\t\t\tvisible=%s,\n' % widget.visible
        s += '\t\t\tlabel_msgid="%s",\n' % getattr(widget, 'label_msgid', '')
        s += '\t\t\ti18n_domain="%s",\n' % getattr(widget, 'i18n_domain', '')

        if widget.getName() == 'TextAreaWidget':
            attrs = ('rows', 'cols', 'validators')
        else:
            attrs = ('size', 'validators')

        for attr in attrs:
            if hasattr(widget, attr):
                value = getattr(widget, attr)
                if attr == 'validators' and isinstance(value, tuple):
                    value = filter(None, value)
                    if not value: value = ()
                if attr in ('rows', 'cols', 'size'): value = int(value)
                if isinstance(value, int ) or isinstance(value, tuple):
                    s += '\t\t\t%s=%s,\n' % (attr, value)
                else:
                    s += '\t\t\t%s="%s",\n' % (attr, value)
        s += '\t\t), \n'
        s += '\t), \n'
        print s

print  "))"
        
return printed
