#!/bin/sh
i18ndude.py rebuild-pot --pot=cmfmember-plone.pot --create=plone `find ../skins/ -iregex '.*\..?pt$'`
