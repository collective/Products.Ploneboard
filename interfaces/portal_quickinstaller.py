from interface import Interface, Attribute

class IQuickInstallerTool(Interface):
    ''' the QuickInstaller Tool 
        contains 'InstalledProduct' instances
    '''

    id = Attribute('id', 'Must be set to "portal_quickinstaller"')
    
    def listInstallableProducts(skipInstalled=1):
        ''' list candidate CMF products for installation -> list of dicts with 
            keys:(id,hasError,status)'''

    def listInstalledProducts(showHidden=0):
        ''' returns a list of products that are installed -> list of dicts with 
            keys:(id,hasError,status,,isLocked,isHidden)'''

    def isProductInstallable(productname):
        ''' is the product directory present and ready for installation '''

    def isProductAvailable(productname):
        ''' is the product directory present (to check if it has been deleted 
            from the Filesystem '''
        
    def installProduct(p,locked=0,hidden=0,swallowExceptions=0):
        ''' installs a product by name 
            throws AlreadyInstalled exception, if components of the product are 
            already installed
            
            if swallowExceptions is true, exceptions are caught and logged
        '''

    def installProducts(products=[], stoponerror=0, REQUEST=None):
        ''' installs the products specified in the products list'''

    def getProductFile(p,fname='readme.txt'):
        ''' returns the content of a file of the product case-insensitive, if it
             does not exist -> None '''

    def getProductReadme(p):
        ''' returns the readme file of the product case-insensitive '''

    def getProductVersion(p):
        ''' returns the version string stored in version.txt'''

    def isProductInstalled(productname):
        ''' checks wether a product is installed (by name) '''

    def notifyInstalled(p,locked=1, hidden=0, **kw):
        ''' marks a product that has been installed without QuickInstaller
         as installed 
         if locked is set -> the prod cannot be uninstalled
         if hidden is set -> the prod is not listed in the UI
         the **kw param is passed to the constructor of InstalledProduct
         '''


    def uninstallProducts( products, cascade=['types','skins','actions',
        'portalobjects','workflows','slots','registrypredicates'],REQUEST=None):
        ''' removes a list of products, cascade defines which items created by 
            the install shall be uninstalled '''

    def reinstallProducts( products, REQUEST=None):
        ''' reinstalls a list of products, the main difference to 
            ininstall/reinstall is that it does not remove portal objects 
            created  during install (e.g. tools, etc.)'''
        
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
        workflows=[],leftslots=[],rightslots=[],registrypredicates=[],logmsg='',
        status='installed', error=0, locked=0, hidden=0):
        ''' constructor '''
        
    def update(types=[],skins=[],actions=[],portalobjects=[],workflows=[],
        leftslots=[],rightslots=[],registrypredicates=[],logmsg='',
        status='installed',error=0,locked=0,hidden=0):
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
        
    def uninstall(cascade=['types','skins','actions','portalobjects',
            'workflows','slots','registrypredicates'],REQUEST=None):
        '''uninstalls the prod and removes its deps
           the parameter 'cascade' specifies what should be deleted while 
           uninstalling the product
           
           if the Product has an uninstall() method in its Install.py it gets 
           called automatically
        '''
    def getInstalledVersion():
        ''' returns the version of the prod in the moment of installation '''


