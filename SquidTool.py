"""
##############################################################################
#
# Copyright (c) 2003 struktur AG and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
# $Id: SquidTool.py,v 1.4 2004/09/22 13:33:38 panjunyong Exp $ (Author: $Author: panjunyong $)
"""

# make sockets non blocking
import timeoutsocket
timeoutsocket.setDefaultSocketTimeout(5)

import os, re, httplib, urlparse, urllib, sys
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, package_home
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.Expression import Expression
from Products.CMFCore.CMFCorePermissions  import ManagePortal, ModifyPortalContent, View
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Acquisition import aq_base
from Permissions import *


class SquidTool(UniqueObject, SimpleItem):
    """ Tool to send PURGE requests to squid  """

    id        = 'portal_squid'
    meta_type = 'CMF Squid Tool'

    security = ClassSecurityInfo()

    manage_options=(
        ({ 'label'   : 'Squid Cache Urls',
           'action'  : 'manage_configForm',
           },
         ) + SimpleItem.manage_options
        )

    manage_configForm = PageTemplateFile('www/config', globals())

    def __init__(self):
        self.id = 'portal_squid'
        self.squid_urls = []


    security.declareProtected(ManagePortal, 'manage_setSquidSettings')
    def manage_setSquidSettings(self, urls, REQUEST=None):
        ''' stores the tool settings '''

        urls = urls.replace("\r\n", "\n")
        urls = urls.split("\n")
        urls = map(lambda x: x.strip(), urls)
        urls = filter(lambda x: x, urls)
        self.squid_urls = urls 
            
        if REQUEST:
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    security.declarePrivate('pruneUrl')
    def pruneUrl(self, ob_url, REQUEST=None):
        # ob_url is a relative to portal url

        results = []
        ob_url=urllib.quote(ob_url)
        for url in self.squid_urls:
            # if not url.endswith('/'): url=url+'/'
            url = urlparse.urljoin(url, ob_url)
            (scheme, host, path, params, query, fragment) = urlparse.urlparse(url)

            # XXX: probably put into seperate thread
            #      and setup a Queue

            try: 
                conn = httplib.HTTPConnection(host)
                conn.putrequest('PURGE', path)
                conn.endheaders()
                conn.sock.set_timeout(2)
                resp = conn.getresponse()
                status = resp.status
                xcache = resp.getheader('x-cache', '')
                xsquiderror = resp.getheader('x-squid-error', '')
            except:
                err = sys.exc_info()
                status = 000 
                xcache = ''
                xsquiderror = "%s %s" % (err[0], err[1])

            results.append((status, xcache, xsquiderror))

            # NOTE: if the purge was successfull status will be 200 (OK)
            #       if the object was not in cache status is 404 (NOT FOUND)
            #       if you are not allowed to PURGE status is 403
            #       see README.txt for details how to setup squid to allow PURGE

            if REQUEST: REQUEST.RESPONSE.write('%s\t%s\t%s\n' % (status, url, xsquiderror))

        return results

    security.declarePrivate('pruneObject')
    def pruneObject(self, ob, REQUEST=None):
        # prune this object
        portal_url = getToolByName(self, 'portal_url')
        url = portal_url.getRelativeUrl(ob)
        return self.pruneUrl(url, REQUEST=REQUEST)        


    security.declareProtected(PURGE_URL, 'manage_pruneUrl')
    def manage_pruneUrl(self, url, REQUEST=None):
        """ give a url which shall be pruned """
        return self.pruneUrl(url, REQUEST=REQUEST)


    def manage_pruneAll(self, REQUEST=None):
        """ prune all objects in catalog """
        portal_catalog = getToolByName(self, 'portal_catalog')
        brains = portal_catalog()
        for brain in brains:
            ob = brain.getObject()
            self.pruneObject(ob)

        return "finished"
    
InitializeClass(SquidTool)

