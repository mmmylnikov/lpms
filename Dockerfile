# pull official base image
FROM python:3.12-slim-bookworm as base

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=noninteractive

# dependency assembly stage
FROM base AS builder

RUN set -xe; \
    apt-get update && apt-get install -y \
        -o APT::Install-Recommends=false \
        -o APT::Install-Suggests=false \
            build-essential\
            gcc\
            g++ \
            libc-dev \
            libffi-dev \
            libxml2-dev \
            libxslt-dev \
            libpq-dev \
            git \
            zlib1g-dev \
            libjpeg-dev \
            libmagic-dev \
            curl \
            wget \
            ca-certificates

ADD ./lpms/requirements.txt /requirements.txt
RUN pip install --prefix=/install -r /requirements.txt

# main image and user setup
FROM base

# install postgres-client for pg_dump
RUN apt-get update && apt-get install -y gnupg2 curl
RUN echo "deb http://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" > /etc/apt/sources.list.d/pgdg.list
RUN curl -L https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - 
RUN apt-get update && apt-get install -y postgresql-client-14 

RUN groupadd -g 800 -r unprivileged && useradd -r -g 800 -u 800 -m unprivileged

RUN set -xe; \
    apt-get update && apt-get install -y \
        -o APT::Install-Recommends=false \
        -o APT::Install-Suggests=false \
        locales gosu procps; \
            gosu nobody true;

COPY --from=builder /install /usr/local

RUN pip install gunicorn==21.2.0

# set locales
RUN echo "LC_ALL=ru_RU.UTF-8" >> /etc/environment && echo "ru_RU.UTF-8 UTF-8" >> /etc/locale.gen && \
    echo "LANG=ru_RU.UTF-8" > /etc/locale.conf && locale-gen ru_RU.UTF-8

# copy project
COPY lpms /opt/app
COPY entrypoint.sh /opt/app
COPY wait-for-it.sh /opt/app

RUN chmod +x /opt/app/entrypoint.sh
RUN chmod +x /opt/app/wait-for-it.sh

# set work directory
WORKDIR /opt/app
RUN chown -R unprivileged:unprivileged /opt/app

# сlearing the cache and deleting temporary files
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# publishing port and setting the entry point
EXPOSE 8000
ENTRYPOINT ["/opt/app/entrypoint.sh"]
CMD ["runserver"]
