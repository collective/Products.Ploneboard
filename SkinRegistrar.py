# gracefully donated by Gilles Lenfant from pilotsystems.net

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.ExternalMethod.ExternalMethod import ExternalMethod


from StringIO import StringIO

from App.Common import package_home
import os

class SkinRegistrar:
    """
    Controls (un)registering of a layer in the skins tool:
     - the layer in the content of the skin tool
     - the layer in the path of all skins
    @author: U{Gilles Lenfant <glenfant@bigfoot.com>}
    @version: 0.1.0
    @ivar _layer: Name of the Product's subdirectory that contains
        the various layers for the Product.
    @type _layer: string
    @ivar _prodglobals: Globals from this Product.
    @type _propglobals: mapping object
    """

    def __init__(self, skinsdir, prodglobals):
        """Constructor
        @param skinsdir: Name of the Product's subdirectory that
            contains the various layers for the Product.
        @type skinsdir: string
        @param prodglobals: Globals from this Product.

            should be provided by Product's C{__init__.py} like this:

            C{product_globals = globals()}

        @type propglobals: mapping object
        @return: None
        """

        self._skinsdir = skinsdir
        self._prodglobals = prodglobals
        return

    def getLayersToAdd(self):
        layerName = self._prodglobals['__name__'].split('.')[-1]
        layerpath = os.path.join(package_home(self._prodglobals),'skins',layerName)
        subLayerNames=[p for p in os.listdir(layerpath) if os.path.isdir(os.path.join(layerpath,p)) and p != 'CVS']
        return [layerName+'/'+l for l in subLayerNames] + [layerName]

    def install(self, aq_obj):
        """Installs and registers the skin resources
        @param aq_obj: object from which cmf site object is acquired
        @type aq_obj: any Zope object in the CMF
        @return: Installation log
        @rtype: string
        """

        rpt = '=> Installing and registering layers from directory %s\n' % self._skinsdir
        skinstool = getToolByName(aq_obj, 'portal_skins')

        # Create the layer in portal_skins

        if self._skinsdir not in skinstool.objectIds():
            addDirectoryViews(skinstool, self._skinsdir, self._prodglobals)
            rpt += 'Added "%s" directory view to portal_skins\n' % self._skinsdir
        else:
            rpt += 'Warning: directory view "%s" already added to portal_skins\n' % self._skinsdir

        # Insert the layer in all skins
        # XXX FIXME: Actually assumes only one layer directory with the name of the Product
        # (should be replaced by a smarter solution that finds individual Product's layers)

        
        layersToAdd=self.getLayersToAdd()
        
        skins = skinstool.getSkinSelections()
        
        for skin in skins:
            layers = skinstool.getSkinPath(skin)
            layers = [layer.strip() for layer in layers.split(',')]
            
            for layerName in layersToAdd:
                if layerName not in layers:
                    try:
                        layers.insert(layers.index('content'), layerName)
                    except ValueError:
                        layers.append(layerName)
                    rpt += 'Added "%s" to "%s" skin\n' % (layerName, skin)
                else:
                    rpt += '! Warning: skipping "%s" skin, "%s" is already set up\n' % (skin, type)

                skinstool.addSkinSelection(skin, ','.join(layers))


        return rpt

    def uninstall(self, aq_obj):
        """Uninstalls and unregisters the skin resources
        @param aq_obj: object from which cmf site object is acquired
        @type aq_obj: any Zope object in the CMF
        @return: Uninstallation log
        @rtype: string
        """

        rpt = '=> Uninstalling and unregistering %s layer\n' % self._skinsdir
        skinstool = getToolByName(aq_obj, 'portal_skins')

        # Removing layer from portal_skins
        # XXX FIXME: Actually assumes only one layer directory with the name of the Product
        # (should be replaced by a smarter solution that finds individual Product's layers)

        layerName = self._prodglobals['__name__'].split('.')[-1]
        if layerName in skinstool.objectIds():
            skinstool.manage_delObjects([layerName])
            rpt += 'Removed "%s" directory view from portal_skins\n' % layerName
        else:
            rpt += '! Warning: directory view "%s" already removed from portal_skins\n' % layerName

        # Removing from skins selection

        skins = skinstool.getSkinSelections()
        for skin in skins:
            layers = skinstool.getSkinPath(skin)
            layers = [layer.strip() for layer in layers.split(',')]
            
            for layerName in self.getLayersToAdd():
                if layerName in layers:
                    layers.remove(layerName)
                    rpt += 'Removed "%s" from "%s" skin\n' % (layerName, skin)
                else:
                    rpt += 'Skipping "%s" skin, "%s" is already removed\n' % (skin, layerName)

        skinstool.addSkinSelection(skin, ','.join(layers))

        return rpt
# /class PloneSkinRegistrar
 