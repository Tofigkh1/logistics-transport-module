# -*- coding: utf-8 -*-

from odoo import models, fields, api


class LogisticsRoute(models.Model):
    _name = 'logistics.route'
    _description = 'Logistics Route'
    _order = 'name'

    name = fields.Char(
        string='Route Name',
        required=True,
    )
    code = fields.Char(
        string='Route Code',
        copy=False,
    )
    origin_id = fields.Many2one(
        'logistics.location',
        string='Origin',
        required=True,
        help='Starting point of the route',
    )
    destination_id = fields.Many2one(
        'logistics.location',
        string='Destination',
        required=True,
        help='End point of the route',
    )
    waypoint_ids = fields.One2many(
        'logistics.route.waypoint',
        'route_id',
        string='Waypoints',
        help='Intermediate stops along the route',
    )
    
    # Distance and Time
    distance_km = fields.Float(
        string='Distance (km)',
        help='Total route distance in kilometers',
    )
    estimated_hours = fields.Float(
        string='Estimated Time (hours)',
        help='Estimated travel time in hours',
    )
    estimated_time_display = fields.Char(
        string='Estimated Time',
        compute='_compute_estimated_time_display',
    )
    
    # Route Details
    route_type = fields.Selection(
        selection=[
            ('direct', 'Direct Route'),
            ('multi_stop', 'Multi-Stop Route'),
            ('round_trip', 'Round Trip'),
        ],
        string='Route Type',
        default='direct',
    )
    description = fields.Text(
        string='Description',
        help='Additional route information and instructions',
    )
    
    # Status
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    
    # Statistics
    usage_count = fields.Integer(
        string='Times Used',
        compute='_compute_usage_count',
    )
    
    # Computed
    waypoint_count = fields.Integer(
        string='Number of Waypoints',
        compute='_compute_waypoint_count',
    )

    _sql_constraints = [
        ('code_unique', 'unique(code)',
         'Route code must be unique!'),
    ]

    @api.depends('estimated_hours')
    def _compute_estimated_time_display(self):
        for route in self:
            if route.estimated_hours:
                hours = int(route.estimated_hours)
                minutes = int((route.estimated_hours - hours) * 60)
                if hours and minutes:
                    route.estimated_time_display = f"{hours}h {minutes}m"
                elif hours:
                    route.estimated_time_display = f"{hours}h"
                else:
                    route.estimated_time_display = f"{minutes}m"
            else:
                route.estimated_time_display = ''

    @api.depends('waypoint_ids')
    def _compute_waypoint_count(self):
        for route in self:
            route.waypoint_count = len(route.waypoint_ids)

    def _compute_usage_count(self):
        Shipment = self.env['logistics.shipment']
        for route in self:
            route.usage_count = Shipment.search_count([
                ('route_id', '=', route.id),
            ])

    @api.model
    def create(self, vals):
        if not vals.get('code'):
            # Auto-generate route code
            origin = self.env['logistics.location'].browse(vals.get('origin_id'))
            destination = self.env['logistics.location'].browse(vals.get('destination_id'))
            if origin and destination:
                origin_code = (origin.city or origin.name)[:3].upper()
                dest_code = (destination.city or destination.name)[:3].upper()
                vals['code'] = f"{origin_code}-{dest_code}"
        return super().create(vals)

    def name_get(self):
        result = []
        for route in self:
            name = route.name
            if route.distance_km:
                name = f"{route.name} ({route.distance_km} km)"
            result.append((route.id, name))
        return result

    @api.onchange('origin_id', 'destination_id')
    def _onchange_locations(self):
        """Auto-generate route name from locations."""
        if self.origin_id and self.destination_id and not self.name:
            self.name = f"{self.origin_id.name} → {self.destination_id.name}"


class LogisticsRouteWaypoint(models.Model):
    _name = 'logistics.route.waypoint'
    _description = 'Route Waypoint'
    _order = 'sequence, id'

    route_id = fields.Many2one(
        'logistics.route',
        string='Route',
        required=True,
        ondelete='cascade',
    )
    location_id = fields.Many2one(
        'logistics.location',
        string='Location',
        required=True,
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    
    # Waypoint Details
    waypoint_type = fields.Selection(
        selection=[
            ('stop', 'Stop'),
            ('pickup', 'Pickup Point'),
            ('delivery', 'Delivery Point'),
            ('rest', 'Rest Stop'),
            ('fuel', 'Fuel Stop'),
            ('checkpoint', 'Checkpoint'),
        ],
        string='Waypoint Type',
        default='stop',
    )
    estimated_arrival = fields.Float(
        string='Est. Arrival (hours from start)',
        help='Estimated hours from route start to reach this waypoint',
    )
    estimated_duration = fields.Float(
        string='Stop Duration (hours)',
        help='Estimated time to spend at this waypoint',
        default=0.5,
    )
    notes = fields.Text(
        string='Notes',
    )
    
    # Related fields
    location_city = fields.Char(
        related='location_id.city',
        string='City',
    )

    def name_get(self):
        result = []
        for waypoint in self:
            name = f"{waypoint.sequence}. {waypoint.location_id.name}"
            if waypoint.waypoint_type != 'stop':
                name = f"{name} ({waypoint.waypoint_type.title()})"
            result.append((waypoint.id, name))
        return result
