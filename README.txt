CMFMember is a replacement for portal_memberdata that provides TTP
(Through-The-Plone) user management. Members are ordinary objects
that are controlled by workflow. Member data can be expanded and
configured via an Archetypes schema (or subclassing).

Requirements

  - Archetypes 1.3

  - CMFPlone 2.0-final

Installation

  1. Put CMFMember in your Zope Products directory.

  2. Restart Zope.

  3. Install CMFMember using CMFQuickInstaller. (In Plone, select
     "plone setup", click on "Add/Remove Products" and install
     CMFMember.)

  4. Click on the CMFMember entry in in the navigation portlet. (The
     entry probably says something like "CMFMember out of date".)

  5. Click the "migrations" tab and migrate.

Workflows

  CMFMember comes with two workflows, member_auto_workflow and
  member_approval_workflow.

  The auto workflow works almost the same as the normal Plone
  registration -- the member is registered on saving the registration
  form and can immediately log into the site.

  The approval workflow forces the registration into an approval
  process, much like the publication workflow for regular content. The
  pending member cannot log in until a site manager approves
  the registration.

Extending Member

  *Stuff about TTW schema and subclassing goes here*
