#!/bin/sh
i18ndude rebuild-pot --pot=cmfmember2-plone.pot --create=plone `find ../skins/ -iregex '.*\..?pt$'`
