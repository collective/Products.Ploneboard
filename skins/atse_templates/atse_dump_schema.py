##parameters=schema_id

# dump schema 

print 
print "# Schema created by ATSchemaEditorNG"
print "# (C) 2004, Zope Software Development and Consulting Andreas jung"
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
        s += '\t\twidget=%s(\n' % widget.getName()
        s += '\t\t\tlabel="%s",\n' % widget.label
        s += '\t\t\tlabel_msgid="%s",\n' % getattr(widget, 'label_msgid', '')
        s += '\t\t\ti18n_domain="%s",\n' % getattr(widget, 'i18n_domain', '')
        for attr in ('rows', 'size', 'cols'):
            if hasattr(widget, attr):
                value = getattr(widget, attr)
                if isinstance(value, int):
                    s += '\t\t\t%s=%s,\n' % (attr, value)
                else:
                    s += '\t\t\t%s="%s",\n' % (attr, value)
        s += '\t\t), \n'
        s += '\t), \n'
        print s

print  "))"
        
return printed
