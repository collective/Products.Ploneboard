// $Id: compopagedrawer.js,v 1.7 2004/06/30 14:37:47 godchap Exp $

//----------------------------------------------------------------------------

//  Depends on kupu 

//  Compatible with rev 4186

//----------------------------------------------------------------------------

function SelectDrawer(tool, xsluri, libsuri, searchuri, compopagepath,
target_path) {
    /* a specific LibraryDrawer for selection of content */


    this.init(tool, xsluri, libsuri, searchuri);

    this.compopagepath = compopagepath;

    this.setTarget = function(target_path, target_index) {
        this.target_path = target_path;
        this.target_index = target_index;
    };

    this.save = function() {
        var selxpath = '//resource[@selected]';
        var selnode = this.xmldata.selectSingleNode(selxpath);
        if (!selnode) {
            return;
        };

        var uri = selnode.selectSingleNode('uri/text()').nodeValue;
        uri = uri.strip();  // needs kupuhelpers.js

        this.hide();
        window.document.location = uri + '/createCompoElement?compopage_path=' +
            this.compopagepath + '&target_path=' + this.target_path +
            '&target_index=' + this.target_index;
    };

    this.setPosition = function(e){

          // this function adapted from code in pdlib.js in CompositePage
          
          drawernode = document.getElementById('kupu-librarydrawer');
          
          if (!e)
            e = event;
          var page_w = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
          var page_h = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
          // have to check documentElement in some IE6 releases
          var page_x = window.pageXOffset || document.documentElement.scrollLeft || document.body.scrollLeft;
          var page_y = window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop;

          // Choose a location for the menu based on where the user clicked
          var node_top, node_left;
          var drawer_half_w = Math.floor(drawernode.offsetWidth / 2) + 1;
          var drawer_half_h = Math.floor(drawernode.offsetHeight / 2) + 1;
          if (page_w - e.clientX < drawer_half_w) {
            // Close to the right edge
            node_left = page_x + page_w - drawernode.offsetWidth - 1; 
          }
          else {
            node_left = page_x + e.clientX - drawer_half_w;
          }
          if (node_left < page_x) {
              node_left = page_x;
          }
          if (page_h - e.clientY < drawer_half_h) {
            // Close to the bottom
            node_top = page_y + page_h - drawernode.offsetHeight - 1;
          }
          else {
            node_top = page_y + e.clientY - drawer_half_h;
          }
          if (node_top < page_y) {
              node_top = page_y;
          }
          drawernode.style.left = '' + node_left + 'px';
          drawernode.style.top = '' + node_top + 'px';
        
    };    



};

SelectDrawer.prototype = new LibraryDrawer;

function CompoDrawerTool() {

    this.openDrawerWithTarget = function(id, e, target_path, target_index) {
        if (this.current_drawer) {
            this.closeDrawer();
            };
        var drawer = this.drawers[id];
        drawer.setTarget(target_path, target_index);
        drawer.createContent();
        drawer.setPosition(e);
        this.current_drawer = drawer;
    };
};

CompoDrawerTool.prototype = new DrawerTool;



// initialization of drawers

var drawertool = new CompoDrawerTool();

function fakeEditor() {

    this.getBrowserName = function() {
        if (_SARISSA_IS_MOZ) {
            return "Mozilla";
        } else if (_SARISSA_IS_IE) {
            return "IE";
        } else {
            throw "Browser not supported!";
        }
    };    
};

function cp_initdrawer(link_xsl_uri, link_libraries_uri, search_links_uri, compopagepath) {
    
    var linktool = new LinkTool();

    editor = new fakeEditor();
    drawertool.initialize(editor);

    var selectdrawer = new SelectDrawer(linktool, link_xsl_uri,
                                    link_libraries_uri, search_links_uri,
                                    compopagepath);
    drawertool.registerDrawer('selectdrawer', selectdrawer);
    
};

function draweropen(e, target_path, target_index) {
                    drawertool.openDrawerWithTarget('selectdrawer', e, target_path, target_index); 
};



