// $Id: compopagedrawer.js,v 1.6 2004/06/30 08:22:44 godchap Exp $

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
          var page_w = window.innerWidth || document.body.clientWidth;
          var page_h = window.innerHeight || document.body.clientHeight;
          // have to check documentElement in some IE6 releases
          var page_x = window.pageXOffset || document.documentElement.scrollLeft || document.body.scrollLeft;
          var page_y = window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop;

          // Choose a location for the menu based on where the user clicked
          if (page_w - e.clientX < drawernode.offsetWidth) {
            // Close to the right edge
            drawernode.style.left = '' + (
              page_x + e.clientX - drawernode.offsetWidth - 1) + 'px';
          }
          else {
            drawernode.style.left = '' + (page_x + e.clientX + 1) + 'px';
          }
          if (page_h - e.clientY < drawernode.offsetHeight) {
            // Close to the bottom
            drawernode.style.top = '' + (
              page_y + e.clientY - drawernode.offsetHeight - 1) + 'px';
          }
          else {
            drawernode.style.top = '' + (page_y + e.clientY + 1) + 'px';
          }
        
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



