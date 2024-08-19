# Product Brand Module for Odoo

This custom module adds brand management functionality to Odoo's product management system.

## Installation and Setup Process

### 1. Create the module structure

Create a new directory for the module in the Odoo addons path:

```bash
mkdir -p /usr/lib/python3/dist-packages/odoo/custom/addons/product_brand
cd /usr/lib/python3/dist-packages/odoo/custom/addons/product_brand
```

### 2. Create necessary files

Create the following files in the module directory:

- `__init__.py`
- `__manifest__.py`
- `models/__init__.py`
- `models/product_brand.py`
- `views/product_brand_views.xml`
- `security/ir.model.access.csv`

### 3. Implement the module

Fill the files with the appropriate code (refer to the individual files for content).

### 4. Update Odoo configuration

Edit the Odoo configuration file:

```bash
sudo nano /etc/odoo/odoo.conf
```

Add the custom addons path to the `addons_path` option:

```
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/usr/lib/python3/dist-packages/odoo/custom/addons
```

Note: Ensure there's only one `addons_path` line to avoid duplication errors.

### 5. Set correct permissions

```bash
sudo chown -R odoo:odoo /usr/lib/python3/dist-packages/odoo/custom/addons/product_brand
sudo chmod -R 755 /usr/lib/python3/dist-packages/odoo/custom/addons/product_brand
```

### 6. Restart Odoo service

```bash
sudo systemctl restart odoo
```

### 7. Install the module

1. Log in to Odoo with administrator privileges
2. Go to Apps
3. Click on "Update Apps List"
4. Search for "Product Brand"
5. Click Install

## Usage

After installation:

1. A new menu item "Brands" will appear under Inventory > Configuration
2. Product forms will have a new field for selecting the brand
3. You can create and manage brands from the Brands menu

## Troubleshooting

If the module doesn't appear in the Apps list:
1. Ensure the module is in the correct directory
2. Check Odoo server logs for any errors: `sudo tail -f /var/log/odoo/odoo-server.log`
3. Verify the `addons_path` in the Odoo configuration file
4. Restart the Odoo service and update the Apps list again