#
# Comment tests
#

import unittest
import PloneboardTestCase
from Products.Ploneboard.transforms.url_to_hyperlink import URLToHyperlink

class MockTransformData:
    def setData(self, value):
        self.data=value


class TestUrlTransform(PloneboardTestCase.PloneboardTestCase):
    def runTest(self, testdata):
        transform = URLToHyperlink()
        data=MockTransformData()
        for (input, answer) in testdata:
            transform.convert(input, data)
            self.failUnlessEqual(data.data, answer)

    def testPlainText(self):
        testdata = [
                ("just a simple string",  "just a simple string"),
                ("htXtp:bla invalid scheme", "htXtp:bla invalid scheme"),
                ]
        self.runTest(testdata)

    def testPlainUrls(self):
        testdata = [
                ("http://simple.url/", '<a href="http://simple.url/">http://simple.url/</a>'),
                # XXX are URI schemes really case insensitive?
                ("HTtp://simple.url/", '<a href="HTtp://simple.url/">HTtp://simple.url/</a>'),
                ("https://simple.url/", '<a href="https://simple.url/">https://simple.url/</a>'),
                ("telnet://simple.url/", '<a href="telnet://simple.url/">telnet://simple.url/</a>'),
                ]
        self.runTest(testdata)

    def testUrlElements(self):
        testdata = [
                ("<telnet://simple.url/>", '<telnet://simple.url/>'),
                ("< telnet://simple.url/>", '< telnet://simple.url/>'),
                ("<telnet://simple.url />", '<telnet://simple.url />'),
                ("http://change.this/ <telnet://simple.url/>", '<a href="http://change.this/">http://change.this/</a> <telnet://simple.url/>'),
                ]
        self.runTest(testdata)


    def testEmail(self):
        testdata = [
                ("test@example.com", '<a href="mailto:test@example.com">test@example.com</a>'),
                ("<test@example.com>", "<test@example.com>"),
                ]
        self.runTest(testdata)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUrlTransform))
    
    return suite

