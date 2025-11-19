FROM ghcr.io/berriai/litellm-database:main-latest

# Install patch utility
RUN apk add --no-cache patch

# Copy and apply patches
COPY patches/litellm-github-copilot-responses.patch /tmp/
RUN cd /usr/lib/python3.13/site-packages && patch -p1 < /tmp/litellm-github-copilot-responses.patch
