ARG PYTHON_VERSION=3.8-slim-buster

FROM python:${PYTHON_VERSION}

ARG APP_HOME=/app
ARG CI=

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

ENV PIPENV_SYSTEM 1

RUN pip install --no-cache-dir pipenv

# Install required things for git-secret
RUN apt-get update && apt-get install -y \
  wget \
  gnupg2 \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*


# Install requirements.
RUN apt-get update && apt-get install -y \
  build-essential \
  git \
  # psycopg2 dependencies
  libpq-dev \
  # Translations dependencies
  gettext \
  # cron
  cron \
  rsyslog \
  # Secret management
  git-secret \
  # Useful tools
  make \
  curl \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# Install pip dependencies using Pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv install --dev --deploy --ignore-pipfile --keep-outdated

WORKDIR ${APP_HOME}

# Add scripts and grant execute permissions
COPY ./docker/local/django/entrypoint.sh /
COPY ./docker/local/django/start.sh /

RUN sed -i 's/\r$//g' \
  /entrypoint.sh \
  /start.sh

RUN chmod +x \
  /entrypoint.sh \
  /start.sh

COPY . .

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/start.sh"]
