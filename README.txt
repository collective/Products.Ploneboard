Overview

  Ploneboard is an easy to use web board. It utilizes the proven Plone user interface, 
  and is made for easy integration into Plone sites. The target audience is businesses 
  and developers wanting a discussion board in their Plone site.

  "Ploneboard web site":http://www.plonesolutions.com/ploneboard

  Contributors

    **Helge Tesdal**, "Plone Solutions":http://www.plonesolutions.com -- Code, idea, architecture

    **Ruslan Spivak** -- Code

    **Alexander Limi**, "Plone Solutions":http://www.plonesolutions.com -- User interface, concepts

    **Vidar Andersen** -- Application icons

    **Johan H. Borg** -- Smiley icons, copyright 2003, used in Ploneboard with permission

    **Kapil Thangavelu** -- Initial architecture

Todo

  - Rename 'types' directory to 'content' or similar, to enable use of python types (StringType etc.) in the root dir

  - Workflow cleanup - see comments

  - Refactor tests, use PloneTestCase

  - Add more security declarations, use the board permissions.

  - Split up posting macros, as entire template is evaluated each time a macro is used

  Alexander's list:
  
    - Getting "not allowed to access getBoardTitle in this context" when trying to use getBoardTitle in board_header
    
    - "Up to" in board_header should list the name of the object above + type, like "Back to developer forum"
    
    - forum_view -> conversation_listing - it's actually a listing, not av view
    
    - Workflow rename
    
      - FreeForAll -> Open
      - MemberPosting -> Only Members can post
      - Private -> Members only

  Jean Jordan reported:
  
    - Old PloneboardWiki (on plone.org) doesn't work as ZWiki was nuked.
  
    - One private forum in a board makes the whole board private (anon is prompted for login)
    
    - No difference between freeforall and memberposting - anon can't post in either
    
    - anon or member can't view a moderated forum
    
    - reviewer can view moderation-form but doesn't see action buttons to publish
    
    - if you reject a moderated post, it vanishes from the plone UI
    
    - as soon as a moderated forum contains a comment that was published, anon and member lose viewing rights 
    
      - Unauthorized - access to 'Creator' denied
      
    - No links to moderation-form or folder_contents (to delete a forum)
    
    - Can't edit posted comment (actually a feature, make sure it works if you change permissions)
    
    - A forum starts in 'freeforall' but if it's moderated or memberposting and you want to send it back, the action says 'anarchy'.
    
    - doesn't look like forum conversations feature in catalog searches at all
    
  Erik de Wild (tripple-o) reported:
  
    - When creating a forum, it says unknown date (because forum date is last posting date), display something like 'no conversations' instead
    
    - After posting a reply, only the conversation start is visible, and not the replies.
    
    - Just above the 'reply to this'-button, the letters "ting" show up while they shouldn't be there
    
    - After posting a second reply, the first reply shows up. There seems to be something wrong with the counter.
    
    - Enable different title in replies instead of using the title of the initial post
    
    - Can't delete a conversation from the ZMI, says TypeError - _delOb() takes exactly 2 arguments, 3 given - line 446 in BTreeFolder2, line 232 in Ploneboard.Forum
    
    - Still get reply-buttons on locked conversations - check permissions before displaying buttons
    
    - Locked conversations disappear from the navtree - probably due to different wfstate and navtree suck. Going to have different navigation and main template in board
    
  Nate Aune reported:
  
    - Problem adding a Forum outside a board - get attribute error getBoard.

  DiscussionTool integration
  
    So the board can be used in the context for content objects
    
  Moderation UI work
  
    Workflow based moderation system, enhanced with javascript to do mass moderation quickly and effectively.
    
  General UI/JS work
  
    A lot of touches to make it easier to use, in-lined reply textarea for example.
    
    
  i18n support
  
    Make sure i18n is supported everywhere, and make a po-file.

  Mail and news integration
  
    - Yeah.