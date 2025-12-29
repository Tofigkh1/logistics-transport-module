# -*- coding: utf-8 -*-

from odoo import models, fields, api


class LogisticsLocation(models.Model):
    _name = 'logistics.location'
    _description = 'Logistics Location'
    _order = 'name'

    name = fields.Char(
        string='Location Name',
        required=True,
        index=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Related Partner',
        help='Partner associated with this location (customer, supplier, etc.)',
    )
    location_type = fields.Selection(
        selection=[
            ('warehouse', 'Warehouse'),
            ('customer', 'Customer Location'),
            ('supplier', 'Supplier Location'),
            ('port', 'Port/Terminal'),
            ('hub', 'Distribution Hub'),
            ('other', 'Other'),
        ],
        string='Location Type',
        default='customer',
        required=True,
    )
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street 2')
    city = fields.Char(string='City')
    state_id = fields.Many2one(
        'res.country.state',
        string='State/Province',
    )
    country_id = fields.Many2one(
        'res.country',
        string='Country',
    )
    zip = fields.Char(string='ZIP/Postal Code')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    latitude = fields.Float(
        string='Latitude',
        digits=(10, 7),
        help='GPS Latitude coordinate',
    )
    longitude = fields.Float(
        string='Longitude',
        digits=(10, 7),
        help='GPS Longitude coordinate',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    notes = fields.Text(string='Notes')
    
    # Computed fields
    complete_address = fields.Char(
        string='Complete Address',
        compute='_compute_complete_address',
        store=True,
    )

    @api.depends('street', 'street2', 'city', 'state_id', 'country_id', 'zip')
    def _compute_complete_address(self):
        for location in self:
            address_parts = []
            if location.street:
                address_parts.append(location.street)
            if location.street2:
                address_parts.append(location.street2)
            if location.city:
                address_parts.append(location.city)
            if location.state_id:
                address_parts.append(location.state_id.name)
            if location.country_id:
                address_parts.append(location.country_id.name)
            if location.zip:
                address_parts.append(location.zip)
            location.complete_address = ', '.join(address_parts) if address_parts else ''

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Auto-fill address from partner if selected."""
        if self.partner_id:
            self.street = self.partner_id.street
            self.street2 = self.partner_id.street2
            self.city = self.partner_id.city
            self.state_id = self.partner_id.state_id
            self.country_id = self.partner_id.country_id
            self.zip = self.partner_id.zip
            self.phone = self.partner_id.phone
            self.email = self.partner_id.email

    def name_get(self):
        result = []
        for location in self:
            name = location.name
            if location.city:
                name = f"{location.name} ({location.city})"
            result.append((location.id, name))
        return result
