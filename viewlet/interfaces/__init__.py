##############################################################################
#
# Copyright (c) 2004 CompositePack Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Viewlet interface.

$Id: __init__.py,v 1.2 2004/06/22 07:47:47 godchap Exp $
"""
from Interface import Interface
from Interface.Attribute import Attribute

class IViewlet(Interface):
    """Interface of Viewlets that can be applied to an object.
    """

    def __call__():
        """Returns the template associated with the viewlet.
        """
