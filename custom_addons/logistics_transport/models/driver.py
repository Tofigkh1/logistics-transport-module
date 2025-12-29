# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date


class LogisticsDriver(models.Model):
    _name = 'logistics.driver'
    _description = 'Logistics Driver'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(
        string='Driver Name',
        required=True,
        tracking=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Related Contact',
        help='Contact record for this driver',
    )
    employee_code = fields.Char(
        string='Employee Code',
        copy=False,
    )
    phone = fields.Char(
        string='Phone',
        tracking=True,
    )
    mobile = fields.Char(
        string='Mobile',
        tracking=True,
    )
    email = fields.Char(
        string='Email',
    )
    
    # License Information
    license_number = fields.Char(
        string='License Number',
        required=True,
        tracking=True,
    )
    license_type = fields.Selection(
        selection=[
            ('a', 'Class A - Heavy Vehicles'),
            ('b', 'Class B - Medium Vehicles'),
            ('c', 'Class C - Light Vehicles'),
            ('d', 'Class D - Passenger Vehicles'),
        ],
        string='License Type',
        default='b',
        tracking=True,
    )
    license_expiry = fields.Date(
        string='License Expiry Date',
        required=True,
        tracking=True,
    )
    license_is_valid = fields.Boolean(
        string='License Valid',
        compute='_compute_license_validity',
        store=True,
    )
    
    # Status
    status = fields.Selection(
        selection=[
            ('available', 'Available'),
            ('on_trip', 'On Trip'),
            ('off_duty', 'Off Duty'),
            ('on_leave', 'On Leave'),
        ],
        string='Status',
        default='available',
        tracking=True,
    )
    is_available = fields.Boolean(
        string='Is Available',
        compute='_compute_is_available',
        store=True,
    )
    
    # Current Assignment
    current_vehicle_id = fields.Many2one(
        'logistics.vehicle',
        string='Current Vehicle',
        help='Vehicle currently assigned to this driver',
    )
    current_shipment_id = fields.Many2one(
        'logistics.shipment',
        string='Current Shipment',
        compute='_compute_current_shipment',
    )
    
    # Additional Info
    date_of_birth = fields.Date(
        string='Date of Birth',
    )
    address = fields.Text(
        string='Address',
    )
    emergency_contact = fields.Char(
        string='Emergency Contact',
    )
    emergency_phone = fields.Char(
        string='Emergency Phone',
    )
    notes = fields.Text(
        string='Notes',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    
    # Statistics
    total_trips = fields.Integer(
        string='Total Trips',
        compute='_compute_statistics',
    )
    completed_trips = fields.Integer(
        string='Completed Trips',
        compute='_compute_statistics',
    )

    # Image
    image_128 = fields.Image(
        string='Image',
        max_width=128,
        max_height=128,
    )

    _sql_constraints = [
        ('license_number_unique', 'unique(license_number)',
         'License number must be unique!'),
        ('employee_code_unique', 'unique(employee_code)',
         'Employee code must be unique!'),
    ]

    @api.depends('license_expiry')
    def _compute_license_validity(self):
        today = date.today()
        for driver in self:
            if driver.license_expiry:
                driver.license_is_valid = driver.license_expiry > today
            else:
                driver.license_is_valid = False

    @api.depends('status', 'license_is_valid')
    def _compute_is_available(self):
        for driver in self:
            driver.is_available = (
                driver.status == 'available' and
                driver.license_is_valid
            )

    def _compute_current_shipment(self):
        Shipment = self.env['logistics.shipment']
        for driver in self:
            shipment = Shipment.search([
                ('driver_id', '=', driver.id),
                ('state', 'in', ['dispatched', 'in_transit']),
            ], limit=1)
            driver.current_shipment_id = shipment.id if shipment else False

    def _compute_statistics(self):
        Shipment = self.env['logistics.shipment']
        for driver in self:
            shipments = Shipment.search([('driver_id', '=', driver.id)])
            driver.total_trips = len(shipments)
            driver.completed_trips = len(shipments.filtered(
                lambda s: s.state == 'done'
            ))

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Auto-fill contact info from partner."""
        if self.partner_id:
            self.phone = self.partner_id.phone
            self.mobile = self.partner_id.mobile
            self.email = self.partner_id.email
            if not self.name:
                self.name = self.partner_id.name

    def action_set_available(self):
        """Set driver status to available."""
        self.write({'status': 'available'})

    def action_set_off_duty(self):
        """Set driver status to off duty."""
        self.write({'status': 'off_duty'})

    def action_set_on_leave(self):
        """Set driver status to on leave."""
        self.write({'status': 'on_leave'})
