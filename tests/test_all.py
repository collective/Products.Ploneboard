import Zope # Sigh, make product initialization happen

try:
    Zope.startup()
except: # Zope > 2.6
    pass

from unittest import main
from Products.CMFCore.tests.base.utils import build_test_suite

def test_suite():

    return build_test_suite('Products.CMFMember.tests',[
        'test_user',
        'test_copy',
        'test_copy_root',
        'test_delete',
        'test_delete_root',
        'test_migration',
        'test_rename',
        'test_rename_root',
        'test_MemberDataTool',
        ])

if __name__ == '__main__':
    main(defaultTest='test_suite')
