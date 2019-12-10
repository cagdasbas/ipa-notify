#!/bin/bash

[ ! -d ~/.priv ] && mkdir ~/.priv
chmod 600 ~/.priv
ipa-getkeytab -s ipa.domain.com -p admin@DOMAIN.COM -P -k ~/.priv/admin.kt

