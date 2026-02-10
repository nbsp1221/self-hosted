FROM ghcr.io/openclaw/openclaw:main

# Keep the upstream runtime behavior, but add a "batteries included" toolbelt.
# We install as root, then drop back to the upstream non-root `node` user.
USER root

# Install common CLI tools and build dependencies for agents.
RUN set -eux && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        bash-completion \
        bat \
        build-essential \
        ca-certificates \
        chromium \
        curl \
        dnsutils \
        fd-find \
        file \
        fzf \
        gh \
        git-lfs \
        gnupg \
        iproute2 \
        iputils-ping \
        jq \
        less \
        lsof \
        nano \
        netcat-openbsd \
        openssh-client \
        pkg-config \
        postgresql-client \
        procps \
        psmisc \
        python3 \
        python3-dev \
        python3-pip \
        python3-venv \
        redis-tools \
        ripgrep \
        rsync \
        socat \
        sqlite3 \
        strace \
        sudo \
        tmux \
        tree \
        unzip \
        vim-tiny \
        wget \
        xz-utils \
        zip \
        zstd \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

# Setup sudo for the `node` user.
RUN echo "node ALL=(ALL) NOPASSWD:ALL" >/etc/sudoers.d/node && \
    chmod 0440 /etc/sudoers.d/node

# Debian renames some binaries; provide the conventional names.
RUN ln -sf /usr/bin/batcat /usr/local/bin/bat && \
    ln -sf /usr/bin/fdfind /usr/local/bin/fd

# Switch back to the non-root user.
USER node
