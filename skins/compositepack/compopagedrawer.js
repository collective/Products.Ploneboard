// $Id: compopagedrawer.js,v 1.3 2004/05/07 09:54:58 godchap Exp $

//----------------------------------------------------------------------------

//  Depends on kupu 

//  Compatible with rev 4186

//----------------------------------------------------------------------------

function SelectDrawer(tool, xsluri, libsuri, searchuri, compopagepath,
target_path) {
    /* a specific LibraryDrawer for selection of content */


    this.init(tool, xsluri, libsuri, searchuri);

    this.compopagepath = compopagepath;

    this.setTarget = function(target_path) {
        this.target_path = target_path;
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
            this.compopagepath + '&target_path=' + this.target_path;
    };

    
};

SelectDrawer.prototype = new LibraryDrawer;

function CompoDrawerTool() {

    this.openDrawerWithTarget = function(id, target_path) {
        if (this.current_drawer) {
            this.closeDrawer();
            };
        var drawer = this.drawers[id];
        drawer.setTarget(target_path);
        drawer.createContent();
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
    //var link_xsl_uri = 'compopagedrawers/selectdrawer.xsl';

    editor = new fakeEditor();
    drawertool.initialize(editor);

    var selectdrawer = new SelectDrawer(linktool, link_xsl_uri,
                                    link_libraries_uri, search_links_uri,
                                    compopagepath);
    drawertool.registerDrawer('selectdrawer', selectdrawer);
    
};

function draweropen(target_path) {
                    drawertool.openDrawerWithTarget('selectdrawer', target_path); 
};



