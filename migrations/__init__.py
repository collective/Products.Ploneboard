from Products.CMFMember import ControlTool as MigrationTool
import v1

def null(portal):
    """ This is a null migration, use it when nothing happens """
    pass

def registerMigrations():
    # so the basic concepts is you put  a bunch of migrations is here

    MigrationTool.registerUpgradePath('development',
                                      '0.7 alpha test',
                                      v1.dev_one0.onezero)

    MigrationTool.registerUpgradePath('plone',
                                      '0.7 alpha test',
                                      v1.plone_one0.onezero)

