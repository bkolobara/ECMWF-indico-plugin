#!/bin/bash

# Copy egg file in right location
cp -r /ecmwf_plugin.egg-info /ecmwf/

# Loop until db container is ready.
psql postgresql://indico:indicopass@postgres -lqt | cut -d \| -f 1 | grep -qw indico
until [ $? -eq 0 ]; do
    sleep 1
    psql postgresql://indico:indicopass@postgres -lqt | cut -d \| -f 1 | grep -qw indico
done

# Check if db is initialized.
psql postgresql://indico:indicopass@postgres/indico -c 'SELECT COUNT(*) FROM events.events'
if [ $? -eq 1 ]; then
    echo 'Preparing DB...'
    echo 'CREATE EXTENSION unaccent;' | psql postgresql://indico:indicopass@postgres/indico
    echo 'CREATE EXTENSION pg_trgm;' | psql postgresql://indico:indicopass@postgres/indico
    indico db prepare
fi

# Run migrations on every startup to pick up plugin migrations.
indico db upgrade
indico db --plugin ecmwf upgrade

echo 'Starting Indico...'
indico run -h 0.0.0.0 -p 8800 -q --enable-evalex