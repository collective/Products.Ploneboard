"""
Author: kapil thangavelu <k_vertigo@objectrealms.net>
"""
from cgi import escape
from types import IntType, FloatType, ListType

from Interfaces import IMetadataSetExporter

from Element import MetadataElement
from XMLType import serialize
from utils import StringBuffer, make_lookup

class MetadataSetExporter:
    """
    for exporting a metadata set definition
    """
    __implements__ = IMetadataSetExporter

    def __init__(self, set):
        self.set = set

    def __call__(self, out=None):

        ext_out = 1
        if out is None:
            ext_out = 0
            out = StringBuffer()

        print >> out, '<?xml version="1.0" encoding="iso-8859-1"?>\n\n'
        print >> out, '<metadata_set id="%s" ns_uri="%s" ns_prefix="%s">' % (
            self.set.getId(),
            self.set.metadata_uri,
            self.set.metadata_prefix
            )

        out.write('<title>%s</title>\n' % (escape(self.set.getTitle(), 1)))
        out.write('<description>%s</description>\n'
                   % (escape(self.set.getDescription(), 1)))

        for e in self.set.getElements():

            print >> out, '  <metadata_element id="%s">' % e.getId()
            print >> out, '   <index_type>%s</index_type>' % e.index_type
            print >> out, '   <index_p>%s</index_p>' % e.index_p
            print >> out, '   <field_type>%s</field_type>' % e.field_type
            print >> out, '   <acquire_p>%s</acquire_p>' % e.acquire_p
            print >> out, '   <read_only_p>%s</read_only_p>' % e.read_only_p

            g = e.read_guard

            print >> out, '   <read_guard>'
            print >> out, '     <roles>%s</roles>' % g.getRolesText()
            print >> out, '     <permissions>%s</permissions>' \
                          % g.getPermissionsText()
            print >> out, '     <expr>%s</expr>' % g.getExprText()
            print >> out, '   </read_guard>'

            g = e.write_guard
            print >> out, '   <write_guard>'
            print >> out, '     <roles>%s</roles>' % g.getRolesText()
            print >> out, '     <permissions>%s</permissions>' \
                          % g.getPermissionsText()
            print >> out, '     <expr>%s</expr>' % g.getExprText()
            print >> out, '   </write_guard>'

            f = e.field

            print >> out, '   <field_values>'

            for k, v in f.values.items():
                if v is None:
                    continue
                if isinstance(v, IntType):
                    out.write('        ' \
                              '<value key="%s" type="%s" value="%d" />\n'
                               % (k, 'int', v))
                elif isinstance(v, FloatType):
                    out.write('        ' \
                              '<value key="%s" type="%s" value="%d" />\n'
                              % (k, 'float', v))
                elif isinstance(v, ListType):
                    out.write('        ' \
                              '<value key="%s" type="%s" value="%s" />\n'
                              % (k, 'list', escape(str(v), 1)))
                else:
                    out.write('        ' \
                              '<value key="%s" type="str" value="%s" />\n'
                              % (k, escape(str(v), 1)))

            print >> out, '   </field_values>'

            print >> out, '   <field_tales>'
            for k,v in f.tales.items():
                if v is None:
                    continue
                # FIXME: we get to the actual "source" for the TALESMethod by
                # getting its _text
                # Needs a different way of retrieving this value?
                print >> out.write('     <value key="%s">%s</value>\n'
                                   % (k, escape(getattr(v, '_text', ''), 1)))
            print >> out, '   </field_tales>'

            print >> out, '   <field_messages>'
            for message_key in f.get_error_names():
                out.write('     <message name="%s">%s</message>\n' % (
                    escape(message_key, 1),
                    escape(f.get_error_message(message_key), 1)
                    )
                )

            print >> out, '   </field_messages>'

            print >> out, '   <index_args>'
            for k,v in e.index_constructor_args.items():
                out.write('     <value key="%s">%s</value>\n'
                          % (k, escape(str(v), 1)))
            print >> out, '   </index_args>'

            print >> out, '  </metadata_element>'



        print >> out, '</metadata_set>'

        if ext_out:
            return out

        return out.getvalue()

class ObjectMetadataExporter:
    """
    for exporting the metadata of an object, returns
    an xml fragement.

    XXX encoding issues
    XXX file/image binary metadata issues
    """

    def __init__(self, binding, sets):
        self.binding = binding
        self.sets = sets

    def __call__(self, out=None):

        external_out = not not out

        if out is None:
            out = StringBuffer()

        out.write('<metadata \n')

        for set in self.sets:
            out.write('    xmlns:%s="%s"\n'
                      % (set.metadata_prefix, set.metadata_uri))
        out.write('      >')

        for set in self.sets:
            sid = set.getId()
            prefix = set.metadata_prefix
            check = make_lookup(set.objectIds(MetadataElement.meta_type))
            data = self.binding._getData(sid)

            for k,v in data.items():
                # with updates its possible that certain annotation data
                # is no longer part of the metadata set, so we filter it out.
                if not check(k):
                    continue

                out.write(u'      <%s:%s>%s</%s:%s>\n'
                          % (prefix, k, serialize(v), prefix, k))

        out.write('</metadata>\n')

        if external_out:
            return None

        return out.getvalue()
