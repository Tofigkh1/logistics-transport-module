# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta


class LogisticsShipment(models.Model):
    _name = 'logistics.shipment'
    _description = 'Logistics Shipment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'scheduled_pickup desc, id desc'

    name = fields.Char(
        string='Shipment Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    
    # Customer Information
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        tracking=True,
        domain=[('is_company', '=', True)],
    )
    customer_reference = fields.Char(
        string='Customer Reference',
        help='Customer order or reference number',
    )
    
    # Locations
    origin_id = fields.Many2one(
        'logistics.location',
        string='Origin',
        required=True,
        tracking=True,
        help='Pickup location',
    )
    destination_id = fields.Many2one(
        'logistics.location',
        string='Destination',
        required=True,
        tracking=True,
        help='Delivery location',
    )
    
    # Route and Assignment
    route_id = fields.Many2one(
        'logistics.route',
        string='Route',
        tracking=True,
    )
    vehicle_id = fields.Many2one(
        'logistics.vehicle',
        string='Vehicle',
        tracking=True,
    )
    driver_id = fields.Many2one(
        'logistics.driver',
        string='Driver',
        tracking=True,
    )
    
    # Dates
    scheduled_pickup = fields.Datetime(
        string='Scheduled Pickup',
        required=True,
        tracking=True,
        default=fields.Datetime.now,
    )
    scheduled_delivery = fields.Datetime(
        string='Scheduled Delivery',
        tracking=True,
    )
    actual_pickup = fields.Datetime(
        string='Actual Pickup',
        tracking=True,
    )
    actual_delivery = fields.Datetime(
        string='Actual Delivery',
        tracking=True,
    )
    
    # State
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('dispatched', 'Dispatched'),
            ('in_transit', 'In Transit'),
            ('delivered', 'Delivered'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        tracking=True,
        copy=False,
    )
    
    # Cargo Information
    item_ids = fields.One2many(
        'logistics.shipment.item',
        'shipment_id',
        string='Shipment Items',
        copy=True,
    )
    total_items = fields.Integer(
        string='Total Items',
        compute='_compute_totals',
        store=True,
    )
    total_weight = fields.Float(
        string='Total Weight (kg)',
        compute='_compute_totals',
        store=True,
        help='Total weight in kilograms',
    )
    total_volume = fields.Float(
        string='Total Volume (m³)',
        compute='_compute_totals',
        store=True,
        help='Total volume in cubic meters',
    )
    
    # Capacity Validation
    is_overweight = fields.Boolean(
        string='Overweight',
        compute='_compute_capacity_warnings',
    )
    is_overvolume = fields.Boolean(
        string='Over Volume',
        compute='_compute_capacity_warnings',
    )
    capacity_warning = fields.Char(
        string='Capacity Warning',
        compute='_compute_capacity_warnings',
    )
    
    # Delivery
    delivery_ids = fields.One2many(
        'logistics.delivery',
        'shipment_id',
        string='Delivery Records',
    )
    pod_count = fields.Integer(
        string='POD Count',
        compute='_compute_delivery_stats',
    )
    
    # Integrations
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sales Order',
        tracking=True,
    )
    invoice_ids = fields.One2many(
        'account.move',
        'shipment_id',
        string='Invoices',
    )
    invoice_count = fields.Integer(
        string='Invoice Count',
        compute='_compute_invoice_count',
    )
    
    # Additional Info
    priority = fields.Selection(
        selection=[
            ('0', 'Normal'),
            ('1', 'Low'),
            ('2', 'High'),
            ('3', 'Urgent'),
        ],
        string='Priority',
        default='0',
    )
    notes = fields.Text(
        string='Notes',
    )
    internal_notes = fields.Text(
        string='Internal Notes',
    )
    
    # Computed
    distance_km = fields.Float(
        string='Distance (km)',
        related='route_id.distance_km',
    )
    on_time = fields.Boolean(
        string='On Time',
        compute='_compute_on_time',
        store=True,
    )

    _sql_constraints = [
        ('name_unique', 'unique(name)',
         'Shipment reference must be unique!'),
    ]

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'logistics.shipment'
            ) or _('New')
        return super().create(vals)

    @api.depends('item_ids', 'item_ids.quantity', 'item_ids.weight', 'item_ids.volume')
    def _compute_totals(self):
        for shipment in self:
            shipment.total_items = len(shipment.item_ids)
            shipment.total_weight = sum(
                item.weight * item.quantity for item in shipment.item_ids
            )
            shipment.total_volume = sum(
                item.volume * item.quantity for item in shipment.item_ids
            )

    @api.depends('total_weight', 'total_volume', 'vehicle_id',
                 'vehicle_id.capacity_weight', 'vehicle_id.capacity_volume')
    def _compute_capacity_warnings(self):
        for shipment in self:
            shipment.is_overweight = False
            shipment.is_overvolume = False
            shipment.capacity_warning = ''
            
            if shipment.vehicle_id:
                warnings = []
                if (shipment.vehicle_id.capacity_weight and
                        shipment.total_weight > shipment.vehicle_id.capacity_weight):
                    shipment.is_overweight = True
                    warnings.append(_('Weight exceeds vehicle capacity'))
                if (shipment.vehicle_id.capacity_volume and
                        shipment.total_volume > shipment.vehicle_id.capacity_volume):
                    shipment.is_overvolume = True
                    warnings.append(_('Volume exceeds vehicle capacity'))
                shipment.capacity_warning = ', '.join(warnings)

    @api.depends('delivery_ids')
    def _compute_delivery_stats(self):
        for shipment in self:
            pods = self.env['logistics.proof.of.delivery'].search([
                ('delivery_id', 'in', shipment.delivery_ids.ids),
            ])
            shipment.pod_count = len(pods)

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for shipment in self:
            shipment.invoice_count = len(shipment.invoice_ids)

    @api.depends('scheduled_delivery', 'actual_delivery')
    def _compute_on_time(self):
        for shipment in self:
            if shipment.actual_delivery and shipment.scheduled_delivery:
                shipment.on_time = shipment.actual_delivery <= shipment.scheduled_delivery
            else:
                shipment.on_time = True

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        """Set driver from vehicle's default driver."""
        if self.vehicle_id and self.vehicle_id.driver_id:
            self.driver_id = self.vehicle_id.driver_id

    @api.onchange('origin_id', 'destination_id')
    def _onchange_locations(self):
        """Try to find a matching route."""
        if self.origin_id and self.destination_id:
            route = self.env['logistics.route'].search([
                ('origin_id', '=', self.origin_id.id),
                ('destination_id', '=', self.destination_id.id),
                ('active', '=', True),
            ], limit=1)
            if route:
                self.route_id = route

    @api.onchange('scheduled_pickup', 'route_id')
    def _onchange_compute_delivery_date(self):
        """Estimate delivery date from pickup and route time."""
        if self.scheduled_pickup and self.route_id and self.route_id.estimated_hours:
            self.scheduled_delivery = self.scheduled_pickup + timedelta(
                hours=self.route_id.estimated_hours
            )

    # Workflow Actions
    def action_confirm(self):
        """Confirm the shipment booking."""
        for shipment in self:
            if shipment.state != 'draft':
                raise UserError(_('Only draft shipments can be confirmed.'))
            if not shipment.item_ids:
                raise UserError(_('Please add at least one item to the shipment.'))
            shipment.write({'state': 'confirmed'})

    def action_dispatch(self):
        """Dispatch the shipment with vehicle and driver."""
        for shipment in self:
            if shipment.state != 'confirmed':
                raise UserError(_('Only confirmed shipments can be dispatched.'))
            if not shipment.vehicle_id:
                raise UserError(_('Please assign a vehicle before dispatching.'))
            if not shipment.driver_id:
                raise UserError(_('Please assign a driver before dispatching.'))
            
            # Update vehicle and driver status
            shipment.vehicle_id.write({'status': 'in_use'})
            shipment.driver_id.write({'status': 'on_trip'})
            
            shipment.write({'state': 'dispatched'})

    def action_start_transit(self):
        """Start the delivery - vehicle is in transit."""
        for shipment in self:
            if shipment.state != 'dispatched':
                raise UserError(_('Only dispatched shipments can start transit.'))
            
            # Create delivery record
            self.env['logistics.delivery'].create({
                'shipment_id': shipment.id,
                'status': 'in_transit',
                'departure_time': fields.Datetime.now(),
            })
            
            shipment.write({
                'state': 'in_transit',
                'actual_pickup': fields.Datetime.now(),
            })

    def action_mark_delivered(self):
        """Mark shipment as delivered at destination."""
        for shipment in self:
            if shipment.state != 'in_transit':
                raise UserError(_('Only shipments in transit can be marked as delivered.'))
            
            # Update delivery record
            delivery = shipment.delivery_ids.filtered(
                lambda d: d.status == 'in_transit'
            )
            if delivery:
                delivery.write({
                    'status': 'delivered',
                    'arrival_time': fields.Datetime.now(),
                })
            
            shipment.write({
                'state': 'delivered',
                'actual_delivery': fields.Datetime.now(),
            })

    def action_complete(self):
        """Complete the shipment after POD confirmation."""
        for shipment in self:
            if shipment.state != 'delivered':
                raise UserError(_('Only delivered shipments can be completed.'))
            
            # Release vehicle and driver
            if shipment.vehicle_id:
                shipment.vehicle_id.write({'status': 'available'})
            if shipment.driver_id:
                shipment.driver_id.write({'status': 'available'})
            
            shipment.write({'state': 'done'})

    def action_cancel(self):
        """Cancel the shipment."""
        for shipment in self:
            if shipment.state in ('in_transit', 'delivered', 'done'):
                raise UserError(_(
                    'Cannot cancel a shipment that is in transit, delivered, or completed.'
                ))
            
            # Release vehicle and driver if assigned
            if shipment.vehicle_id and shipment.state == 'dispatched':
                shipment.vehicle_id.write({'status': 'available'})
            if shipment.driver_id and shipment.state == 'dispatched':
                shipment.driver_id.write({'status': 'available'})
            
            shipment.write({'state': 'cancelled'})

    def action_reset_to_draft(self):
        """Reset cancelled shipment to draft."""
        for shipment in self:
            if shipment.state != 'cancelled':
                raise UserError(_('Only cancelled shipments can be reset to draft.'))
            shipment.write({'state': 'draft'})

    # Smart Buttons
    def action_view_invoices(self):
        """Open related invoices."""
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('account.action_move_out_invoice_type')
        if self.invoice_count == 1:
            action['views'] = [(False, 'form')]
            action['res_id'] = self.invoice_ids.id
        else:
            action['domain'] = [('id', 'in', self.invoice_ids.ids)]
        return action

    def action_create_invoice(self):
        """Create invoice for the shipment."""
        self.ensure_one()
        if self.state not in ('delivered', 'done'):
            raise UserError(_('Can only invoice delivered or completed shipments.'))
        
        # Create invoice - simplified version
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.customer_id.id,
            'shipment_id': self.id,
            'invoice_origin': self.name,
            'invoice_line_ids': [(0, 0, {
                'name': f'Shipment: {self.name}',
                'quantity': 1,
                'price_unit': 0.0,  # To be set based on pricing rules
            })],
        }
        invoice = self.env['account.move'].create(invoice_vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
            'target': 'current',
        }


