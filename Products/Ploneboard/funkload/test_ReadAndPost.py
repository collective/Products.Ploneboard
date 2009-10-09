# -*- coding: iso-8859-15 -*-
"""viewboard FunkLoad test

$Id: $
"""
import unittest
from funkload.FunkLoadTestCase import FunkLoadTestCase
from webunit.utility import Upload
from funkload.utils import Data
from StringIO import StringIO
from utils import getPostUrlFromForum, getReplyUrlFromConversation
#from funkload.utils import xmlrpc_get_credential

class Viewboard(FunkLoadTestCase):
    """Browse ploneboard

    This test use a configuration file Viewboard.conf.
    """

    def setUp(self):
        """Setting up test."""
        self.logd("setUp")
        self.server_url = self.conf_get('main', 'url')
        self.site = self.conf_get('main', 'site')
        # XXX here you can setup the credential access like this
        # credential_host = self.conf_get('credential', 'host')
        # credential_port = self.conf_getInt('credential', 'port')
        # self.login, self.password = xmlrpc_get_credential(credential_host,
        #                                                   credential_port,
        # XXX replace with a valid group
        #                                                   'members')

    def test_viewboard(self):
        # The description should be set in the configuration file
        server_url = self.server_url
        site = self.site
        # begin of test ---------------------------------------------

        self.setBasicAuth('admin', 'admin')
        self.get(server_url + site + "/ploneboard",
            description="Get /pb/ploneboard")

        self.get(server_url + site + "/ploneboard/python",
            description="Get /pb/ploneboard/python")

        self.get(server_url + site + "/ploneboard/python/add_conversation_form",
            description="Get /pb/ploneboard/pyth...d_conversation_form")

        res = self.post(server_url + site + "/ploneboard/python/add_conversation_form", params=[
            ['form.submitted', '1'],
            ['title', 'This is a test posting in the python forum'],
            ['text_text_format:default', 'text/html'],
            ['text', '\r\n<p>Guido rocks!</p>\r\n<p>Plone rocks!</p>\r\n<p>Ploneboard rocks!</p>\r\n'],
            ['files:list', Upload("")],
            ['form.button.Post', 'Post comment']],
            description="Post /pb/ploneboard/pyth...d_conversation_form")

        url = getPostUrlFromForum(res, 0)

        res = self.get(url,
            description="Get latest posting")
        url = getReplyUrlFromConversation(res, 0)

        self.get(url + "?title=This+is+a+test+posting+in+the+python+forum",
            description="Get add comment form")

        self.post(url, params=[
            ['form.submitted', '1'],
            ['title', 'Re: This is a test posting in the python forum'],
            ['text_text_format:default', 'text/html'],
            ['text', 'Previously admin wrote:\r\n<blockquote>\r\n<p>Guido rocks!</p>\r\n<p>Plone rocks!</p>\r\n<p>Ploneboard rocks!</p>\r\n</blockquote>\r\n<p>Zope rocks too!</p>\r\n'],
            ['files:list', Upload("")],
            ['form.button.Post', 'Post comment']],
            description="Post comment")

        res = self.get(server_url + site + "/ploneboard/python",
            description="Get /pb/ploneboard/python")
        url = getPostUrlFromForum(res, 1)
        self.get(url,
            description="Get second last post")

        self.get(server_url + site + "/ploneboard/python",
            description="Get /pb/ploneboard/python")

        self.get(server_url + site + "/ploneboard",
            description="Get /pb/ploneboard")

        # end of test -----------------------------------------------

    def tearDown(self):
        """Setting up test."""
        self.logd("tearDown.\n")



if __name__ in ('main', '__main__'):
    unittest.main()
