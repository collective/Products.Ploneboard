#
#  ATSchemaEditorNG TestCase
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from atse_testcase import ATSETestCase

class TestSchemaEditor(ATSETestCase):

    def afterSetUp(self):
        self.installDependencies()
        self.createBasicSetup()

    def test_updateObjectSchema(self):
        original_schema = self.target1.Schema()
        name = 'additionalField'
        
        self.container.atse_delField(name)
        
        self.container.update_all_schemas()
        
        new_schema = self.target1.Schema()
        self.assertNotEqual([x.getName() for x in original_schema.fields()], [x.getName() for x in new_schema.fields()])

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSchemaEditor))
    return suite

if __name__ == '__main__':
    framework()
