/** @odoo-module */

/**
 * Tour -- alur happy path Product Configurator di Purchase Order (Smoke Test #1, 04A_DEV_TESTING.md).
 *
 * Provenance: [HASIL-BACA]. Ditulis oleh BACKFILL (Step 04, backfill, 2026-07-28) -- BELUM
 * dieksekusi lewat Chrome headless sungguhan. Selector CSS di bawah didasarkan pola umum tour Odoo
 * 17 (`.o_list_button_add`, `.o_field_widget[name=...]`, dst) -- BUKAN diverifikasi langsung ke DOM
 * modul ini. Sangat mungkin perlu penyesuaian selector setelah run pertama (Mode B) -- itu bagian
 * normal dari proses, bukan tanda BR-01/BR-05/BR-09 salah.
 */
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("purchase_product_optional_happy_path", {
    test: true,
    url: "/odoo/purchase",
    steps: () => [
        {
            content: "Buka Purchase Order baru",
            trigger: ".o_list_button_add",
            run: "click",
        },
        {
            content: "Pilih vendor",
            trigger: ".o_field_widget[name=partner_id] input",
            run: "edit F-02/F-03 Test Vendor",
        },
        {
            content: "Konfirmasi vendor dari dropdown",
            trigger: ".o_field_widget[name=partner_id] .ui-menu-item > a",
            run: "click",
        },
        {
            content: "Tambah baris Purchase Order",
            trigger: ".o_field_x2many_list_row_add > a",
            run: "click",
        },
        {
            content: "Pilih produk configurable (punya optional products)",
            trigger: ".o_field_widget[name=product_template_id] input",
            run: "edit Tour Configurable Product",
        },
        {
            content: "Konfirmasi produk dari dropdown -> dialog Product Configurator diharapkan terbuka",
            trigger: ".ui-menu-item > a:contains('Tour Configurable Product')",
            run: "click",
        },
        {
            content: "Dialog Product Configurator terbuka (BR-01)",
            trigger: ".modal .o_purchase_product_configurator, .modal:contains('Configure your product')",
        },
        {
            content: "Confirm dialog (harga sudah dihitung, BR-05/BR-09)",
            trigger: ".modal footer button.btn-primary",
            run: "click",
        },
        {
            content: "Baris PO tersimpan -- dialog tertutup",
            trigger: ".o_form_view:not(:has(.modal))",
        },
    ],
});
