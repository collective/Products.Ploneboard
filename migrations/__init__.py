from Products.CMFMember import ControlTool as MigrationTool
import v1

def null(portal):
    """ This is a null migration, use it when nothing happens """
    pass

def registerMigrations():
    # so the basic concept is you put a bunch of migrations in here

    MigrationTool.registerUpgradePath('development',
                                      '1.0 alpha',
                                      v1.dev_one0a.oneZeroAlpha)

    MigrationTool.registerUpgradePath('plone',
                                      '1.0 alpha',
                                      v1.plone_one0a.oneZeroAlpha)

    MigrationTool.registerUpgradePath('1.0 alpha',
                                      '1.0 beta',
                                      null)

    MigrationTool.registerUpgradePath('1.0 beta',
                                      '1.0 beta2',
                                      null)

    MigrationTool.registerUpgradePath('1.0 beta2',
                                      '1.0 beta3',
                                      v1.one0b2_one0b3.oneZeroBeta3)

    MigrationTool.registerUpgradePath('1.0 beta3',
                                      '1.0 beta4',
                                      null)

    MigrationTool.registerUpgradePath('1.0 beta4',
                                      '1.0 beta5',
                                      null)

    MigrationTool.registerUpgradePath('1.0beta5',
                                      '1.1.0-CVS',
                                      null)
