from AccessControl import ClassSecurityInfo
from Products.Archetypes.Widget import DecimalWidget, IntegerWidget, LinesWidget, StringWidget

class ReadOnlyFloatWidget(DecimalWidget):
    _properties = DecimalWidget._properties.copy()
    _properties.update({
        'macro' : "read_only_float_widget",
        })
    security = ClassSecurityInfo()

class ReadOnlyIntegerWidget(IntegerWidget):
    _properties = IntegerWidget._properties.copy()
    _properties.update({
        'macro' : "read_only_integer_widget",
        })
    security = ClassSecurityInfo()

class ReadOnlyLinesWidget(LinesWidget):
    _properties = LinesWidget._properties.copy()
    _properties.update({
        'macro' : "read_only_lines_widget",
        })
    security = ClassSecurityInfo()

class ReadOnlyStringWidget(StringWidget):
    _properties = StringWidget._properties.copy()
    _properties.update({
        'macro' : 'read_only_string_widget',
        })
    security = ClassSecurityInfo()


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
