CMFSquidTool 

  A CMF Tool to prune squid cached pages from Zope.
  This product is covered by a license. See LICENSE.txt

Installation:

 1. Configure Squid:

    Squid does not allow you to purge objects 
    unless it is configured with access controls in 
    squid.conf. First you must add something like

        acl PURGE method purge
        acl localhost src 127.0.0.1
        http_access allow purge localhost
        http_access deny purge

    The above only allows purge requests which
    come from the local host and denies all other
    purge requests.

    Restart Squid after this reconfiguration.

 2. Zope Product

    Extract this tarball into your Zope Product folder
    and restart Zope when you did so.

    Afterwards install the tool into your portal by
    using the quickinstaller tool.


Configuration:

 1. ZMI Setup

    Enter the url to your portal rool like it is
    accessable through squid into the field inside
    the Squid Cache Urls tab of the portal_squid 
    tool.



 Simon Eisenmann
 
 simon@struktur.de
 

--
(c) 2003, Simon Eisenmann. All rights reserved.
