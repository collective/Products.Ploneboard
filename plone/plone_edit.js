
// Plone-specific editing scripts.  Referenced by plone/bottom.pt.
// The variable "ui_url" is provided by common/header.pt.

function plone_edit(element) {
  var path = escape(element.getAttribute("source_path"));
  window.document.location = path + "/edit_compo_element"; 
}

function plone_add(target) {
  // Note that target_index is also available.
  var path = escape(target.getAttribute("target_path"));
  // alert(path);
  draweropen(path);
}