class LogisticsShipmentItem(models.Model):
    _name = 'logistics.shipment.item'
    _description = 'Shipment Item'
    _order = 'sequence, id'

    shipment_id = fields.Many2one(
        'logistics.shipment',
        string='Shipment',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    
    # Item Details
    name = fields.Char(
        string='Description',
        required=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        help='Optional link to product',
    )
    
    # Quantities
    quantity = fields.Float(
        string='Quantity',
        default=1.0,
        required=True,
    )
    uom = fields.Char(
        string='Unit',
        default='pcs',
    )
    
    # Dimensions
    weight = fields.Float(
        string='Weight (kg)',
        help='Weight per unit in kilograms',
    )
    volume = fields.Float(
        string='Volume (m³)',
        help='Volume per unit in cubic meters',
    )
    length = fields.Float(
        string='Length (cm)',
    )
    width = fields.Float(
        string='Width (cm)',
    )
    height = fields.Float(
        string='Height (cm)',
    )
    
    # Computed Totals
    total_weight = fields.Float(
        string='Total Weight',
        compute='_compute_totals',
        store=True,
    )
    total_volume = fields.Float(
        string='Total Volume',
        compute='_compute_totals',
        store=True,
    )
    
    # Package Info
    package_type = fields.Selection(
        selection=[
            ('box', 'Box'),
            ('pallet', 'Pallet'),
            ('crate', 'Crate'),
            ('drum', 'Drum'),
            ('bag', 'Bag'),
            ('container', 'Container'),
            ('other', 'Other'),
        ],
        string='Package Type',
        default='box',
    )
    package_count = fields.Integer(
        string='Number of Packages',
        default=1,
    )
    
    # Special Handling
    is_fragile = fields.Boolean(
        string='Fragile',
    )
    is_hazardous = fields.Boolean(
        string='Hazardous',
    )
    requires_temperature_control = fields.Boolean(
        string='Temperature Controlled',
    )
    special_instructions = fields.Text(
        string='Special Instructions',
    )
    
    notes = fields.Text(
        string='Notes',
    )

    @api.depends('quantity', 'weight', 'volume')
    def _compute_totals(self):
        for item in self:
            item.total_weight = item.quantity * item.weight
            item.total_volume = item.quantity * item.volume

    @api.onchange('length', 'width', 'height')
    def _onchange_dimensions(self):
        """Calculate volume from dimensions."""
        if self.length and self.width and self.height:
            # Convert cm³ to m³
            self.volume = (self.length * self.width * self.height) / 1000000

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Fill details from product."""
        if self.product_id:
            self.name = self.product_id.name
            self.weight = self.product_id.weight
            self.volume = self.product_id.volume


class AccountMove(models.Model):
    _inherit = 'account.move'

    shipment_id = fields.Many2one(
        'logistics.shipment',
        string='Related Shipment',
    )
