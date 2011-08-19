function AddAttachmentField(inp) {
  var parent = inp.parentNode;

  if (parent.attachments==null) {
    parent.attachments=1;
    parent.maxattachments=parent.getAttribute("attachments");
  }

  var e = document.createElement("input");
  e.setAttribute("type", "file");
  e.setAttribute("name", "files:list");
  e.setAttribute("size", "30");
  parent.insertBefore(e, inp);

  e=document.createElement("br");
  parent.insertBefore(e, inp);

  parent.attachments++;

  if (parent.attachments>=parent.maxattachments)
    parent.removeChild(inp);

  return false;
}


