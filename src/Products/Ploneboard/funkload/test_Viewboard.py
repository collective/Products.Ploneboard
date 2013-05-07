# -*- coding: iso-8859-15 -*-
import unittest
from funkload.FunkLoadTestCase import FunkLoadTestCase
from webunit.utility import Upload
from funkload.utils import Data
from StringIO import StringIO
from utils import getPostUrlFromForum, getReplyUrlFromConversation, getForumUrlsFromBoard
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
        res = self.get(server_url + site + "/ploneboard",
            description="Get /pb/ploneboard")

        forumurls = getForumUrlsFromBoard(res)

        for forumurl in forumurls:

            res = self.get(forumurl,
                description="Get forum %s" % forumurl.split('/')[-1])

            url = getPostUrlFromForum(res, 0)

            self.get(url,
                description="Get latest posting in %s" % forumurl.split('/')[-1])

            #url = getPostUrlFromForum(res, 1)
            #self.get(url,
            #    description="Get second last post")
            #
            #url = getPostUrlFromForum(res, 2)
            #self.get(url,
            #    description="Get third last post")

        # end of test -----------------------------------------------

    def tearDown(self):
        """Setting up test."""
        self.logd("tearDown.\n")



if __name__ in ('main', '__main__'):
    unittest.main()
