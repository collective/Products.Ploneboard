#!/bin/bash
cd $(dirname $0)/locales
# ensure that when something is wrong, nothing is broken more than it should...
set -e

PRODUCTNAME='Products.Ploneboard'
I18NDOMAIN="ploneboard"

# first, create some pot containing anything
i18ndude rebuild-pot --pot ${PRODUCTNAME}-generated.pot --create ${I18NDOMAIN} --merge manual.pot ../*
i18ndude rebuild-pot --pot plone-generated.pot --create plone --merge plone-manual.pot ../* ../profiles/

# then filter what we don't want, ie doubles
cp ${PRODUCTNAME}-generated.pot Ploneboard.pot
i18ndude filter plone-generated.pot ${PRODUCTNAME}-generated.pot > plone-generated2.pot
## plone-plone.pot is a symbolic link (or whatever is openable on the fs) that
## points to PloneTranslation/i18n/plone.pot (Pre Plone4)
## or plone/app/locales/locales/plone.pot (Plone4)
i18ndude filter plone-generated2.pot plone-plone.pot > Ploneboard-plone.pot

# some cleaning
rm -f ${PRODUCTNAME}-generated.pot
rm -f plone-generated.pot
rm -f plone-generated2.pot

# finally, update the po files
i18ndude sync --pot Ploneboard-plone.pot */LC_MESSAGES/plone.po
i18ndude sync --pot Ploneboard.pot */LC_MESSAGES/ploneboard.po

WARNINGS=`find . -name "*pt" | xargs i18ndude find-untranslated | grep -e '^-WARN' | wc -l`
ERRORS=`find . -name "*pt" | xargs i18ndude find-untranslated | grep -e '^-ERROR' | wc -l`
FATAL=`find . -name "*pt"  | xargs i18ndude find-untranslated | grep -e '^-FATAL' | wc -l`

echo
echo "There are $WARNINGS warnings \(possibly missing i18n markup\)"
echo "There are $ERRORS errors \(almost definitely missing i18n markup\)"
echo "There are $FATAL fatal errors \(template could not be parsed, eg. if it\'s not html\)"
echo "For more details, run \'find . -name \"\*pt\" \| xargs i18ndude find-untranslated\' or"
echo "Look the rebuild i18n log generate for this script called \'rebuild_i18n.log\' on locales dir"

rm ./rebuild_i18n.log

touch ./rebuild_i18n.log

find ../ -name "*pt" | xargs i18ndude find-untranslated > rebuild_i18n.log
