from interface import Interface, Attribute

class IQuickInstallerTool(Interface):
    ''' the QuickInstaller Tool 
        contains 'InstalledProduct' instances
    '''

    id = Attribute('id', 'Must be set to "portal_quickinstaller"')
    
    def listInstallableProducts(skipInstalled=1):
        ''' returns a list of products that are installed -> list of strings'''

    def installProducts(products=[], stoponerror=0, REQUEST=None):
        ''' installs the products specified in the products list'''

    def isProductInstalled(productname):
        ''' checks wether a product is installed (by name) '''

    def notifyInstalled(p,locked=1, hidden=0, **kw):
        ''' marks a product that has been installed without QuickInstaller
         as installed 
         the **kw param is passed to the constructor of InstalledProduct
         '''

    def installProduct(p):
        ''' installs a product by name '''

    def uninstallProducts( products, REQUEST=None):
        ''' removes a list of products '''
        
class IInstalledProduct(Interface):
    ''' represents the installed product 
        is contained inside the QuickInstallerTool '''        

    id = Attribute('id', 'Must be set to the same name as the product directory')

    types = Attribute('types','default: []')
    skins = Attribute('types','default: []')
    actions = Attribute('types','default: []')
    portalobjects = Attribute('types','default: []')
    workflows = Attribute('types','default: []')
    leftslots = Attribute('types','default: []')
    rightslots = Attribute('types','default: []')

    def __init__(id,types=[],skins=[],actions=[],portalobjects=[],
        workflows=[],leftslots=[],rightslots=[],logmsg='',status='installed',
        error=0,locked=0, hidden=0):
        ''' constructor '''
        
    def update(types=[],skins=[],actions=[],portalobjects=[],workflows=[],
        leftslots=[],rightslots=[],logmsg='',status='installed',error=0,locked=0,hidden=0):
        ''' updates the product attributes '''
        
    def log(logmsg):
        ''' adds a log to the transcript '''
        
    def hasError():
        ''' returns if the prod is in error state '''

    def isLocked():
        ''' is the product locked for uninstall '''

    def isHidden():
        ''' is the product hidden'''
    
    def isInstalled():
        ''' determines if the product is in already installed '''
        
    def getTranscriptAsText():
        ''' return the product's install log as plain text '''
        
    def uninstall(cascade=['types','skins','actions','portalobjects','workflows','slots'],REQUEST=None):
        '''uninstalls the prod and removes its deps
           the parameter 'cascade' specifies what should be deleted while uninstalling the product
           
           if the Product has an uninstall() method in its Install.py it gers called automatically
        '''
        