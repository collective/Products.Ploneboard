CMFMember is a replacement for portal_memberdata that provides TTP
(Through-The-Plone) member management. Members are ordinary Archetypes
(AT) objects that are controlled by workflow.  Member data can be
expanded and configured via an AT schema (or via subclassing). For
more about the goals of the project, please see GOALS.txt.


WARNINGS:

    Before you get all excited about upgrading, please be aware of the
    following "gotchas" regarding CMFMember:

    - There is NO reverse migration, meaning once you migrate your
      existing Members to CMFMember types, there is no mechanism
      provided for going back to "the way things were".  It is HIGHLY
      RECOMMENDED that you back up your entire Plone site before
      proceeding with migration.

    - We have provided a mechanism for migrating your extended member
      data (properties defined in the memberdata tool) over to an AT
      schema (using Archetype's VariableSchema support) for your
      convenience.  This has NOT been heavily tested.  We STRONGLY
      recommend you check to make sure all of your fields were migrated
      properly.

    - The VariableSchema support can be exposed through the ZMI by
      changing the 'expose_var_schema' variable near the top of the
      MemberDataContainer.py file to a non-zero value.  This will cause
      a 'Schema' tab to appear in the MemberDataContainer's management
      interface, and will allow for TTW editing of custom schema fields.
      This will also give anyone with the "Manage properties" permission
      the ability to run arbitrary code on the server, so please only
      use this if you trust your managers completely.

    - If you upgrade Archetypes out from under CMFMember, all of the
      catalog associations disappear.  (To see these, go to the
      archetype_tool, click the Catalog Tab and you'll see all of the
      catalog associations. The way to avoid this is to install
      CMFMember after getting Archetypes to where you want it.
      (See Requirements section)

    - If you change the workflow that is associated with your Member
      type, your existing users will be set to the initial (default)
      state of your new workflow.  This is because the information
      about the workflow state is stored in the workflow itself.
      A recommended workaround is to write a quick script that
      captures the existing states, then, after your workflow change,
      sets the Members to whatever state you map them to::

       wf_map = {
                 'public':'public',
                 'private':'secret',
                 'new':'unregistered',
                }

       user ID:   Old State:   New State:
       ========   ==========   ==================
       user_1     public       wf_map['public']
       user_2     private      wf_map['private']
       user_3     new          wf_map['new']

      or something like that...


REQUIREMENTS:

    - Archetypes 1.3 from the release-1_3-branch, the upcoming
      Archetypes1.3 release will be from this branch.  (NOTE: recent
      iterations of the release-1_3-branch require the MimetypesRegistry
      product to be installed separately.)

    - Plone-2.0.1 or greater.  (Plone 2.0-final will NOT suffice,
      there is a fix to MembershipTool's getMemberById() method that
      is required to make the unit tests pass.)


INSTALLATION:

    1. Put CMFMember (and the Requirements) in your Zope Products directory.

    1a. Run the test suite.  This will require ZopeTestCase available from

        Stefan Holek, whose testing technique is unstoppable:

        http://zope.org/Members/shh/ZopeTestCase

        While you're at it, we suggest you check out his band, EPY:

        http://epy.co.at/

    2. Restart Zope.

    4. Install CMFMember into your Plone site using
       CMFQuickInstaller. (In Plone, select "plone setup", click on
       "Add/Remove Products" and install CMFMember.)  You can also use
       the portal_quickinstaller tool from the ZMI to install the
       Product.

    5. Click on the CMFMember entry in in the navigation portlet. (The
       entry probably says something like "CMFMember out of date".)
       You can also use the cmfmember_control tool from the ZMI for this.

    6. (SEE WARNING ABOVE) Click the "migrations" tab and migrate.


WORKFLOWS:

    CMFMember comes with two workflows by default:

        - member_auto_workflow (default)

          This workflow works almost the same as the normal Plone
          registration -- the member is registered upon submission
          of the registration form and can immediately log into the
          site.

        - member_approval_workflow

          The approval workflow forces the registration into an approval
          process, much like the publication workflow for regular content.
          The pending member cannot log in until a site manager approves
          the registration.

    Feel free to build a custom workflow and associate it to the Member
    Type! This is why we built this thing. ;)  If you do, be sure to review
    the warning section above.


EXTENDING MEMBERS:


    CMFMember allows you to customize the member data. You can customize
    the data either using a TTW (through-the-web) schema editor, or by
    creating an Archetypes module that subclasses CMFMember.Member.

    Optional Field Attributes

      CMFMember adds an optional attribute to the Archetypes Field
      schema. This attribute allows CMFMember to present the member edit
      form differently, depending on whether the register action has run yet.

      **regfield** -- The 'regfield' attribute is used to mark fields that
      should appear on the registration form. Fields must have
      'regfield=1' in order to appear on the form.

      Note that if a field is marked as required ('required=1') but not
      marked as a regfield, it will not appear on the registration form.
      In this case, validation will fail and the workflow will not trigger
      the next state.


    TTW Schema

      There are plans underway to provide a full GUI TTW schema
      editor.  For now, you can (after migrating), use the
      portal_memberdata tool to add your custom schema fields.  In the
      ZMI, click on the portal_memberdata tool, then click the
      "schema" tab and paste your completed schema into there.  (Note
      that your schema definition will be appended to the default
      schema.)  If you want a data point to show up on the
      registration form when a new member registers, add "regfield=1"
      to the schema for that field.


MAILING LIST:

    Interested Users and Developers are welcome to join the
    collective-cmfmember@lists.sourceforge.net mailing list, hosted on
    SourceForge (duh) as part of the Collective project:

    http://sf.net/projects/collective


MAILING LIST:

    Interested Users and Developers are welcome to join the
    cmfmember-dev mailing list hosted on sourceforge.

    http://sf.net/projects/collective


BUGS:


    Please report bugs (which are different from feature requests) to
    the following collector:

    http://plone.org/development/teams/developer/groups/issues


FEATURE REQUESTS:

    In the spirit of Open Source, we suggest you write your new features
    to satisfy your particular Use Case yourself!  Cut a branch, work on
    your changes; we'll review them and merge them in if appropriate.

    One thing we ask is that if you plan on writing new features, you
    keep the entire community in mind, write your features as options,
    and use "best practices" coding techniques.  We also ask that you
    write tests for your code before it will be considered.  Open
    communication is key!  Join the #cmfmember channel on IRC
    (irc.freenode.net), ask questions, let people know what direction
    you want to take and you'll find friendly helpful people.

Thanks for using CMFMember, built with beer!
