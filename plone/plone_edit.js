
// Plone-specific editing scripts.  Referenced by plone/bottom.pt.
// The variable "ui_url" is provided by common/header.pt.

function plone_edit(element) {
  var path = escape(element.getAttribute("source_path"));
  window.document.location = path + "/edit_compo_element"; 
}

function plone_add(target) {
  // Note that target_index is also available.
  var path = escape(target.getAttribute("target_path"));
  draweropen(path);
}

function plone_change_viewlet(element, viewlet) {
  // Note that target_index is also available.
  var path = escape(element.getAttribute("source_path"));
  window.document.location = path + "/change_viewlet?viewletId=" + viewlet;
}


function composite_pack_prepare_element_menu(header) {
  if (!pd_selected_item) {
    allowed_viewlets = null;
  }
  else {
    allowed_viewlets = pd_selected_item.getAttribute('allowed_viewlets');
  }
  header.parentNode.setAttribute("allowed_viewlets", allowed_viewlets);
  composite_prepare_element_menu(header);
  return true;
}

function composite_prepare_change_viewlet_menu(header) {
  // Prepares the header of the element context menu.
  var node, menuItem, slots, i;
  while (header.childNodes.length)
    header.removeChild(header.childNodes[0]);
  // change viewlet header
  menuItem = document.createElement("div");
  menuItem.setAttribute("class", "context-menu-header");
  node = document.createTextNode('Select viewlet');
  menuItem.appendChild(node);
  header.appendChild(menuItem);
  // loop on viewlets
  parent = header.parentNode;
  if (parent.getAttribute("allowed_viewlets")) {
    slots = parent.getAttribute("allowed_viewlets").split(" ");
    for (i = 0; i < slots.length; i++) {
      menuItem = document.createElement("div");
      menuItem.setAttribute("class", "context-menu-item");
      onmouseup = "plone_change_viewlet(pd_selected_item, '" + slots[i] + "')";
      menuItem.setAttribute("onmouseup", onmouseup);
      node = document.createTextNode(slots[i]);
      pd_setupContextMenuItem(menuItem);
      menuItem.appendChild(node);
      header.appendChild(menuItem);
    }
  }
  return true;
}

