
// Plone-specific editing scripts.  Referenced by plone/bottom.pt.
// The variable "ui_url" is provided by common/header.pt.
function plone_edit(element) {
  var path = element.getAttribute("full_path");
  window.document.location = path + "/edit_compo_element"; 
}

function plone_add(target) {
  // Note that target_index is also available.
  var target_path = target.getAttribute("target_path");
  var target_index = target.getAttribute("target_index");
  draweropen(target_path, target_index);
}

function plone_add_title(target) {
  // Note that target_index is also available.
  var form = document.forms.modify_composites;
  var compopage_path = form.elements.composite_path.value;
  var title = prompt('Input the title value', 'a title');
  var target_path = target.getAttribute("target_path");
  var target_index = target.getAttribute("target_index");
  url = "createCompoTitle?target_path=" + target_path;
  url = url + "&target_index=" + target_index;
  url = url + "&compopage_path=" + compopage_path;
  url = url + "&title=" + title;
  window.document.location = url;
}

function plone_change_viewlet(element, viewlet) {
  var form, url, element_path, compopage_path;
  form = document.forms.modify_composites;
  compopage_path = form.elements.composite_path.value;
  element_path = element.getAttribute("full_path");
  url = element_path + "/change_viewlet?viewletId=" + viewlet;
  url = url + "&compopage_path=" + compopage_path;
  window.document.location = url;
}


function composite_pack_prepare_element_menu(header) {
  if (!pd_selected_item) {
    allowed_viewlets_ids = null;
    allowed_viewlets_titles = null;
  }
  else {
    allowed_viewlets_ids = pd_selected_item.getAttribute('allowed_viewlets_ids');
    allowed_viewlets_titles = pd_selected_item.getAttribute('allowed_viewlets_titles');
  }
  header.parentNode.setAttribute("allowed_viewlets_ids", allowed_viewlets_ids);
  header.parentNode.setAttribute("allowed_viewlets_titles", allowed_viewlets_titles);
  composite_prepare_element_menu(header);
  return true;
}

function composite_prepare_change_viewlet_menu(header) {
  // Prepares the header of the element context menu.
  var node, menuItem, i, parent;
  var viewlets_titles, viewlets_ids;
  while (header.childNodes.length)
    header.removeChild(header.childNodes[0]);
  // change viewlet header
  menuItem = document.createElement("div");
  menuItem.className = "context-menu-header";
  node = document.createTextNode('Select viewlet');
  menuItem.appendChild(node);
  header.appendChild(menuItem);
  // loop on viewlets
  parent = header.parentNode;
  if (parent.getAttribute("allowed_viewlets_ids")) {
    viewlets_ids = parent.getAttribute("allowed_viewlets_ids").split(" ");
    viewlets_titles = parent.getAttribute("allowed_viewlets_titles").split("%");
    for (i = 0; i < viewlets_ids.length; i++) {
      menuItem = document.createElement("div");
      plone_setup_viewlet_menu_item(menuItem, viewlets_ids[i], viewlets_titles[i]);
      header.appendChild(menuItem);
    }
  }
  return true;
}

function plone_setup_viewlet_menu_item(menuItem, viewlet_id, viewlet_title) {
      menuItem.className = "context-menu-item";
      menuItem.onmouseup = function() {
          plone_change_viewlet(pd_selected_item, viewlet_id);
      };
      node = document.createTextNode(viewlet_title);
      menuItem.appendChild(node);
      pd_setupContextMenuItem(menuItem);
}

