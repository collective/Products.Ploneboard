CMFMember is a replacement for portal_memberdata that provides TTP user management.
Members are controlled by workflow, and member data configuration is done via an 
Archetypes schema.

Requirements: Archetypes (CVS HEAD), CMFBTreeFolder2, CMFPlone (CVS HEAD for 1_0 branch)

portal_memberdata is transformed into a CMFBTreeFolder2 folder.  In the folder you can
view, edit, delete, and rename users just like ordinary file objects.  Members' public / 
private status can be changed by changing the state.  The current default workflow
requires manager approval of new members and does not let members set their own
passwords.  By changing the workflow, you can allow members to set their own passwords
and to be automatically approved for membership.  Hopefully we will provide some of these 
alternative workflows when we hit 1.0

