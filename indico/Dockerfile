FROM centos:centos7

ENV INDICO_CONFIG="/opt/indico/etc/indico.conf"

RUN yum makecache fast
RUN yum update -y;
RUN yum install -y epel-release vim less;
RUN yum install -y texlive-xetex
RUN yum install -y gcc python-virtualenv

# PostgreSQL tools are reaquired to build Indico's db adapter.
RUN yum install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm
RUN yum install -y postgresql11-devel
ENV PATH="/usr/pgsql-11/bin:$PATH"

RUN mkdir -p /opt/indico/{data,etc}
RUN mkdir -p /opt/indico/data/{log,cache,archive,tmp}

WORKDIR /opt/indico
RUN virtualenv env -p /usr/bin/python2.7

ENV VIRTUAL_ENV=/opt/indico/env
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install --upgrade pip
RUN pip install 'indico==2.2.4'

# Indico's source code is required to build plugin assets.
RUN yum install -y git nodejs
RUN git clone --recursive https://github.com/indico/indico.git src
WORKDIR /opt/indico/src
RUN git checkout 2.2-maintenance
RUN pip install -r requirements.dev.txt
# Update to latest stable npm version
RUN npm install -g n
RUN n stable
RUN npm install 

RUN yum clean all

# Maildump is used to catch outgoing emails.
RUN pip install maildump

# Build plugin's egg file
COPY src /ecmwf
RUN pip install -e /ecmwf
RUN cp -r /ecmwf/ecmwf_plugin.egg-info /ecmwf_plugin.egg-info

# Upgrade flask to a version supporting OIDC
RUN sed -i '/Flask-Multipass/d' /opt/indico/env/lib/python2.7/site-packages/indico-2.2.4.dist-info/METADATA
RUN pip install --pre --upgrade 'flask-multipass[oidc]'
RUN pip install Authlib==0.12.1

WORKDIR /opt/indico

COPY indico.conf /opt/indico/etc/indico.conf
RUN cp /opt/indico/env/lib/python2.7/site-packages/indico/logging.yaml.sample /opt/indico/etc/logging.yaml
COPY run_indico.sh /opt/indico/
COPY run_plugin_builder.sh /opt/indico/
COPY run_indico_celery_worker.sh /opt/indico/
RUN chmod +x /opt/indico/run_indico.sh /opt/indico/run_plugin_builder.sh /opt/indico/run_indico_celery_worker.sh
