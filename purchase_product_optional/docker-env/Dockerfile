# Migration testing (18.0 -> 19.0), Step 6/9 - adds a real headless-Chrome binary + websocket
# client so Odoo's own test runner (HttpCase.start_tour / browser_js) can execute the Tour test
# (static/tests/tours/purchase_product_optional_tour.js). Do NOT override entrypoint/command in
# docker-compose.yml - losing the official entrypoint breaks HOST/USER/PASSWORD env var translation.
#
# pip3 install --break-system-packages <pkg> || pip3 install <pkg> fallback pattern is REQUIRED
# (migration-tool/templates/Dockerfile.template) - odoo image base varies whether pip enforces
# PEP 668 or not, hardcoding either form breaks the other direction.
FROM odoo:19.0
USER root
RUN apt-get update && apt-get install -y --no-install-recommends wget gnupg ca-certificates \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends google-chrome-stable \
    && rm -rf /var/lib/apt/lists/* \
    && (pip3 install --break-system-packages websocket-client || pip3 install websocket-client)
USER odoo
