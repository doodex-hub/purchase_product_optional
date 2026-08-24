# BACKFILL (doc-dev-backfill), Step 07 Mode E — adds a real headless-Chrome binary + websocket
# client so Odoo's own test runner (HttpCase.start_tour / browser_js) can execute Tour tests. Do
# NOT override entrypoint/command in docker-compose.yml (see
# doc-dev-backfill/ai-doc/USAGE_GUIDE.md §Mode B "menambah package OS/Python ke image" — losing the
# official entrypoint breaks HOST/USER/PASSWORD env var translation to the db connection).
#
# History: `apt-get install chromium` (2026-07-29, first attempt) FAILED — "no installation
# candidate". Root cause found: odoo:17.0's base is Ubuntu 22.04 (jammy), where Ubuntu's own
# `chromium` apt package is a Snap-only transitional stub (no real binary), and Snap doesn't work
# in a plain Docker container. Fix: install Google Chrome from Google's own apt repo instead (same
# approach Odoo's own CI uses) — a real .deb package, not Snap.
FROM odoo:17.0
USER root
RUN apt-get update && apt-get install -y --no-install-recommends wget gnupg ca-certificates \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends google-chrome-stable \
    && pip3 install websocket-client \
    && rm -rf /var/lib/apt/lists/*
USER odoo
