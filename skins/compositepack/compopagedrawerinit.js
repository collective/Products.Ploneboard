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

function cp_initdrawer(link_libraries_uri, search_links_uri, compopagepath) {
    
    var linktool = new LinkTool();
    var link_xsl_uri = 'compopagedrawers/selectdrawer.xsl';

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

