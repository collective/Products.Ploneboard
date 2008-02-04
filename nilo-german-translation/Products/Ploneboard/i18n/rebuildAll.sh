#!/bin/bash

i18ndude rebuild-pot --pot Ploneboard.pot --create ploneboard --merge manual.pot `find ../skins/ -iregex '.*\..?pt$'`

i18ndude sync --pot Ploneboard-plone.pot `find . -iregex '.*plone-.*\.po$'`

i18ndude  sync --pot Ploneboard.pot  `find . -iregex '.*\.po$'|grep -v plone`

