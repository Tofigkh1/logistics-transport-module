# -*- coding: utf-8 -*-

from odoo import models, fields, api


class LogisticsVehicle(models.Model):
    _name = 'logistics.vehicle'
    _description = 'Logistics Vehicle'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(
        string='Vehicle Name',
        required=True,
        tracking=True,
    )
    license_plate = fields.Char(
        string='License Plate',
        required=True,
        tracking=True,
    )
    vehicle_type = fields.Selection(
        selection=[
            ('truck', 'Truck'),
            ('van', 'Van'),
            ('trailer', 'Trailer'),
            ('container', 'Container Truck'),
            ('pickup', 'Pickup Truck'),
            ('tanker', 'Tanker'),
            ('refrigerated', 'Refrigerated Truck'),
        ],
        string='Vehicle Type',
        default='truck',
        required=True,
        tracking=True,
    )
    
    # Capacity
    capacity_weight = fields.Float(
        string='Weight Capacity (kg)',
        help='Maximum weight capacity in kilograms',
        tracking=True,
    )
    capacity_volume = fields.Float(
        string='Volume Capacity (m³)',
        help='Maximum volume capacity in cubic meters',
        tracking=True,
    )
    
    # Status
    status = fields.Selection(
        selection=[
            ('available', 'Available'),
            ('in_use', 'In Use'),
            ('maintenance', 'Under Maintenance'),
            ('out_of_service', 'Out of Service'),
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
    
    # Driver Assignment
    driver_id = fields.Many2one(
        'logistics.driver',
        string='Default Driver',
        help='Default driver assigned to this vehicle',
        tracking=True,
    )
    current_driver_id = fields.Many2one(
        'logistics.driver',
        string='Current Driver',
        help='Driver currently operating this vehicle',
    )
    
    # Current Assignment
    current_shipment_id = fields.Many2one(
        'logistics.shipment',
        string='Current Shipment',
        compute='_compute_current_shipment',
    )
    
    # Vehicle Details
    brand = fields.Char(
        string='Brand/Make',
    )
    model = fields.Char(
        string='Model',
    )
    year = fields.Char(
        string='Year',
    )
    color = fields.Char(
        string='Color',
    )
    vin = fields.Char(
        string='VIN',
        help='Vehicle Identification Number',
    )
    
    # Registration & Insurance
    registration_date = fields.Date(
        string='Registration Date',
    )
    registration_expiry = fields.Date(
        string='Registration Expiry',
        tracking=True,
    )
    insurance_policy = fields.Char(
        string='Insurance Policy Number',
    )
    insurance_expiry = fields.Date(
        string='Insurance Expiry',
        tracking=True,
    )
    
    # Maintenance
    last_maintenance_date = fields.Date(
        string='Last Maintenance Date',
    )
    next_maintenance_date = fields.Date(
        string='Next Maintenance Date',
    )
    odometer = fields.Float(
        string='Odometer (km)',
        help='Current odometer reading in kilometers',
    )
    
    # Fuel
    fuel_type = fields.Selection(
        selection=[
            ('diesel', 'Diesel'),
            ('petrol', 'Petrol'),
            ('electric', 'Electric'),
            ('hybrid', 'Hybrid'),
            ('lpg', 'LPG'),
        ],
        string='Fuel Type',
        default='diesel',
    )
    fuel_capacity = fields.Float(
        string='Fuel Tank Capacity (L)',
        help='Fuel tank capacity in liters',
    )
    fuel_efficiency = fields.Float(
        string='Fuel Efficiency (km/L)',
        help='Average kilometers per liter',
    )
    
    # Additional
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
    total_distance = fields.Float(
        string='Total Distance (km)',
        compute='_compute_statistics',
    )
    
    # Image
    image_128 = fields.Image(
        string='Image',
        max_width=128,
        max_height=128,
    )

    _sql_constraints = [
        ('license_plate_unique', 'unique(license_plate)',
         'License plate must be unique!'),
        ('vin_unique', 'unique(vin)',
         'VIN must be unique!'),
    ]

    @api.depends('status')
    def _compute_is_available(self):
        for vehicle in self:
            vehicle.is_available = vehicle.status == 'available'

    def _compute_current_shipment(self):
        Shipment = self.env['logistics.shipment']
        for vehicle in self:
            shipment = Shipment.search([
                ('vehicle_id', '=', vehicle.id),
                ('state', 'in', ['dispatched', 'in_transit']),
            ], limit=1)
            vehicle.current_shipment_id = shipment.id if shipment else False

    def _compute_statistics(self):
        Shipment = self.env['logistics.shipment']
        for vehicle in self:
            shipments = Shipment.search([
                ('vehicle_id', '=', vehicle.id),
                ('state', '=', 'done'),
            ])
            vehicle.total_trips = len(shipments)
            # Calculate total distance from routes
            total_distance = sum(
                shipment.route_id.distance_km
                for shipment in shipments
                if shipment.route_id
            )
            vehicle.total_distance = total_distance

    @api.onchange('driver_id')
    def _onchange_driver_id(self):
        """Update current driver when default driver changes."""
        if self.driver_id and not self.current_driver_id:
            self.current_driver_id = self.driver_id

    def action_set_available(self):
        """Set vehicle status to available."""
        self.write({'status': 'available'})

    def action_set_maintenance(self):
        """Set vehicle status to maintenance."""
        self.write({'status': 'maintenance'})

    def action_set_out_of_service(self):
        """Set vehicle status to out of service."""
        self.write({'status': 'out_of_service'})

    def name_get(self):
        result = []
        for vehicle in self:
            name = f"{vehicle.name} ({vehicle.license_plate})"
            result.append((vehicle.id, name))
        return result
