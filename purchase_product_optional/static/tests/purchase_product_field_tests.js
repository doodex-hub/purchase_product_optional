/** @odoo-module */

/**
 * QUnit unit tests -- patch PurchaseOrderLineProductField._onProductTemplateUpdate (BR-01, AC-01).
 *
 * Provenance: [HASIL-BACA]. Ditulis oleh BACKFILL (Step 04, backfill, 2026-07-28) -- BELUM
 * dieksekusi lewat browser/QUnit runner sungguhan.
 *
 * !! RISIKO LEBIH TINGGI dari product_configurator_dialog_tests.js !! -- `_onProductTemplateUpdate`
 * di `purchase_product_field.js` memanggil `super._onProductTemplateUpdate(...)` (hasil `patch()`
 * terhadap method milik `purchase_product_matrix`). Panggilan `.call(fakeThis, ...)` di bawah
 * mengandalkan asumsi bahwa `super` di dalam method yang di-patch tetap resolve lewat home-object
 * lexical (bukan lewat `this` runtime) -- ini BENAR secara semantik JS standar, tapi belum
 * dikonfirmasi berjalan aman lewat mekanisme `patch()` khusus Odoo tanpa environment nyata. Kalau
 * test ini gagal karena alasan itu (bukan karena logic branching-nya salah), sesuaikan dengan
 * mounting `PurchaseOrderLineProductField` sungguhan lewat `makeView`, jangan langsung dianggap
 * BR-01 salah.
 */
import { PurchaseOrderLineProductField } from "@purchase_product_matrix/js/purchase_product_field";

const proto = PurchaseOrderLineProductField.prototype;

QUnit.module("purchase_product_optional > _onProductTemplateUpdate (AC-01)", () => {

    function makeFakeFieldThis(rpcResult) {
        const calls = { openProductConfigurator: 0, openGridConfigurator: 0, dialogAdd: [], notificationAdd: [], recordUpdate: [] };
        return {
            calls,
            orm: { call: async () => rpcResult },
            dialog: { add: (...args) => calls.dialogAdd.push(args) },
            notification: { add: (...args) => calls.notificationAdd.push(args) },
            props: { record: { data: { product_template_id: [1, "Test Product"], product_id: false }, update: async (vals) => calls.recordUpdate.push(vals) } },
            context: {},
            _openProductConfigurator: function () { calls.openProductConfigurator++; },
            _openGridConfigurator: function () { calls.openGridConfigurator++; },
        };
    }

    QUnit.test("AC-01-02: single variant tanpa optional products -> record di-update langsung, dialog TIDAK dibuka", async (assert) => {
        const fakeThis = makeFakeFieldThis({
            product_id: { id: 55 }, product_name: "Variant A", has_optional_products: false,
        });
        await proto._onProductTemplateUpdate.call(fakeThis);
        assert.strictEqual(fakeThis.calls.openProductConfigurator, 0, "dialog configurator TIDAK dibuka");
        assert.strictEqual(fakeThis.calls.recordUpdate.length, 1, "record.update dipanggil sekali");
        assert.deepEqual(fakeThis.calls.recordUpdate[0], { product_id: [55, "Variant A"] });
    });

    QUnit.test("AC-01-01: single variant DENGAN optional products -> dialog configurator dibuka, record TIDAK di-update langsung", async (assert) => {
        const fakeThis = makeFakeFieldThis({
            product_id: { id: 55 }, product_name: "Variant A", has_optional_products: true,
        });
        await proto._onProductTemplateUpdate.call(fakeThis);
        assert.strictEqual(fakeThis.calls.openProductConfigurator, 1, "AC-01-01: dialog configurator dibuka");
        assert.strictEqual(fakeThis.calls.recordUpdate.length, 0, "AC-01-01: record TIDAK langsung di-update");
    });

    QUnit.test("AC-01-03: purchase_warning type=block -> WarningDialog ditampilkan, product_template_id direset", async (assert) => {
        const fakeThis = makeFakeFieldThis({
            purchase_warning: { type: "block", title: "Blocked", message: "Cannot buy this" },
        });
        await proto._onProductTemplateUpdate.call(fakeThis);
        assert.strictEqual(fakeThis.calls.dialogAdd.length, 1, "AC-01-03: WarningDialog ditambahkan");
        assert.strictEqual(fakeThis.calls.recordUpdate.length, 1);
        assert.deepEqual(fakeThis.calls.recordUpdate[0], { product_template_id: false });
    });

    QUnit.test("AC-01-04: purchase_warning type=warning -> notification ditambahkan, alur lanjut ke mode", async (assert) => {
        const fakeThis = makeFakeFieldThis({
            purchase_warning: { type: "warning", title: "Heads up", message: "Just a note" },
            mode: "configurator",
        });
        await proto._onProductTemplateUpdate.call(fakeThis);
        assert.strictEqual(fakeThis.calls.notificationAdd.length, 1, "AC-01-04: notification ditambahkan");
        assert.strictEqual(fakeThis.calls.openProductConfigurator, 1, "AC-01-04: alur tetap lanjut buka dialog configurator");
    });

    QUnit.test("AC-01-05: mode kosong -> default buka dialog configurator (bukan grid)", async (assert) => {
        const fakeThis = makeFakeFieldThis({});
        await proto._onProductTemplateUpdate.call(fakeThis);
        assert.strictEqual(fakeThis.calls.openProductConfigurator, 1, "AC-01-05: default configurator");
        assert.strictEqual(fakeThis.calls.openGridConfigurator, 0);
    });

    QUnit.test("AC-01-06: mode != 'configurator' -> buka grid configurator", async (assert) => {
        const fakeThis = makeFakeFieldThis({ mode: "matrix" });
        await proto._onProductTemplateUpdate.call(fakeThis);
        assert.strictEqual(fakeThis.calls.openGridConfigurator, 1, "AC-01-06: grid configurator dibuka");
        assert.strictEqual(fakeThis.calls.openProductConfigurator, 0);
    });
});
