# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class LogisticsProofOfDelivery(models.Model):
    _name = 'logistics.proof.of.delivery'
    _description = 'Proof of Delivery'
    _order = 'timestamp desc'

    name = fields.Char(
        string='POD Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    delivery_id = fields.Many2one(
        'logistics.delivery',
        string='Delivery',
        required=True,
        ondelete='cascade',
    )
    
    # Related fields
    shipment_id = fields.Many2one(
        related='delivery_id.shipment_id',
        string='Shipment',
        store=True,
    )
    customer_id = fields.Many2one(
        related='delivery_id.customer_id',
        string='Customer',
        store=True,
    )
    driver_id = fields.Many2one(
        related='delivery_id.driver_id',
        string='Driver',
        store=True,
    )
    
    # Recipient Information
    recipient_name = fields.Char(
        string='Recipient Name',
        required=True,
        help='Name of the person who received the delivery',
    )
    recipient_id_number = fields.Char(
        string='Recipient ID/Badge Number',
        help='ID or badge number of the recipient',
    )
    recipient_position = fields.Char(
        string='Recipient Position/Title',
        help='Position or job title of the recipient',
    )
    recipient_company = fields.Char(
        string='Recipient Company',
        help='Company name if different from customer',
    )
    
    # Signature and Photos
    signature = fields.Binary(
        string='Signature',
        help='Digital signature of the recipient',
    )
    signature_filename = fields.Char(
        string='Signature Filename',
    )
    photo = fields.Binary(
        string='Delivery Photo',
        help='Photo of the delivered goods',
    )
    photo_filename = fields.Char(
        string='Photo Filename',
    )
    additional_photos = fields.Many2many(
        'ir.attachment',
        string='Additional Photos',
        help='Additional photos of the delivery',
    )
    
    # Timestamp and Location
    timestamp = fields.Datetime(
        string='Delivery Timestamp',
        required=True,
        default=fields.Datetime.now,
    )
    latitude = fields.Float(
        string='Latitude',
        digits=(10, 7),
        help='GPS latitude at time of delivery',
    )
    longitude = fields.Float(
        string='Longitude',
        digits=(10, 7),
        help='GPS longitude at time of delivery',
    )
    delivery_address = fields.Text(
        string='Delivery Address',
        help='Actual delivery address (may differ from planned)',
    )
    
    # Delivery Status
    condition = fields.Selection(
        selection=[
            ('good', 'Good Condition'),
            ('minor_damage', 'Minor Damage'),
            ('major_damage', 'Major Damage'),
            ('partial', 'Partial Delivery'),
        ],
        string='Goods Condition',
        default='good',
        required=True,
    )
    items_delivered = fields.Integer(
        string='Items Delivered',
        help='Number of items actually delivered',
    )
    items_rejected = fields.Integer(
        string='Items Rejected',
        help='Number of items rejected by recipient',
    )
    
    # Notes
    notes = fields.Text(
        string='Delivery Notes',
        help='Notes from driver about the delivery',
    )
    recipient_notes = fields.Text(
        string='Recipient Comments',
        help='Comments from the recipient',
    )
    damage_description = fields.Text(
        string='Damage Description',
        help='Description of any damage to goods',
    )
    
    # Verification
    is_verified = fields.Boolean(
        string='Verified',
        default=False,
        help='Has this POD been verified by operations',
    )
    verified_by = fields.Many2one(
        'res.users',
        string='Verified By',
    )
    verified_date = fields.Datetime(
        string='Verified Date',
    )

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'logistics.proof.of.delivery'
            ) or _('New')
        
        record = super().create(vals)
        
        # Auto-complete delivery when POD is created
        if record.delivery_id and record.delivery_id.status in ('arrived', 'in_transit'):
            record.delivery_id.action_deliver()
        
        return record

    def action_verify(self):
        """Mark POD as verified."""
        self.write({
            'is_verified': True,
            'verified_by': self.env.uid,
            'verified_date': fields.Datetime.now(),
        })

    def action_unverify(self):
        """Remove verification from POD."""
        self.write({
            'is_verified': False,
            'verified_by': False,
            'verified_date': False,
        })

    @api.onchange('delivery_id')
    def _onchange_delivery_id(self):
        """Auto-fill information from delivery."""
        if self.delivery_id:
            # Set delivery address from destination
            if self.delivery_id.destination_id:
                self.delivery_address = self.delivery_id.destination_id.complete_address
            
            # Set items count from shipment
            if self.delivery_id.shipment_id:
                self.items_delivered = self.delivery_id.shipment_id.total_items
