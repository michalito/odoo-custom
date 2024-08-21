{
    'name': 'Product Extensions',
    'version': '17.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Manage product brands and form view',
    'description': """This module adds brand management to products and alters the form view accordingly""",
    'author': 'Michael Sinoplis',
    'depends': ['product', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_brand_views.xml',
        'views/product_template_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}