"""Migration tools for ATContentTypes

Migration system for the migration from CMFDefault/Event types to archetypes
based CMFPloneTypes (http://sf.net/projects/collective/).

Copyright (c) 2004, Christian Heimes and contributors
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, 
   this list of conditions and the following disclaimer in the documentation 
   and/or other materials provided with the distribution.
 * Neither the name of the author nor the names of its contributors may be used
   to endorse or promote products derived from this software without specific
   prior written permission.

$Id: common.py,v 1.2 2004/03/08 17:24:05 tiran Exp $
"""

from Products.Archetypes.debug import log as at_log

try:
    dummy = True
except:
    True=1
    False=0

DEBUG      = False
REMOVE_OLD = True
 
def LOG(logmessage):
    """ wrap archetypes log method
    """

    if DEBUG:
        at_log(logmessage)
