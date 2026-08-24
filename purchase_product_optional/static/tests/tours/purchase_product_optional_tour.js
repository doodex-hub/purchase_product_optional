/** @odoo-module **/
// BACKFILL (doc-dev-backfill), Step 07 (Mode E — headless Tour): exercises the real product
// configurator dialog (BR-01/AC-01) through Odoo's own headless Chrome, not a mocked call.
// Companion Python test: tests/test_purchase_product_optional_tour.py

import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("purchase_product_optional_configurator_tour", {
    test: true,
    url: "/web",
    steps: () => [
        {
            // Same pattern as odoo/addons/purchase/static/src/js/tours/purchase.js
            // (stepUtils.showAppsMenuItem()) — the .o_app tiles only render once this is open.
            trigger: ".o_navbar_apps_menu button",
            content: "Open the apps menu",
            run: "click",
        },
        {
            trigger: '.o_app[data-menu-xmlid="purchase.menu_purchase_root"]',
            content: "Open the Purchase app",
            run: "click",
        },
        {
            trigger: ".o_list_button_add",
            content: "Create a new purchase order",
            run: "click",
        },
        {
            trigger: '.o_field_widget[name="partner_id"] input',
            content: "Type the BACKFILL QA vendor name",
            run: "text BACKFILL QA Vendor",
        },
        {
            trigger: '.ui-menu-item > a:contains("BACKFILL QA Vendor")',
            content: "Select the vendor from the dropdown",
            run: "click",
        },
        {
            trigger: ".o_field_x2many_list_row_add > a",
            content: "Add a new order line",
            run: "click",
        },
        {
            trigger: '.o_field_widget[name="product_template_id"] input',
            content: "Type the main product name",
            run: "text BACKFILL QA Main Product",
        },
        {
            trigger: '.ui-menu-item > a:contains("BACKFILL QA Main Product")',
            content: "Select the main product from the dropdown",
            run: "click",
        },
        {
            // NOTE: when a .modal is visible, Odoo's Tour engine (tour_compilers.js
            // `findTrigger()`) auto-scopes the search to `$visibleModal.find(selector)` UNLESS
            // `in_modal: false` is set. A leading `.modal` in the selector therefore asks for a
            // *nested* .modal inside the modal already found — which never exists. Do not prefix
            // these triggers with `.modal` again (that was the bug in the first real run).
            trigger: '.modal-title:contains("Configure your product")',
            content: "BR-01: product configurator dialog opened automatically",
        },
        {
            trigger: 'td:contains("BACKFILL QA Optional Product")',
            content: "BR-01: the optional product is listed in the dialog",
        },
        {
            trigger: 'tr:has(td:contains("BACKFILL QA Optional Product")) button:contains("Add")',
            content: "Add the optional product",
            run: "click",
        },
        {
            trigger: 'button.btn-primary:contains("Confirm")',
            content: "Confirm the configuration",
            run: "click",
        },
        {
            // Not `...Main Product` here: that row's product_template_id field stays focused/in
            // edit mode (an <input>) right after Confirm, and :contains() only matches rendered
            // textContent, not an <input>'s value. The optional line was added with
            // `mode: "readonly"` (purchase_product_field.js `addNewRecord`), so it renders as
            // plain text and is a safe assertion target for "both lines got added".
            trigger: '.o_data_row:contains("BACKFILL QA Optional Product")',
            content: "Optional product line is on the purchase order",
        },
        {
            // Odoo's tour runner fails any tour that ends with a dirty/unsaved form ("Tour
            // finished with an open form view in edition mode") — save explicitly so the tour
            // itself passes cleanly, independent of the actual PO business flow being tested.
            trigger: ".o_form_button_save",
            content: "Save the purchase order",
            run: "click",
        },
        {
            // The save click issues an async RPC (web_save) — without waiting for it to
            // actually finish, the browser session can close mid-save (observed: RPC succeeded
            // but Chrome closed ~130ms later, still flagged as "unsaved"). The breadcrumb only
            // stops showing "New" once the record has a real id/name after web_save resolves.
            trigger: ".o_breadcrumb .active:not(:contains('New'))",
            content: "Wait for the purchase order to actually finish saving",
        },
    ],
});
