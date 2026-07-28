# -*- coding: utf-8 -*-
"""Karakterisasi BR-02/BR-03/F-02/F-03/F-05 — onchange_partner_id & convert_price.

Provenance: [HASIL-BACA]. Test di file ini mendokumentasikan PERILAKU SEKARANG (termasuk
kandidat bug F-02/F-05), BUKAN memperbaikinya — lihat doc-dev/backfill/FINDINGS.md.
Ditulis oleh BACKFILL (Step 04, backfill), belum dieksekusi via Odoo+Postgres nyata di sesi
Cowork ini (sandbox tidak bisa menjalankan live server) — lihat serah-terima Mode B di
doc-dev/backfill/test/04A_DEV_TESTING.md.
"""
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestPurchaseOrderCurrency(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.currency_usd = cls.env.ref('base.USD')
        cls.currency_eur = cls.env.ref('base.EUR')
        # Beberapa environment demo Odoo menonaktifkan currency selain currency perusahaan.
        (cls.currency_usd + cls.currency_eur).sudo().write({'active': True})
        cls.partner = cls.env['res.partner'].create({'name': 'F-02/F-03 Test Vendor'})

    def _make_po(self, currency):
        return self.env['purchase.order'].create({
            'partner_id': self.partner.id,
            'currency_id': currency.id,
        })

    # ------------------------------------------------------------------
    # AC-02 — onchange_partner_id (BR-02 / F-02)
    # ------------------------------------------------------------------

    def test_ac_02_01_onchange_no_partner(self):
        """AC-02-01: tanpa partner_id, currency PO tidak disentuh sama sekali."""
        po = self.env['purchase.order'].new({
            'currency_id': self.currency_usd.id,
        })
        po.onchange_partner_id()
        self.assertEqual(
            po.currency_id, self.currency_usd,
            "AC-02-01: currency tidak berubah kalau partner_id kosong",
        )
        param = self.env['ir.config_parameter'].sudo().get_param('currency_id')
        self.assertEqual(
            int(param), self.currency_usd.id,
            "AC-02-01: currency_id yang sudah ada tetap ditulis ke config param global",
        )

    def test_ac_02_02_onchange_partner_currency_matches(self):
        """AC-02-02: currency partner == currency PO saat ini — assignment jadi no-op observable."""
        self.partner.property_purchase_currency_id = self.currency_usd
        po = self._make_po(self.currency_usd)
        po.onchange_partner_id()
        self.assertEqual(
            po.currency_id, self.currency_usd,
            "AC-02-02: currency tetap sama (assignment ke nilai yang sudah sama)",
        )

    def test_ac_02_03_onchange_partner_currency_differs_bug(self):
        """AC-02-03 (F-02): currency partner BEDA dari currency PO — currency PO TETAP tidak
        berubah, bertentangan dengan docstring method ("update currency based on the partner's
        purchase currency"). Test ini mendokumentasikan bug, bukan perilaku yang diinginkan.
        """
        self.partner.property_purchase_currency_id = self.currency_eur
        po = self._make_po(self.currency_usd)
        po.onchange_partner_id()
        self.assertEqual(
            po.currency_id, self.currency_usd,
            "AC-02-03 (F-02): currency PO TETAP USD, TIDAK ikut EUR milik partner — kalau "
            "assertion ini GAGAL (currency berubah jadi EUR), berarti F-02 sudah diperbaiki "
            "di kode, update FINDINGS.md jadi RESOLVED alih-alih menganggap test ini salah",
        )

    # ------------------------------------------------------------------
    # AC-03 — convert_price (BR-03 / F-03 / F-05)
    # ------------------------------------------------------------------

    def test_ac_03_01_convert_price_same_currency(self):
        """AC-03-01: short-circuit — currency sama dengan config param, harga apa adanya."""
        self.env['ir.config_parameter'].sudo().set_param(
            'currency_id', str(self.currency_usd.id)
        )
        price = self.env['product.template'].convert_price(100.0, self.currency_usd.id)
        self.assertEqual(price, 100.0, "AC-03-01: harga dikembalikan tanpa konversi")

    def test_ac_03_03_convert_price_real_conversion_no_crash(self):
        """AC-03-03 (F-05, REVISI 2026-07-28): hipotesis awal ("convert_price CRASH TypeError
        karena _convert() dipanggil tanpa argumen wajib company/date") TERBUKTI SALAH lewat 3x
        eksekusi Mode B nyata (run #1, #2, #4) -- di versi Odoo 17.0 yang dites, `company` dan
        `date` pada `res.currency._convert()` punya default value, jadi convert_price() tetap
        jalan normal walau currency benar-benar beda. Lihat FINDINGS.md F-05 untuk histori
        lengkap (assertion lama dipertahankan di histori commit, bukan dihapus diam-diam).
        Test ini sekarang mengkarakterisasi perilaku SEBENARNYA: tidak crash, harga terkonversi.
        """
        self.env['ir.config_parameter'].sudo().set_param(
            'currency_id', str(self.currency_usd.id)
        )
        price = self.env['product.template'].convert_price(100.0, self.currency_eur.id)
        self.assertIsInstance(
            price, float,
            "AC-03-03 (F-05 tidak terbukti): convert_price mengembalikan float hasil konversi, "
            "TIDAK crash, meski currency benar-benar beda.",
        )
