{
    'name': 'Barcode Scanner',
    'version': '1.0',
    'license': 'LGPL-3',
    'category': 'Inventory',
    'summary': 'Custom module for barcode scanning',
    'description': "",
    'author': 'Michael Sinoplis',
    'depends': ['product', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/barcode_scanner_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}