CMFQuickInstallerTool
==================

Features
----------

This tool is independent from the former CMFQuickInstaller.
The main difference to CMFQuickInstaller the tracking of
what a product creates during install. 

Therefore it has to be installed as a tool inside a CMF portal,
where it stores the infotmation about the installed products.

The requirements for a product to be installable with
QuickInstallerTool are quite simple (almost all existing CMF 
products fulfill them):
the product has to implement an external mtehod 'Install' in 
a python module 'Install.py' in its Extensions directory.

Products can be uninstalled and QuickInstellerTool removes
the following items a product creates during install:

portal types,
portal skins,
portal actions,
portalobjects (objects created in the root of the portal),
workflows,
left and right slots (also checks them only for the portal)

Attention: QuickInstallerTool just tracks which objects are 
ADDED, but not what is changed or deleted.

second Attention:
QuickInstallerTool just can uninstall products that are 
installed via QuickInstallerTool

Installation
------------

- Drop the CMFQuickInstallerTool into the Products directory.

- inside the portal instanciate a CMF QuickInstaller Tool

Usage:
--------

in the ZMI click on portal_quickinstaller.
the management screen allows you to select products for
installation and uninstallation.
you can browse into the installed products and see what
they created and see the logs of the install process.

for Plone there will be an interface inside the portal so that
it is not necessary to enter thr ZMI for priduct management

