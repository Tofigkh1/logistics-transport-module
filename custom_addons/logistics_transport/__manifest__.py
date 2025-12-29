# -*- coding: utf-8 -*-
{
    'name': 'Logistics Transport',
    'version': '17.0.1.0.0',
    'summary': 'Transport and Logistics Management Module',
    'description': """
        Logistics Transport Management Module
        =====================================
        This module provides:
        - Carrier Information Management
        - Delivery Period Tracking
        - Origin and Destination Management
        - Product Transport Details
        - Transport Mode Selection
        - Incoterm Management
        - PDF Report Generation and Printing
    """,
    'category': 'Inventory/Delivery',
    'author': 'Developer',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'product',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/transport_views.xml',
        'report/transport_report.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}

