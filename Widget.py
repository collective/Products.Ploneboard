from Products.Archetypes.Widget import DecimalWidget, IntegerWidget, LinesWidget, StringWidget

class ReadOnlyFloatWidget(DecimalWidget):
    _properties = DecimalWidget._properties.copy()
    _properties.update({
        'macro' : "read_only_float_widget",
        })

class ReadOnlyIntegerWidget(IntegerWidget):
    _properties = IntegerWidget._properties.copy()
    _properties.update({
        'macro' : "read_only_integer_widget",
        })

class ReadOnlyLinesWidget(LinesWidget):
    _properties = LinesWidget._properties.copy()
    _properties.update({
        'macro' : "read_only_lines_widget",
        })

class ReadOnlyStringWidget(StringWidget):
    _properties = StringWidget._properties.copy()
    _properties.update({
        'macro' : 'read_only_string_widget',
        })


from Products.Archetypes.Registry import registerWidget

registerWidget(ReadOnlyFloatWidget,
               title='ReadOnlyFloat',
               description='Shows read-only float',
               used_for=('Products.Archetypes.Field.FloatField',)
               )

registerWidget(ReadOnlyIntegerWidget,
               title='ReadOnlyInteger',
               description='Shows read-only integer',
               used_for=('Products.Archetypes.Field.IntegerField',)
               )

registerWidget(ReadOnlyLinesWidget,
               title='ReadOnlyLines',
               description='Shows read-only lines',
               used_for=('Products.Archetypes.Field.LinesField',)
               )

registerWidget(ReadOnlyStringWidget,
               title='ReadOnlyString',
               description='Shows read-only text',
               used_for=('Products.Archetypes.Field.StringField',)
               )
