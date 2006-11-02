## Controller Validator "validate_add_comment"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Validates a posting
##

def FileSize(file):
    if hasattr(file, 'size'):
        size=file.size
    elif hasattr(file, 'tell'):
        file.seek(0, 2)
        size=file.tell()
        file.seek(0)
    else:
        try:
            size=len(file)
        except TypeError:
            size=0

    return size/1024

text = context.REQUEST.get('text', '');

if len(text) <= 0:
    state.setError("text", "No content entered", new_status="failure")

files=context.REQUEST.get('files', [])
maxsize=context.getConversation().getMaxAttachmentSize()

if maxsize!=-1:
    for file in files:
        if FileSize(file)>maxsize:
            state.setError("files", "Attachment is too large", new_status="failure")
            break

if state.getErrors():
    return state.set(
            portal_status_message='Please correct the indicated errors.')

return state
