GroupUserFolder


(c)2002-2003 Ingeniweb



(This is a structured-text formated file)



ABSTRACT

  GroupUserFolder is a kind of user folder that provides a special kind of user management.
  Some users are "flagged" as GROUP and then normal users will be able to belong to one or
  serveral groups.

STRUCTURE

  Group and "normal" User management is distinct. Here's a typical GroupUserFolder hierarchy::

     - acl_users (GroupUserFolder)
     |
     |-- Users (GroupUserFolder-related class)
     | |
     | |-- acl_users (UserFolder or derived class)
     |
     |-- Groups (GroupUserFolder-related class)
     | |
     | |-- acl_users (UserFolder or derived class)


  So, INSIDE the GroupUserFolder (or GRUF), there are 2 acl_users :

    - The one in the 'Users' object manages real users

    - The one in the 'Groups' object manages groups

  The two acl_users are completely independants. They can even be of different kinds.
  For example, a Zope UserFolder for Groups management and an LDAPUserFolder for Users management.

  Inside the "Users" acl_users, groups are seen as ROLES (that's what we call "groles") so that 
  roles can be assigned to users using the same storage as regular users. Groups are prefixed
  by "group_" so that they could be easily recognized within roles.

  Then, on the top GroupUserFolder, groups and roles both are seen as users, and users have their
  normal behaviour (ie. "groles" are not shown), except that users affected to one or several groups
  have their roles extended with the roles affected to the groups they belong to.


  Just for information : one user can belong to zero, one or more groups.
  One group can have zero, one or more users affected.

  [2003-05-10] There's currently no way to get a list of all users belonging to a particular group.


GROUPS BEHAVIOUR

  
  ...will be documented soon...


GRUF AND PLONE

  See the dedicated README-Plone file.


GRUF AND SimpleUserFolder

  You might think there is a bug using GRUF with SimpleUserFolder (but there's not): if you create
  a SimpleUserFolder within a GRUF a try to see it from the ZMI, you will get an InfiniteRecursionError.

  That's because SimpleUserFolder tries to fetch a getUserNames() method and finds GRUF's one, which 
  tries to call SimpleUserFolder's one which tries to fetch a getUserNames() method and finds GRUF's one, 
  which tries to call SimpleUserFolder's one which tries to fetch a getUserNames() method and finds GRUF's one, 
  which  tries to call SimpleUserFolder's one which tries to fetch a getUserNames() method and finds GRUF's 
  one, which  tries to call SimpleUserFolder's one which tries to fetch a getUserNames() method and finds 
  GRUF's one, which  tries to call SimpleUserFolder's one which tries to fetch a getUserNames() method and 
  finds GRUF's one, which  tries to call SimpleUserFolder's one which tries (see what I mean ?)

  To avoid this, just create a getUserNames() object (according to SimpleUserFolder specification) in the folder
  where you put your SimpleUserFolder in (ie. one of 'Users' or 'Groups' folders).

  GRUF also implies that the SimpleUserFolder methods you create are defined in the 'Users' or 'Groups' folder.
  If you define them above in the ZODB hierarchy, they will never be acquired and GRUF ones will be catched
  instead, causing infinite recursions.


GRUF AND LDAPUserFolder

  (As I do not have too much time to document it extensively, I include a discution in #plone with
  Ronan Amicel and Alan Runyan which might give you some clues about it. If you feel like writing
  doc for it, do not hesitate ! :-) )

  [23:16:56] <ronnix> as I told you, I'm currently trying to use GRUF with LDAP. I'm not sure of the best way to do it yet. My groups are defined in the LDAP directory.
  [23:17:10] <ronnix> The underlying user folder has some kind of group management itself, and makes it easy to list the members of a group.
  [23:17:54] <pjgrizel> hum, you mean the LDAPUserFolder's group management ? It's an LDAP group concept, not a Zope group concept. 
  [23:18:02] <pjgrizel> LDAP groups are mapped directly as Zope roles 
  [23:18:43] <pjgrizel> in fact, if your groups are not changing very often, you can have an LDAPUF in "Users" and a classic User Folder in "Groups" 
  [23:19:03] <pjgrizel> then, you create one user per (LDAP) group in the Group's acl_users 
  [23:19:07] <ronnix> Yes. I currently have a homegrown system for groups which I'm not completely satisfied with, and would like to migrate to GRUF as smoothly as possible, keeping the groups in LDAP for other applications
  [23:19:57] <ronnix> So I need to map the LDAP groups to Zope groups somehow. Maybe I need a special user folder in Groups that gives me users from the LDAP groups
  [23:20:19] <pjgrizel> and, in the "groups" tab of LDAPUserFolder, you just have to (manually) assign your LDAP groups to Zope roles... and as in the GRUF's Users folder groups are seen as roles prefixed to "group_", all you have to do is to assign your LDAP groups to your GRUF groups... quite easy at this point ! :-) 
  [23:21:16] <ronnix> i can map ldap groups to zope roles
  [23:21:38] <ronnix> but i'm not sure i understand the end of what you said
  [23:22:27] <pjgrizel> if you watch the "groups" tab of LDAPUF, you'll understand easily: LDAP groups are shown and you can assign them to Zope roles. 
  [23:22:37] <ronnix> ok with that
  [23:23:45] <pjgrizel> and GRUF makes (GRUF-)groups appear as roles within the "Users/acl_users" folder of GRUF 
  [23:24:18] <pjgrizel> so, all you have to do in the LDAPUF groups tab is to map LDAP groups to GRUF groups, in fact. 
  [23:24:33] <ronnix> ok i get it now!
  [23:24:43] <pjgrizel> :-) 
  [23:24:54] <pjgrizel> easy to do (I think) but not that easy to explain... 
  [23:25:27] <runyaga> can it be documented?
  [23:25:31] <runyaga> im not paying attention -srry
  [23:26:01] <ronnix> can i do it with local roles too?
  [23:27:32] <pjgrizel> local roles ? what do you mean by that ? 
  [23:28:00] <ronnix> not sure yet, need to try :-D
  [23:28:06] <pjgrizel> :-D 
  [23:28:33] <pjgrizel> (runyaga: yes, it's been documented in various mails... I need to collect what I wrote before to put in back in the README file) 
  [23:28:58] <pjgrizel> (seems like I've spent the last few weeks writing documentation... :-( I've got a huge chapter about security for my book update) 
  [23:29:00] <runyaga> that and plone howto would be great
  [23:29:04] <ronnix> basically, i want members of some ldap groups to have, let's say Reviewer role on some folder.
  [23:29:04] <runyaga> COOL
  [23:29:39] <pjgrizel> ronnix: yes, it works that way. You don't have to worry about that, batteries are included with GRUF ! :-) 
  [23:30:03] <ronnix> oh, yeah, sure, give local roles to the group
  [23:30:05] <pjgrizel> you should even try the "Audit" tab with the latest CVS version, which will give you an abstract of the security for your site 
  [23:30:10] <pjgrizel> (and it works with Plone !) 
  [23:43:33] <ronnix> pjgrizel: i just tried a slightly hacked GRUF + LDAP combo on a test pole site and it seems to work great
  [23:44:25] <ronnix> it seems I can do all the stuff I need with groups
  [23:44:39] <pjgrizel> ronnix: great ! but what did you hacked in GRUF or LDAP ? 
  [23:45:28] <ronnix> hacked cmfldap to query acl_users.Users.acl_users, to allow it to access extra methods in ldapuserfolder
  [23:45:50] <pjgrizel> oh, ok... that's what I've got to fix now ! :-) 
  [23:45:52] <ronnix> hacked GRUFUser to expose LDAPUser methods/attributes
  [23:46:01] <ronnix> but it's just a kludge
  [23:46:21] <ronnix> we should have a clean solution
  [23:46:34] <pjgrizel> we'll have ! 

  So... the next thing to do is to wrap user objects, now ! :-)


BUGS

  There is a bug using GRUF with Zope 2.5 and Plone 1.0Beta3 : when trying to join the plone site
  as a new user, there is a Zope error "Unable to unpickle object"... I don't know how to fix that now.
  With Zope 2.6 there is no such bug.


