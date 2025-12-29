# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class LogisticsDelivery(models.Model):
    _name = 'logistics.delivery'
    _description = 'Delivery Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Delivery Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    shipment_id = fields.Many2one(
        'logistics.shipment',
        string='Shipment',
        required=True,
        ondelete='cascade',
        tracking=True,
    )
    
    # Related fields from shipment
    customer_id = fields.Many2one(
        related='shipment_id.customer_id',
        string='Customer',
        store=True,
    )
    vehicle_id = fields.Many2one(
        related='shipment_id.vehicle_id',
        string='Vehicle',
        store=True,
    )
    driver_id = fields.Many2one(
        related='shipment_id.driver_id',
        string='Driver',
        store=True,
    )
    origin_id = fields.Many2one(
        related='shipment_id.origin_id',
        string='Origin',
    )
    destination_id = fields.Many2one(
        related='shipment_id.destination_id',
        string='Destination',
    )
    
    # Status
    status = fields.Selection(
        selection=[
            ('pending', 'Pending'),
            ('departed', 'Departed'),
            ('in_transit', 'In Transit'),
            ('arrived', 'Arrived'),
            ('delivered', 'Delivered'),
            ('failed', 'Delivery Failed'),
        ],
        string='Status',
        default='pending',
        tracking=True,
    )
    
    # Timestamps
    departure_time = fields.Datetime(
        string='Departure Time',
        tracking=True,
    )
    arrival_time = fields.Datetime(
        string='Arrival Time',
        tracking=True,
    )
    
    # Duration
    transit_duration = fields.Float(
        string='Transit Duration (hours)',
        compute='_compute_transit_duration',
        store=True,
    )
    transit_duration_display = fields.Char(
        string='Transit Time',
        compute='_compute_transit_duration',
    )
    
    # Location Updates
    current_location = fields.Char(
        string='Current Location',
        help='Last known location of the vehicle',
    )
    current_latitude = fields.Float(
        string='Current Latitude',
        digits=(10, 7),
    )
    current_longitude = fields.Float(
        string='Current Longitude',
        digits=(10, 7),
    )
    last_update = fields.Datetime(
        string='Last Location Update',
    )
    
    # Proof of Delivery
    pod_ids = fields.One2many(
        'logistics.proof.of.delivery',
        'delivery_id',
        string='Proof of Delivery',
    )
    has_pod = fields.Boolean(
        string='Has POD',
        compute='_compute_has_pod',
    )
    
    # Delivery Details
    delivery_attempts = fields.Integer(
        string='Delivery Attempts',
        default=0,
    )
    failure_reason = fields.Text(
        string='Failure Reason',
        help='Reason for delivery failure if applicable',
    )
    
    # Notes
    notes = fields.Text(
        string='Notes',
    )
    driver_notes = fields.Text(
        string='Driver Notes',
    )

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'logistics.delivery'
            ) or _('New')
        return super().create(vals)

    @api.depends('departure_time', 'arrival_time')
    def _compute_transit_duration(self):
        for delivery in self:
            if delivery.departure_time and delivery.arrival_time:
                delta = delivery.arrival_time - delivery.departure_time
                hours = delta.total_seconds() / 3600
                delivery.transit_duration = hours
                
                # Display format
                h = int(hours)
                m = int((hours - h) * 60)
                if h and m:
                    delivery.transit_duration_display = f"{h}h {m}m"
                elif h:
                    delivery.transit_duration_display = f"{h}h"
                else:
                    delivery.transit_duration_display = f"{m}m"
            else:
                delivery.transit_duration = 0
                delivery.transit_duration_display = ''

    @api.depends('pod_ids')
    def _compute_has_pod(self):
        for delivery in self:
            delivery.has_pod = bool(delivery.pod_ids)

    def action_depart(self):
        """Mark delivery as departed from origin."""
        for delivery in self:
            delivery.write({
                'status': 'departed',
                'departure_time': fields.Datetime.now(),
            })

    def action_in_transit(self):
        """Mark delivery as in transit."""
        for delivery in self:
            delivery.write({
                'status': 'in_transit',
            })

    def action_arrive(self):
        """Mark delivery as arrived at destination."""
        for delivery in self:
            delivery.write({
                'status': 'arrived',
                'arrival_time': fields.Datetime.now(),
            })

    def action_deliver(self):
        """Mark delivery as completed."""
        for delivery in self:
            delivery.write({
                'status': 'delivered',
            })
            # Update shipment status
            if delivery.shipment_id.state == 'in_transit':
                delivery.shipment_id.action_mark_delivered()

    def action_fail(self):
        """Mark delivery as failed."""
        for delivery in self:
            delivery.write({
                'status': 'failed',
                'delivery_attempts': delivery.delivery_attempts + 1,
            })

    def action_retry(self):
        """Retry a failed delivery."""
        for delivery in self:
            delivery.write({
                'status': 'pending',
            })

    def action_update_location(self):
        """Open wizard to update current location."""
        self.ensure_one()
        return {
            'name': _('Update Location'),
            'type': 'ir.actions.act_window',
            'res_model': 'logistics.delivery',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'form_view_initial_mode': 'edit'},
        }

    def action_capture_pod(self):
        """Open POD capture form."""
        self.ensure_one()
        return {
            'name': _('Capture Proof of Delivery'),
            'type': 'ir.actions.act_window',
            'res_model': 'logistics.proof.of.delivery',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_delivery_id': self.id,
            },
        }
