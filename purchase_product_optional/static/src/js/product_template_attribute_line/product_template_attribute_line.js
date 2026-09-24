/** @odoo-module */

import { Component, t, useProps } from "@odoo/owl";
import { formatCurrency } from "@web/core/currency";
import { BadgeExtraPrice } from "../badge_extra_price/badge_extra_price";

export class ProductTemplateAttributeLine extends Component {
    static components = { BadgeExtraPrice };
    static template = "purchaseProductConfigurator.ptal";
    props = useProps({
        productTmplId: t.number(),
        id: t.number(),
        attribute: t.object({
            id: t.number(),
            name: t.string(),
            display_type: t.customValidator(
                t.string(),
                (type) => ["color", "multi", "pills", "radio", "select"].includes(type)
            ),
        }),
        attribute_values: t.array(
            t.object({
                id: t.number(),
                name: t.string(),
                html_color: t.or([t.boolean(), t.string()]), // backend sends 'false' when there is no color
                image: t.or([t.boolean(), t.string()]), // backend sends 'false' when there is no image set
                is_custom: t.boolean(),
                price_extra: t.number(),
                excluded: t.boolean().optional(),
            })
        ),
        selected_attribute_value_ids: t.array(t.number()),
        create_variant: t.customValidator(
            t.string(),
            (type) => ["always", "dynamic", "no_variant"].includes(type)
        ),
        customValue: t.or([t.literal(false), t.string()]).optional(),
    });

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * Update the selected PTAV in the state.
     *
     * @param {Event} event
     */
    updateSelectedPTAV(event) {
        this.env.updateProductTemplateSelectedPTAV(
            this.props.productTmplId, this.props.id, event.target.value, this.props.attribute.display_type == 'multi'
        );
    }

    /**
     * Update in the state the custom value of the selected PTAV.
     *
     * @param {Event} event
     */
    updateCustomValue(event) {
        this.env.updatePTAVCustomValue(
            this.props.productTmplId, this.props.selected_attribute_value_ids[0], event.target.value
        );
    }

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Return template name to use by checking the display type in the props.
     *
     * Each attribute line can have one of this five display types:
     *      - 'Color'  : Display each attribute as a circle filled with said color.
     *      - 'Pills'  : Display each attribute as a rectangle-shaped element.
     *      - 'Radio'  : Display each attribute as a radio element.
     *      - 'Select' : Display each attribute in a selection tag.
     *      - 'Multi'  : Display each attribute in a multi-checkbox tag.
     *
     * @return {String} - The template name to use.
     */
    getPTAVTemplate() {
        switch(this.props.attribute.display_type) {
            case 'color':
                return 'purchaseProductConfigurator.ptav-color';
            case 'multi':
                return 'purchaseProductConfigurator.ptav-multi';
            case 'pills':
                return 'purchaseProductConfigurator.ptav-pills';
            case 'radio':
                return 'purchaseProductConfigurator.ptav-radio';
            case 'select':
                return 'purchaseProductConfigurator.ptav-select';
        }
    }

    /**
     * Return the name of the PTAV
     *
     * In the selection HTML tag, it is impossible to show the component `BadgeExtraPrice`. Append
     * the extra price to the name to ensure that the extra price will be shown.
     * Note: used in `purchaseProductConfigurator.ptav-select`.
     *
     * @param {Object} ptav - The attribute, as a `product.template.attribute.value` summary dict.
     * @return {String} - The name of the PTAV.
     */
    getPTAVSelectName(ptav) {
        if (ptav.price_extra) {
            const sign = ptav.price_extra > 0 ? '+' : '-';
            const price = formatCurrency(
                Math.abs(ptav.price_extra), this.env.currencyId
            );
            return ptav.name +" ("+ sign + " " + price + ")";
        } else {
            return ptav.name;
        }
    }

    /**
     * Check if the selected ptav is custom or not.
     *
     * @return {Boolean} - Whether the selected ptav is custom or not.
     */
    isSelectedPTAVCustom() {
        return this.props.attribute_values.find(
            ptav => this.props.selected_attribute_value_ids.includes(ptav.id)
        )?.is_custom;
    }

    get showValuesChoice() {
        return this.props.attribute_values.length > 1
            || this.props.attribute.display_type == 'multi'
    }

    /**
     * Check if the line has a custom ptav or not.
     *
     * @return {Boolean} - Whether the line has a custom ptav or not.
     */
    hasPTAVCustom() {
        return this.props.attribute_values.some(
            ptav => ptav.is_custom
        );
    }
 }
