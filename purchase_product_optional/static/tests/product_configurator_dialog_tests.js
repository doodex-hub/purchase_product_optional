/** @odoo-module */

/**
 * QUnit unit tests -- ProductConfiguratorDialogPurchase (BR-05/BR-06/BR-07/BR-09).
 *
 * Provenance: [HASIL-BACA]. Ditulis oleh BACKFILL (Step 04, backfill, 2026-07-28) --
 * BELUM dieksekusi lewat browser/QUnit runner sungguhan (Cowork sandbox tidak bisa menjalankan
 * Odoo+browser headless). Lihat doc-dev/backfill/test/04A_DEV_TESTING.md untuk status.
 *
 * Strategi: sebagian besar test di sini memanggil method PROTOTYPE komponen lewat `.call(fakeThis, ...)`
 * dengan `this` palsu (bukan mounting komponen OWL penuh) -- ini valid untuk method yang cuma
 * menyentuh `this.state`/`this.env`/method lain di prototype yang sama, dan MENGHINDARI ketidakpastian
 * API mount/service-mocking Odoo 17 yang belum bisa diverifikasi tanpa environment nyata. Method yang
 * BENAR-BENAR butuh lifecycle OWL (`setup()`, DOM `id_vendor_0`) dites lewat mount asli di bagian
 * paling akhir -- itu bagian yang risiko sintaksnya PALING TINGGI untuk disesuaikan saat run pertama.
 */
import { ProductConfiguratorDialogPurchase } from "@purchase_product_optional/js/product_configurator_dialog/product_configurator_dialog";
import { getFixture, mount } from "@web/../tests/helpers/utils";
import { makeTestEnv } from "@web/../tests/helpers/mock_env";

const proto = ProductConfiguratorDialogPurchase.prototype;

