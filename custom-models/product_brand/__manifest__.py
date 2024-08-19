{
    'name': 'Product Brand',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Manage product brands',
    'description': """This module adds brand management to products.""",
    'author': 'Michael Sinoplis',
    'depends': ['product'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_brand_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}