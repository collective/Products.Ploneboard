from Globals import package_home
import os, os.path
import utils

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

######################################################################
# CONFIGURATION
# EMAIL_IDS_VALID = False
# Setting this to true will allow for characters valid in emails to
# appear througout the site as valid ids. Given the limited nature of
# this patch this impacts tradational content as well as
# user_ids. This shouldn't be a problem for most people, but it is
# disabled byt default
EMAIL_IDS_VALID = False
#
if EMAIL_IDS_VALID:
    utils.patch_ids()
######################################################################
