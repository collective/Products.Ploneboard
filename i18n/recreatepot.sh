#!/bin/sh
i18ndude rebuild-pot --pot=cmfmember-plone.pot --create=plone `find ../skins/ -iregex '.*\..?pt$'`
