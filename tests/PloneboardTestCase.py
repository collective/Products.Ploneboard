from Testing import ZopeTestCase

# Make the boring stuff load quietly
ZopeTestCase.installProduct('Ploneboard')

from Products.PloneTestCase import PloneTestCase

PloneTestCase.setupPloneSite(products=('Ploneboard',))


class PloneboardTestCase(PloneTestCase.PloneTestCase):

    class Session(dict):
        def set(self, key, value):
            self[key] = value

    def _setup(self):
        PloneTestCase.PloneTestCase._setup(self)
        self.app.REQUEST['SESSION'] = self.Session()

class PloneboardFunctionalTestCase(PloneTestCase.FunctionalTestCase):
    
    class Session(dict):
        def set(self, key, value):
            self[key] = value

    def _setup(self):
        PloneTestCase.FunctionalTestCase._setup(self)
        self.app.REQUEST['SESSION'] = self.Session()
