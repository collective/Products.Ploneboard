
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

       
