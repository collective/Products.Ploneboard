#!/bin/bash
# ensure that when something is wrong, nothing is broken more than it should...
set -e

# first, create some pot containing anything
i18ndude rebuild-pot --pot ploneboard-generated.pot --create ploneboard --merge manual.pot ../*
i18ndude rebuild-pot --pot plone-generated.pot --create plone --merge plone-manual.pot ../*

# then filter what we don't want, ie doubles
cp ploneboard-generated.pot Ploneboard.pot
i18ndude filter plone-generated.pot ploneboard-generated.pot > plone-generated2.pot
## plone-plone.pot is a symbolic link (or whatever is openable on the fs) that
## points to PloneTranslation/i18n/plone.pot (Pre Plone4)
## or plone/app/locales/locales/plone.pot (Plone4)
i18ndude filter plone-generated2.pot plone-plone.pot > Ploneboard-plone.pot

# some cleaning
rm -f ploneboard-generated.pot
rm -f plone-generated.pot
rm -f plone-generated2.pot

# finally, update the po files
i18ndude sync --pot Ploneboard-plone.pot `find . -iregex '.*plone-.*\.po$'`
i18ndude sync --pot Ploneboard.pot  `find . -iregex '.*\.po$'|grep -v plone`

