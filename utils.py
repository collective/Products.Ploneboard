# Copyright (C) 2003 strukturAG <simon@struktur.de>
#                    http://www.strukturag.com, http://www.icoya.com

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

"""
utilities

$Id: utils.py,v 1.2 2003/12/09 14:26:35 longsleep Exp $
"""

__version__ = "$Revision: 1.2 $"


# PlacelessTranslation Service Negotiator Support
try:
    # NOTE: the code below works only with the forked releases of PTS, yet
    from Products.PlacelessTranslationService.Negotiator \
        import getLangPrefsMethod as pts_getLangPrefsMethod
    getLangPrefsMethod = lambda req, get=pts_getLangPrefsMethod: get(req).getAccepted(req)
except ImportError, AttributeError:
    # NOTE: this is called for non forked PTS versions from 1.0b1 which raise ImportError
    #       this is also called for older PTS version which raise AttributeError
    #       to get the PTS fork visit http:/sf.net/projects/collective
    getLangPrefsMethod = lambda req: map(
        lambda x: x.split(';')[0].strip(),
        req.get('HTTP_ACCEPT_LANGUAGE','').split(',')
        )


class CheckValidity:
    def __init__(self, available_languages, available_languages_long):
        self.available_languages=available_languages
        self.available_languages_long=available_languages_long

    def check(self, lang):
        if self.available_languages:
            # check
            return lang in self.available_languages
        else:
            # failsave mode
            # check if len(lang) is 2 or 3
            if len(lang) == 2 or len(lang) == 3:
                return 1
            else: return 0

    def name(self, lang):
        if self.available_languages and self.available_languages_long:
            i=self.available_languages.index(lang)
            return self.available_languages_long[i]
        else: return 'Unknown'
        
