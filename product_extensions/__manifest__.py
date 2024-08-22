{
    'name': 'Product Extensions',
    'version': '1.0.1',
    'license': 'LGPL-3',
    'category': 'Inventory',
    'summary': 'Adding more functionality to the inventory App',
    'description': """This module adds brand and vendor management to products and alters the form view accordingly""",
    'author': 'Michael Sinoplis',
    'depends': ['product', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_brand_views.xml',
        'views/product_template_views.xml',
        'views/product_supplier_views.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}