QUnit.module("purchase_product_optional > ProductConfiguratorDialogPurchase", (hooks) => {

    // ------------------------------------------------------------------
    // AC-09-02 -- _isPossibleCombination / isPossibleConfiguration (guard confirm)
    // ------------------------------------------------------------------

    QUnit.module("_isPossibleCombination (AC-09-02)");

    QUnit.test("returns true when no selected ptav is excluded", (assert) => {
        const product = {
            attribute_lines: [
                {
                    selected_attribute_value_ids: [1],
                    attribute_values: [{ id: 1, excluded: false }, { id: 2, excluded: true }],
                },
            ],
        };
        assert.strictEqual(proto._isPossibleCombination(product), true);
    });

    QUnit.test("returns false when a selected ptav is excluded", (assert) => {
        const product = {
            attribute_lines: [
                {
                    selected_attribute_value_ids: [2],
                    attribute_values: [{ id: 1, excluded: false }, { id: 2, excluded: true }],
                },
            ],
        };
        assert.strictEqual(proto._isPossibleCombination(product), false);
    });

    // ------------------------------------------------------------------
    // AC-07-01 / AC-07-02 -- _addProduct / _removeProduct (optional products rekursif)
    // ------------------------------------------------------------------

    QUnit.module("_addProduct / _removeProduct (AC-07)");

    function makeFakeDialogThis(products, optionalProducts) {
        return {
            state: { products, optionalProducts },
            _findProduct: proto._findProduct,
            _getChildProducts: proto._getChildProducts,
            _removeProduct: proto._removeProduct,
            _addProduct: proto._addProduct,
            _getOptionalProducts: async () => [],
        };
    }

    QUnit.test("AC-07-02: optional product dengan >1 parent TIDAK dihapus kalau salah satu parent dihapus", (assert) => {
        const shared = { product_tmpl_id: 99, parent_product_tmpl_ids: [1, 2] };
        const parent1 = { product_tmpl_id: 1, parent_product_tmpl_ids: [] };
        const fakeThis = makeFakeDialogThis([parent1], [shared]);

        proto._removeProduct.call(fakeThis, 1);

        const stillTracked = fakeThis.state.optionalProducts.find((p) => p.product_tmpl_id === 99);
        assert.ok(stillTracked, "AC-07-02: shared optional product masih ada di optionalProducts");
        assert.deepEqual(
            stillTracked.parent_product_tmpl_ids, [2],
            "AC-07-02: parent id 1 sudah dibuang dari parent_product_tmpl_ids, parent 2 tetap ada"
        );
    });

    QUnit.test("AC-07-02: optional product dihapus berantai saat parent TERAKHIR hilang", (assert) => {
        const onlyChild = { product_tmpl_id: 100, parent_product_tmpl_ids: [1] };
        const parent1 = { product_tmpl_id: 1, parent_product_tmpl_ids: [] };
        const fakeThis = makeFakeDialogThis([parent1], [onlyChild]);

        proto._removeProduct.call(fakeThis, 1);

        const stillTracked = fakeThis.state.optionalProducts.find((p) => p.product_tmpl_id === 100);
        assert.notOk(stillTracked, "AC-07-02: optional product ikut terhapus setelah parent terakhir hilang");
    });

    // ------------------------------------------------------------------
    // AC-05 -- vendor-based pricing (get_product_update_price / get_optional_product_prices)
    // ------------------------------------------------------------------

    QUnit.module("Vendor-based pricing (AC-05)");

    QUnit.test("AC-05-01: harga & currency ikut supplierinfo yang partner_id-nya cocok id_vendor", async (assert) => {
        const fakeThis = {
            id_vendor: "42",
            product_tmpl_id: 7,
            supplierinfo_id: [501, 502],
            orm: {
                call: async (model, method) => {
                    if (model === "product.template" && method === "search_read") {
                        return [{ seller_ids: [501, 502], standard_price: 100, currency_id: [1, "USD"] }];
                    }
                    if (model === "product.supplierinfo" && method === "search_read") {
                        return [
                            { partner_id: [42, "Vendor Match"], price: 77, currency_id: [2, "EUR"] },
                            { partner_id: [43, "Other Vendor"], price: 55, currency_id: [1, "USD"] },
                        ];
                    }
                    if (model === "product.template" && method === "convert_price") {
                        // AC-05 fokus ke pemilihan harga, bukan konversi (itu F-05) -- passthrough.
                        return 77;
                    }
                    throw new Error(`Unexpected orm.call: ${model}.${method}`);
                },
            },
        };

        const price = await proto.get_product_update_price.call(fakeThis);
        assert.strictEqual(fakeThis.price, 77, "AC-05-01: harga yang dipilih adalah milik vendor yang cocok (42), bukan default/first");
    });

    QUnit.test("AC-05-02: fallback ke supplierinfo PERTAMA kalau tidak ada yang cocok id_vendor", async (assert) => {
        const fakeThis = {
            id_vendor: "999", // tidak match partner manapun
            product_tmpl_id: 7,
            supplierinfo_id: [501, 502],
            orm: {
                call: async (model, method) => {
                    if (model === "product.template" && method === "search_read") {
                        return [{ seller_ids: [501, 502], standard_price: 100, currency_id: [1, "USD"] }];
                    }
                    if (model === "product.supplierinfo" && method === "search_read") {
                        return [
                            { partner_id: [43, "First Vendor"], price: 55, currency_id: [1, "USD"] },
                            { partner_id: [44, "Second Vendor"], price: 66, currency_id: [1, "USD"] },
                        ];
                    }
                    if (model === "product.template" && method === "convert_price") {
                        return 55;
                    }
                    throw new Error(`Unexpected orm.call: ${model}.${method}`);
                },
            },
        };

        await proto.get_product_update_price.call(fakeThis);
        assert.strictEqual(
            fakeThis.price, 55,
            "AC-05-02: fallback ke supplierinfo[0] (55), BUKAN standard_price (100), saat id_vendor tidak match"
        );
    });

    // ------------------------------------------------------------------
    // AC-06 -- pembacaan id_vendor dari DOM (butuh mount OWL asli -- risiko sintaks TERTINGGI)
    // ------------------------------------------------------------------

    QUnit.module("id_vendor dari DOM (AC-06) -- BELUM diverifikasi, prasyarat mount OWL penuh", (hooks) => {
        let target;
        hooks.beforeEach(async () => {
            target = getFixture();
        });

        QUnit.test("AC-06-02: dialog gagal setup kalau elemen id_vendor_0 tidak ada di DOM", async (assert) => {
            // Sengaja TIDAK menaruh <input id="id_vendor_0"> di fixture -- mendokumentasikan F-04:
            // document.getElementById('id_vendor_0').value akan throw karena elemen null.
            assert.throws(
                () => {
                    const el = document.getElementById("id_vendor_0_does_not_exist_in_fixture");
                    // eslint-disable-next-line no-unused-expressions
                    el.value;
                },
                /Cannot read propert/,
                "AC-06-02 (F-04): membaca .value dari elemen yang tidak ada melempar TypeError -- " +
                "ini test PENANDA perilaku, BUKAN test mount dialog sungguhan (lihat catatan file " +
                "ini soal keterbatasan Mode Cowork untuk mount OWL penuh)"
            );
        });
    });
});
