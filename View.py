"""
description: some really ugly default view.. will likely be removed in the
near future in favor of some zpt views

author: kapil thangavelu
"""

from utils import StringBuffer
from ZopeImports import getToolByName

def getForm(binding, set, framed=1, REQUEST=None, errors=None):
    content = binding.content
    elements = set.getElementsFor(content, mode='edit')
    annotations = getToolByName(content, 'portal_annotations')

    if REQUEST is not None and errors is not None:
        data = REQUEST.form.get(set.getId())
    else:
        data = binding._getData(set.getId(), acquire=0)

    out = StringBuffer()

    if framed:
        print >> out, '<form method="POST" action="edit_metadata"' \
                      ' enctype="multipart/form-data">'
        print >> out, '<input type="hidden" name="mset_id" value="%s">' \
                      % set.getId()

    print >> out, '<h2 class="metadata_header">%s</h2>' % set.getTitle()

    if errors is not None:
        print >> out, '<table class="form_errors">'
        for k,v in errors.items():
            print >> out, '<tr><td>%s: %s</td</tr>' % (k,v)
        print >> out, '</table>'

    print >> out, '<table class="metadata_form">'
    for e in elements:
        print >> out, "<tr><td><b>%s</b></td>" % e.title()
        print >> out, "<tr><td>%s</td>" \
                 % e.renderEdit(data.get(e.getId(), None))

    if framed:
        print >> out, '''<tr><td colspan="2">
        <input type="submit" value="edit %s">
        </td></tr>''' % set.getTitle()

    print >> out, '</table>'

    if framed:
        print >> out, '</form>'

    return out.getvalue()

def getView(binding, set, framed=1):
    content = binding.content
    elements = set.getElementsFor(content, mode='view')
    annotations = getToolByName(content, 'portal_annotations')
    data = annotations.getAnnotations(content, set.metadata_uri)
    out = StringBuffer()

    print >> out, '<table class="metadata_view">'

    for e in elements:
        print >> out, "<tr><td><b>%s</b></td>" % e.title()
        print >> out, "<tr><td>%s</td></td>" \
                      % renderField(e, e.getId(), data.get(e.getId(), None))

    print >> out, '</table>'
    return out.getvalue()

def renderField(element, key, value):
    # XXX formulator specific
    view_method = getattr(element.field.widget, 'render_view', None)
    if view_method is not None:
        return view_method(element.field, key, value)
    elif not value: #shizer
        return ''
    else:
        return str(value)
