FROM python:3.8

# grab tini for signal processing and zombie killing
ENV TINI_VERSION v0.19.0
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends wget ca-certificates; \
    rm -rf /var/lib/apt/lists/*; \
    wget -O /usr/local/bin/tini "https://github.com/krallin/tini/releases/download/$TINI_VERSION/tini"; \
    wget -O /usr/local/bin/tini.asc "https://github.com/krallin/tini/releases/download/$TINI_VERSION/tini.asc"; \
    export GNUPGHOME="$(mktemp -d)"; \
    for server in $(shuf -e  \
                                hkp://p80.pool.sks-keyservers.net:80 \
                                keyserver.ubuntu.com \
                                hkp://keyserver.ubuntu.com:80) ; do \
        gpg --no-tty --keyserver "$server" --recv-keys 6380DC428747F6C393FEACA59A84159D7001A4E5 && break || : ; \
    done; \
    gpg --batch --verify /usr/local/bin/tini.asc /usr/local/bin/tini; \
    { command -v gpgconf > /dev/null && gpgconf --kill all || :; }; \
    rm -rf "$GNUPGHOME" /usr/local/bin/tini.asc; \
    chmod +x /usr/local/bin/tini; \
    tini -h


WORKDIR /usr/src/app

COPY requirements-docker.txt ./requirements.txt

RUN set -xe; \
    python -m venv venv; \
    . venv/bin/activate; \
    python -m pip install --upgrade pip; \
    pip install --no-cache-dir -r requirements.txt; \
    pip install rasa-x --extra-index-url https://pypi.rasa.com/simple; \
    python -c "import transformers; transformers.T5Tokenizer.from_pretrained('t5-base'); transformers.T5ForConditionalGeneration.from_pretrained('t5-base');";

COPY entrypoint.sh rasa_create_guest_url.py /usr/local/bin/
COPY actions/ actions/
COPY nlg nlg/
COPY data data/
COPY config.yml \
     credentials.yml \
     domain.yml \
     endpoints.yml \
     ./

RUN set -xe; \
    . venv/bin/activate; \
    rasa train;

# User configuration

ARG RASA_X_USERNAME
ARG RASA_X_PASSWORD
ARG RASA_BASE_URL
ARG RASA_BOT_NAME
ARG RASA_BOT_DESCRIPTION

# Note: The RASA X username cannot be changed in the community version!
ENV RASA_X_USERNAME ${RASA_X_USERNAME:-me}
ENV RASA_X_PASSWORD ${RASA_X_PASSWORD:-rasapass}
ENV RASA_BASE_URL ${RASA_BASE_URL:-http://localhost:5002}
ENV RASA_BOT_NAME ${RASA_BOT_NAME:-CovidBot}
ENV RASA_BOT_DESCRIPTION ${RASA_BOT_DESCRIPTION:-}

RUN chmod +x /usr/local/bin/entrypoint.sh \
             /usr/local/bin/rasa_create_guest_url.py

ENTRYPOINT ["/usr/local/bin/tini", "--"]

CMD ["/usr/local/bin/entrypoint.sh"]
