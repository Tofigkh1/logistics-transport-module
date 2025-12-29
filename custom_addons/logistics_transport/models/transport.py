# -*- coding: utf-8 -*-
from odoo import models, fields, api


# class Transport(models.Model):
#     _name = 'logistics.transport'
#     _description = 'Transport Model'

#     name = fields.Char(
#         string='Reference',
#         required=True,
#         default='New'
#     )

#     carrier_id = fields.Many2one(
#         'res.partner',
#         string='Carrier',
#         required=True
#     )
#     carrier_contact = fields.Char(
#         string='Carrier Contact'
#     )
#     carrier_phone = fields.Char(
#         string='Carrier Phone',
#         related='carrier_id.phone',
#         readonly=True
#     )
#     carrier_email = fields.Char(
#         string='Carrier Email',
#         related='carrier_id.email',
#         readonly=True
#     )




class LogisticsTransport(models.Model):
    _name = 'logistics.transport'
    _description = 'Logistics Transport'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: 'New'
    )
    
    # Daşıyıcı məlumatları
    carrier_id = fields.Many2one(
        'res.partner',
        string='Carrier',
        required=True,
        tracking=True,
        domain="[('is_company', '=', True)]",
        help='Select the carrier/transport company'
    )
    carrier_contact = fields.Char(
        string='Carrier Contact',
        help='Contact person at carrier company'
    )
    carrier_phone = fields.Char(
        string='Carrier Phone',
        related='carrier_id.phone',
        readonly=True
    )
    carrier_email = fields.Char(
        string='Carrier Email',
        related='carrier_id.email',
        readonly=True
    )
    
    # Çatdırılma müddəti
    date_departure = fields.Datetime(
        string='Departure Date',
        required=True,
        tracking=True,
        default=fields.Datetime.now
    )
    date_arrival = fields.Datetime(
        string='Expected Arrival Date',
        required=True,
        tracking=True
    )
    delivery_duration = fields.Integer(
        string='Delivery Duration (Days)',
        compute='_compute_delivery_duration',
        store=True,
        help='Calculated delivery duration in days'
    )
    
    # Haradan
    origin_address = fields.Text(
        string='Origin Address',
        required=True,
        help='Full address of origin location'
    )
    origin_city = fields.Char(
        string='Origin City',
        required=True
    )
    origin_country_id = fields.Many2one(
        'res.country',
        string='Origin Country',
        required=True
    )
    
    # Haraya
    destination_address = fields.Text(
        string='Destination Address',
        required=True,
        help='Full address of destination location'
    )
    destination_city = fields.Char(
        string='Destination City',
        required=True
    )
    destination_country_id = fields.Many2one(
        'res.country',
        string='Destination Country',
        required=True
    )
    
    transport_mode = fields.Selection([
        ('road', 'Road Transport'),
        ('rail', 'Rail Transport'),
        ('sea', 'Sea Freight'),
        ('air', 'Air Freight'),
        ('multimodal', 'Multimodal'),
    ], string='Transport Mode', required=True, default='road', tracking=True)


    incoterm = fields.Selection([
        ('EXW', 'EXW - Ex Works'),
        ('FCA', 'FCA - Free Carrier'),
        ('CPT', 'CPT - Carriage Paid To'),
        ('CIP', 'CIP - Carriage and Insurance Paid To'),
        ('DAP', 'DAP - Delivered at Place'),
        ('DPU', 'DPU - Delivered at Place Unloaded'),
        ('DDP', 'DDP - Delivered Duty Paid'),
        ('FAS', 'FAS - Free Alongside Ship'),
        ('FOB', 'FOB - Free on Board'),
        ('CFR', 'CFR - Cost and Freight'),
        ('CIF', 'CIF - Cost, Insurance and Freight'),
    ], string='Incoterm', help='International Commercial Terms')
    

    transport_line_ids = fields.One2many(
        'logistics.transport.line',
        'transport_id',
        string='Products'
    )
    
  
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    
    notes = fields.Text(string='Notes')
    
    total_weight = fields.Float(
        string='Total Weight (kg)',
        compute='_compute_totals',
        store=True
    )
    total_volume = fields.Float(
        string='Total Volume (m³)',
        compute='_compute_totals',
        store=True
    )
    total_quantity = fields.Float(
        string='Total Quantity',
        compute='_compute_totals',
        store=True
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('logistics.transport') or 'New'
                # return super().create(vals_list)
        return super(LogisticsTransport, self).create(vals_list)


        

    #       @api.depends('date_departure', 'date_arrival')
    # def _compute_delivery_duration(self):
    #     for record in self:
    #         if record.date_departure and record.date_arrival:
    #             delta = record.date_arrival - record.date_departure
    #             record.delivery_duration = delta.total_seconds() / (24 * 3600)
    #         else:
    #             record.delivery_duration = 0.0

    
    @api.depends('date_departure', 'date_arrival')
    def _compute_delivery_duration(self):
        for record in self:
            if record.date_departure and record.date_arrival:
                delta = record.date_arrival - record.date_departure
                record.delivery_duration = int(delta.total_seconds() / (24 * 3600))
            else:
                record.delivery_duration = 0
    
    @api.depends('transport_line_ids.quantity', 'transport_line_ids.weight', 'transport_line_ids.volume')
    def _compute_totals(self):
        for record in self:
            record.total_quantity = sum(record.transport_line_ids.mapped('quantity'))
            record.total_weight = sum(record.transport_line_ids.mapped('weight'))
            record.total_volume = sum(record.transport_line_ids.mapped('volume'))
    
    def action_confirm(self):
        self.write({'state': 'confirmed'})
    
    def action_in_transit(self):
        self.write({'state': 'in_transit'})
    
    def action_deliver(self):
        self.write({'state': 'delivered'})
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})
    
    def action_draft(self):
        self.write({'state': 'draft'})


class LogisticsTransportLine(models.Model):
    _name = 'logistics.transport.line'
    _description = 'Logistics Transport Line'
    
    transport_id = fields.Many2one(
        'logistics.transport',
        string='Transport',
        required=True,
        ondelete='cascade'
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True
    )
    product_uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        related='product_id.uom_id',
        readonly=True
    )
    description = fields.Html(
        string='Description',
        related='product_id.description',
        readonly=True
    )
    quantity = fields.Float(
        string='Quantity',
        required=True,
        default=1.0
    )
    weight = fields.Float(
        string='Weight (kg)',
        help='Total weight in kilograms'
    )
    volume = fields.Float(
        string='Volume (m³)',
        help='Total volume in cubic meters'
    )
    package_type = fields.Selection([
        ('box', 'Box'),
        ('pallet', 'Pallet'),
        ('container', 'Container'),
        ('bulk', 'Bulk'),
        ('other', 'Other'),
    ], string='Package Type', default='box')
    notes = fields.Text(string='Notes')

