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
# $Id: SquidTool.py,v 1.6 2004/09/24 03:33:21 panjunyong Exp $ (Author: $Author: panjunyong $)
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
        for host in self.squid_urls:
            # XXX: probably put into seperate thread
            #      and setup a Queue

            try: 
                conn = httplib.HTTPConnection(host)
 
                # XXX hack to use HTTP/1.0 and the timeoutsocket
                # NOTE: only HTTP/1.0 and the full url can make PURGE work
                # You can see code from squid's client.c

                conn._http_vsn = 10
                conn.conn_http_vsn_str = 'HTTP/1.0'
                conn.putrequest('PURGE', ob_url) 
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

            if REQUEST: REQUEST.RESPONSE.write('%s\t%s\t%s\n' % (status, ob_url, xsquiderror))

        return results

    security.declareProtected(PURGE_URL, 'pruneObject')
    def pruneObject(self, ob, REQUEST=None):
        # prune this object
        return self.pruneUrl(ob.absolute_url(), REQUEST=REQUEST)        

    security.declareProtected(PURGE_URL, 'manage_pruneUrl')
    def manage_pruneUrl(self, url, REQUEST=None):
        """ give a url which shall be pruned """
        request = REQUEST or self.REQUEST
        server_url = request['SERVER_URL']
        if url[:4].lower() != 'http':
            url =  urlparse.urljoin(server_url, url)
        return self.pruneUrl(url, REQUEST=REQUEST)

    security.declareProtected(ManagePortal, 'manage_pruneAll')
    def manage_pruneAll(self, REQUEST=None):
        """ prune all objects in catalog """
        portal_catalog = getToolByName(self, 'portal_catalog')
        brains = portal_catalog()
        for brain in brains:
            url = brain.getURL()
            self.pruneObject(ob)

        return "finished"
 
InitializeClass(SquidTool)

