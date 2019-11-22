#!/bin/bash

ssh root@ecmwfindicohex.vs.mythic-beasts.com << EOF
  cd /opt/indico/plugins/ecmwf
  git pull
  cd /opt/indico
  source .venv/bin/activate
  export INDICO_CONFIG=/opt/indico/.indico.conf
  indico db --plugin ecmwf upgrade
  touch /opt/indico/web/indico.wsgi
EOF
