from Products.CMFMember import ControlTool as MigrationTool
from ImportMembers import ImportSetup

MigrationTool.registerSetupWidget(ImportSetup)

# uncomment if you want to register the widget with Plone migration tool
# but you don't want that, CMFMember migration tool is prettier :)
from Products.CMFPlone import MigrationTool as PloneMigrationTool
PloneMigrationTool.registerSetupWidget(ImportSetup)
