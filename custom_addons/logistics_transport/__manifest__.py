# -*- coding: utf-8 -*-
{
    'name': 'Logistics Transport',
    'version': '17.0.1.0.0',
    'category': 'Inventory/Delivery',
    'summary': 'Freight/Cargo Transportation Management',
    'description': """
Logistics Transport Module
==========================
A comprehensive freight and cargo transportation management module for Odoo 17.0.

Features:
---------
* Shipment booking and management
* Route planning with waypoints
* Vehicle and driver management
* Delivery tracking
* Proof of delivery capture
* Integration with Sales and Invoicing

This module helps logistics companies manage their freight operations efficiently.
    """,
    'author': 'Logistics Team',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'contacts',
        'sale',
        'account',
    ],
    'data': [
        # Security
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        # Data
        'data/sequence_data.xml',
        # Views
        'views/menu_views.xml',
        'views/location_views.xml',
        'views/vehicle_views.xml',
        'views/driver_views.xml',
        'views/route_views.xml',
        'views/shipment_views.xml',
        'views/delivery_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
