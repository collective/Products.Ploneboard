#!/bin/sh

for PO in cmfmember-??.po; do
    if [ $PO != "cmfmember-en.po" ]; then
        i18ndude sync --pot cmfmember.pot -s $PO
    fi
done
