lists the currently concurrent authenticated users that
are logged into the portal .

this product is based on UserTrack that can be found 
at the same download location and must be installed.

- Installation

    - Install UserTrack into Zope (by unpacking the archive)

    - Install CMFUserTrackTool into Zope

    - register the CMFUserTrackTool in your Plone Portal
         
        this is done as with any other CMF Product,
        the simplest way is using QuickInstallerTool

    - in the portal there exists now a tool named 'portal_activeusers'

- Usage

    - You see on the right border an 'active_users' slot 
    
    - If you have CMFMessage installed you can click
        on the mail icon near the user to send him/her
        an instance message

ATTENTION
    The product is not yet ZEO-ready!




