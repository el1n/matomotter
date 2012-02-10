#!/bin/sh

python \
	/opt/google_appengine/dev_appserver.py \
	--address=0.0.0.0 \
	--port=8000 \
	--datastore_path=/tmp/matomotter/var/data.store \
	--history_path=/tmp/matomotter/var/data.store.history \
	/tmp/matomotter/public_html
