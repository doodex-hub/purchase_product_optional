/** @odoo-module */
import { PurchaseOrderLineProductField } from '@purchase_product_matrix/js/purchase_product_field';
import { serializeDateTime } from "@web/core/l10n/dates";
import { x2ManyCommands } from "@web/core/orm_service";
import { WarningDialog } from "@web/core/errors/error_dialogs";
import { useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";
import { ProductConfiguratorDialogPurchase } from "./product_configurator_dialog/product_configurator_dialog";
import { useRecordObserver } from "@web/model/relational_model/utils";
import { useMatrixConfigurator } from "@product_matrix/js/matrix_configurator_hook";

async function applyProductPurchase(record, product) {
    const customAttributesCommands = [
        x2ManyCommands.set([]),  // Command.clear isn't supported in static_list/_applyCommands
    ];
    for (const ptal of product.attribute_lines) {
        const selectedCustomPTAV = ptal.attribute_values.find(
            ptav => ptav.is_custom && ptal.selected_attribute_value_ids.includes(ptav.id)
        );
        if (selectedCustomPTAV) {
            customAttributesCommands.push(
                x2ManyCommands.create(undefined, {
                    custom_product_template_attribute_value_id: { id: selectedCustomPTAV.id, display_name: "we don't care" },
                    custom_value: ptal.customValue,
                })
            );
        }
    }

    const noVariantPTAVIds = product.attribute_lines.filter(
        ptal => ptal.create_variant === "no_variant"
    ).flatMap(ptal => ptal.selected_attribute_value_ids);

    await record.update({
        product_id: { id: product.id, display_name: product.display_name },
        // product_qty: 4,
        product_no_variant_attribute_value_ids: [x2ManyCommands.set(noVariantPTAVIds)],
        product_custom_attribute_value_ids: customAttributesCommands,
    });
    await record.update({
        product_qty: product.quantity
    });
    
}


patch(PurchaseOrderLineProductField.prototype, {
    setup() {
        super.setup(...arguments);

        this.dialog = useService("dialog");
        this.notification = useService("notification");
        this.orm = useService("orm");
        this.matrixConfigurator = useMatrixConfigurator();
    },

    async _onProductTemplateUpdate() {
        super._onProductTemplateUpdate(...arguments);

        const result = await this.orm.call(
            'product.template',
            'get_single_product_variant',
            [this.props.record.data.product_template_id.id],
            {
                context: this.context,
            }
        );

        if (result && result.product_id) {
            if (this.props.record.data.product_id != result.product_id.id) {
                if (result.has_optional_products) {
                    this._openProductConfigurator();
                } else {
                    await this.props.record.update({
                        product_id: { id: result.product_id, display_name: result.product_name },
                    });
                }
            }
        } else {
            if (result && result.purchase_warning) {
                const { type, title, message } = result.purchase_warning;
                if (type === 'block') {
                    this.dialog.add(WarningDialog, { title, message });
                    this.props.record.update({ 'product_template_id': false });
                    return;
                } else if (type == 'warning') {
                    this.notification.add(message, { title, type: "warning" });
                }
            }

            if (!result.mode || result.mode === 'configurator') {
                this._openProductConfigurator();
            } else {
                this.matrixConfigurator.open(this.props.record, false);
            }
        }
    },

    onEditConfiguration() {
        super.onEditConfiguration(...arguments);
        if (this.props.record.data.is_configurable_product) {
            this._openProductConfigurator(true);
        }
    },

    async _openProductConfigurator(edit = false) {
        const purchaseOrderRecord = this.props.record.model.root;
        let ptavIds = this.props.record.data.product_template_attribute_value_ids?.records?.map(record => record.resId) || [];
        let customAttributeValues = [];
    
        if (edit) {
            ptavIds = ptavIds.concat(this.props.record.data.product_no_variant_attribute_value_ids?.records?.map(record => record.resId) || []);
            // `record.data` (relational_model) many2one fields are `{id, display_name}` objects,
            // while `orm.read()` RPC results still return the legacy `[id, display_name]` tuple —
            // normalize both branches to a plain id here so the downstream `.map()` below stays
            // format-agnostic.
            customAttributeValues = this.props.record.data.product_custom_attribute_value_ids?.records?.[0]?.isNew
                ? this.props.record.data.product_custom_attribute_value_ids.records.map(record => ({
                    custom_product_template_attribute_value_id: record.data.custom_product_template_attribute_value_id?.id,
                    custom_value: record.data.custom_value,
                }))
                : (await this.orm.read(
                    'product.attribute.custom.value',
                    this.props.record.data.product_custom_attribute_value_ids?.currentIds || [],
                    ["custom_product_template_attribute_value_id", "custom_value"]
                )).map(data => ({
                    custom_product_template_attribute_value_id: data.custom_product_template_attribute_value_id?.[0],
                    custom_value: data.custom_value,
                }));
        }

        this.dialog.add(ProductConfiguratorDialogPurchase, {
            productTemplateId: this.props.record.data.product_template_id?.id,
            ptavIds: ptavIds,
            customAttributeValues: customAttributeValues.map(data => ({
                ptavId: data.custom_product_template_attribute_value_id,
                value: data.custom_value,
            })),
            quantity: this.props.record.data.product_qty,
            productUOMId: this.props.record.data.product_uom?.id,
            companyId: purchaseOrderRecord.data.company_id?.id,
            pricelistId: purchaseOrderRecord.data.pricelist_id?.id,
            currencyId: this.props.record.data.currency_id?.id,
            soDate: serializeDateTime(purchaseOrderRecord.data.date_order),
            edit: edit,
            save: async (mainProduct, optionalProducts) => {
                await applyProductPurchase(this.props.record, mainProduct);

                console.log('Main Product Quantity:', mainProduct.quantity);
                // await this._onProductUpdate();
                // purchaseOrderRecord.data.order_line.leaveEditMode();

                for (const optionalProduct of optionalProducts) {
                    const line = await purchaseOrderRecord.data.order_line.addNewRecord({
                        position: 'bottom',
                        mode: "readonly",
                    });
                    await applyProductPurchase(line, optionalProduct);
                    console.log('tes')
                }
            },            
            discard: () => {
                purchaseOrderRecord.data.order_line.delete(this.props.record);
            },
        });
    },
})