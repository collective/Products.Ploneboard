CMFMember is a replacement for portal_memberdata that provides TTP
(Through-The-Plone) user management. Members are ordinary Archetypes
(AT) objects that are controlled by workflow.  Member data can be
expanded and configured via an AT schema (or via subclassing).


WARNINGS:

    Before you get all excited about upgrading, please be aware of the
    following "gotchas" regarding CMFMember:
    
    - There is NO reverse migration, meaning once you migrate your
      existing Members to CMFMember types, there is no mechanism
      provided for going back to "the way things were".  It is
      HIGHLY RECOMMENDED that you back up, at the very least, your
      Members, if not your entire Plone site before proceeding with
      migration.
        
    - We have provided a mechanism for migrating your extended
      member data (properties defined in the memberdata tool) over
      to an AT schema for your convenience.  We recommend you
      check the be sure all of your fields went properly.
        
    - If you change the workflow that is associated with your Member
      type, your existing users will be set to the initial (default)
      state of your new workflow.  This is because the information
      about the workflow state is stored in the workflow itself.
      A recommended workaround is to write a quick script that
      captures the existing states, then, after your workflow change,
      sets the Members to whatever state you map them to:
        
      wf_map = {
                'public':'public',
                'private':'secret',
                'new':'unregistered',
               }
        
      user ID:   Old State:   New State:
      ==========================================
      user_1     public       wf_map['public']
      user_2     private      wf_map['private']
      user_3     new          wf_map['new']
        
      or something like that...
        

REQUIREMENTS:

    - Archetypes 1.3

    - CMFPlone 2.0-final
    

INSTALLATION:

    1. Put CMFMember (and the Requirements) in your Zope Products directory.
    
    1a. Run the test suite.  This will require ZopeTestCase available from
        Stefan Holek, who's testing technique is unstoppable:
        
        http://zope.org/Members/shh/ZopeTestCase
        
        While you're at it, we suggest you check out his band, EPY:
        
        http://epy.co.at/
    
    2. Restart Zope.

    3. Install CMFMember using CMFQuickInstaller. (In Plone, select
       "plone setup", click on "Add/Remove Products" and install
       CMFMember.)  You can also use the portal_quickinstaller tool
       from the ZMI to install the Product.

    4. Click on the CMFMember entry in in the navigation portlet. (The
       entry probably says something like "CMFMember out of date".)
       You can also use the cmfmember_control tool from the ZMI for this.

    5. (SEE WARNING ABOVE) Click the "migrations" tab and migrate.
    

WORKFLOWS:

    CMFMember comes with two workflows by default:
    
        - member_auto_workflow (default)

            This workflow works almost the same as the normal Plone
            registration -- the member is registered on saving the
            registration form and can immediately log into the site.

        - member_approval_workflow

            The approval workflow forces the registration into an approval
            process, much like the publication workflow for regular content. 
            The pending member cannot log in until a site manager approves
            the registration.

    Feel free to build a custom workflow and associate it to the Member
    Type!  This is why we built this thing ;)  If you do, be sure to review
    the warning section above.
    

EXTENDING MEMBERS:

    * More stuff about TTW schema and subclassing goes here
  
    You can add custom memberdata to your Members by building a
    schema that provides the custom dataset.  You will be able to
    do this TTW when the TTW schema editor is complete :)  For now,
    you can (after migrating), use the portal_memberdata tool to add
    your custom schema.  In the ZMI, click on the portal_memberdata
    tool, then click the "schema" tab and paste your completed schema
    into there.  If you want a data point to be available when a new
    member registers, add "regfield=1" to the schema for that
    data point.


BUGS:

    Please report bugs (which are different from feature requests) to:
    
    http://plone.org/development/teams/developer/groups/issues
    

FEATURES REQUESTS:

    In the spirit of Open Source, we suggest you write your new features
    to satisfy your particular Use Case yourself!  Cut a branch, work on
    your changes; we'll review them and merge them in if appropriate.
    
    One thing we ask is that if you plan on writing new features, you keep
    the entire community in mind, write your features as options, and use
    "best practices" coding techniques.  We also ask that you write tests
    for your code before it will be considered.  Open communication is key!
    Join the #CMFMember channel on IRC, ask questions, let people know
    what direction you want to take and you'll find friendly helpful people.
    
Thanks for using CMFMember, build with beer!
    