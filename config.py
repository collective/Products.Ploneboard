from Globals import package_home
import os, os.path

PKG_NAME = "CMFMember"
SKIN_NAME = "member"

GLOBALS = globals()
HOMEDIR = package_home(GLOBALS)
TARGET_DIR = os.path.join(HOMEDIR, 'skins', SKIN_NAME)

def getVersion():
    src_path = package_home(GLOBALS)
    f =  file(os.path.join(src_path, 'version.txt'))
    return f.read()

VERSION = getVersion()

DEFAULT_WORKFLOW = 'member_auto_workflow'
DEFAULT_TYPE = 'Member'
DEFAULT_CATALOGS = ['member_catalog', 'portal_catalog',]

DEPENDENCIES = ['Archetypes']
Z_DEPENDENCIES = ['PortalTransforms', 'MimetypesRegistry', 'ZCatalog']
