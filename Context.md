# Oil Distribution App - Context & Reference

## Project Overview
Custom Frappe 16 + ERPNext 16 PWA (Ionic Vue 8 + frappe-ui) for engine oil distribution with intercompany transfers, stock reservations, reports, and India compliance across 3 companies.

---

## Environment
- **Frappe Framework**: v16.26.3
- **ERPNext**: v16.27.0
- **HRMS**: v16.12.2
- **India Compliance**: v16.7.0
- **Site**: `dev.localhost`
- **Ports**: socketio_port = 0, webserver_port = 8000
- **Procfile**: socketio commented out (Codespaces compatible)

---

## Companies
| Company | Abbr | Default Currency | Country |
|---------|------|------------------|---------|
| Geeta Enterprise | GE | INR | India |
| Global Export | GEX | INR | India |
| Shubham Enterprise | SHE | INR | India |

---

## Items (Engine Oils Only)
| Item Code | Description |
|-----------|-------------|
| ENGINE-10W30 | Engine Oil 10W30 |
| ENGINE-15W40 | Engine Oil 15W40 |
| ENGINE-20W50 | Engine Oil 20W50 |
| ENGINE-5W30 | Engine Oil 5W30 |

---

## Warehouses (Per Company)
Each company has 7 warehouses:
- `Available WH - {abbr}` (Main warehouse for available stock)
- `Reserved WH - {abbr}` (Main warehouse for reserved stock)
- `Stores - {abbr}`
- `Raw Material Warehouse - {abbr}`
- `Finished Goods - {abbr}`
- `Transit Warehouse - {abbr}`
- `Work In Progress Warehouse - {abbr}`

Plus standard ERPNext warehouses for each company.

---

## Single Module
The entire app is consolidated into one Frappe module: **Oil Distribution** (`oil_distribution/modules.txt`).

All DocTypes, Pages, Reports, Number Cards, Dashboard Charts, and Workspace definitions live under the single module path:
```
oil_distribution/oil_distribution/oil_distribution/
```

There are NO separate `intercompany_operations/`, `reservation_management/`, or `dashboard_reports/` module directories.

---

## Custom DocTypes

### Inter Company Transfer (ICT)
- **Module**: Oil Distribution
- **Status**: Submittable
- **Naming**: ICT.##### (auto-increment)
- **Features**:
  - Multi-item child table (Inter Company Transfer Item)
  - Generated Documents tracking (Dynamic Link)
  - Auto SO -> PO -> DN -> PR chain via ERPNext native APIs
  - Fields: batch_no, sales_tax_template, purchase_tax_template
  - Source warehouse filtered by source company
  - Target warehouse filtered by target company
  - Amount auto-calculated from item rates

### Stock Reservation
- **Module**: Oil Distribution
- **Status**: Submittable
- **Naming**: SR.##### (auto-increment)
- **Features**:
  - Material Transfer on submit/release
  - Reserved warehouse via naming convention: `Reserved WH - {company_abbr}`
  - `total_reserved_for_swastik` field (read-only): Shows grand total of ALL reserved quantities across ALL companies for ALL items
  - Warehouse filtering by company (warehouse + reserved_warehouse)
  - `reserved_for` options: Swastik, Sales Order, Purchase Order, Work Order, Internal, Other
  - Negative stock warning (orange, non-blocking)

### Transfer Settings
- **Module**: Oil Distribution
- **Type**: Singleton
- **Fields**: notification_email, auto_create_intercompany_docs, inter_company_auto_mode, inter_company_default_series

---

## Custom Roles
- Intercompany Manager
- Reservation Manager
- Stock Reservation User

---

## Reports
All reports are `is_standard=No` with JS stored in DB `javascript` column. All live under `oil_distribution/oil_distribution/oil_distribution/report/`.

| Report | Directory | Description |
|--------|-----------|-------------|
| IOCL Procurement Report | `iocl_procurement_report/` | Procurement analysis |
| Negative Stock Report | `negative_stock_report/` | Items with negative stock |
| Available Vs Reserved | `available_vs_reserved/` | Stock comparison |
| Intercompany Transfer Report | `intercompany_transfer_report/` | Transfer summary |
| Company Wise Stock | `company_wise_stock/` | Stock by company & warehouse |
| Reserved Stock | `reserved_stock/` | Reservation details |

---

## Pages (Frappe Desk)

### Oil Command Center
- **Route**: `/oil-command-center`
- **Location**: `oil_distribution/oil_distribution/oil_distribution/page/oil_command_center/`
- **Files**: `oil_command_center.py`, `oil_command_center.js`, `oil_command_center.json`
- **Plan**: See `oil_distribution/oil_distribution/oil_distribution/page/oil_command_center/plan.md`

### Stock Dashboard
- **Route**: `/stock-dashboard`
- **Location**: `oil_distribution/oil_distribution/oil_distribution/page/stock_dashboard/`
- **Files**: `stock_dashboard.py`, `stock_dashboard.js`, `stock_dashboard.json`
- **Plan**: See `oil_distribution/oil_distribution/oil_distribution/page/stock_dashboard/plan.md`

---

## PWA (Progressive Web App)
- **Route**: `/oil-ops`
- **Location**: `oil_distribution/www/oil-ops.html` + `oil_distribution/www/oil_ops.py`
- **Frontend**: Ionic Vue 8 + frappe-ui + Tailwind CSS + Vite
- **Source**: `oil_distribution/frontend/src/`
- **Built assets**: `oil_distribution/public/frontend/`

### PWA Views (Frontend Routes)
| Route | View | Description |
|-------|------|-------------|
| `/dashboards` | Dashboards.vue | Operations dashboard with module cards + master data links |
| `/command-center` | CommandCenter.vue | Sales/Procurement/Stock/ICT/Reservations |
| `/stock` | StockDashboard.vue | Stock intelligence with donut/bar charts, warehouse tables |
| `/procurement` | Procurement.vue | Purchase orders list |
| `/sales` | Sales.vue | Sales orders list |
| `/ict` | ICT.vue (List/Form/Dashboard) | Inter-company transfer management |
| `/reservations` | Reservations.vue | Stock reservation list + create form |
| `/customers` | Customers.vue | Customer master data list |
| `/suppliers` | Suppliers.vue | Supplier master data list |
| `/items` | Items.vue | Item master data list |

### PWA API Layer
Backend APIs for the PWA are in `oil_distribution/api/oil_ops.py` (whitelisted endpoints).

---

## App Structure
```
oil_distribution/                          # Root app package
├── hooks.py                               # Root hooks (Frappe reads this)
├── modules.txt                            # Single module: "Oil Distribution"
├── patches.txt                            # Post-model-sync patch
├── setup.py                               # Package metadata
├── info.json                              # App metadata
├── Context.md                             # This file
├── frontend/                              # Ionic Vue 8 PWA source
│   ├── src/
│   │   ├── App.vue
│   │   ├── router/index.js
│   │   ├── api/ (common.js, ict.js, reservations.js)
│   │   ├── components/ (KPICard.vue)
│   │   └── views/ (Dashboards, CommandCenter, StockDashboard, etc.)
│   ├── package.json
│   └── vite.config.js
└── oil_distribution/                      # Inner Python package
    ├── __init__.py                        # __version__ = "0.0.1"
    ├── hooks.py                           # Inner hooks (has website_route_rules, more fixtures)
    ├── modules.txt                        # "Oil Distribution"
    ├── patches.txt                        # v1_init_setup
    ├── setup_overall_dashboard.py
    ├── setup_test_data.py
    ├── tasks.py
    ├── api/
    │   ├── oil_ops.py                     # Whitelisted PWA APIs
    │   ├── reports.py                     # Scheduled email reports
    │   ├── setup_icons.py
    │   ├── setup_master_data.py
    │   ├── stock_events.py                # Stock Entry handlers (stubs)
    │   ├── test_full.py                   # 20-test E2E suite
    │   ├── test_production.py             # 31-test production suite
    │   └── test_bulk.py                   # 51-test bulk suite
    ├── oil_distribution/                  # Deepest module package
    │   ├── module_def.json
    │   ├── doctype/
    │   │   ├── inter_company_transfer/
    │   │   ├── inter_company_transfer_item/
    │   │   ├── inter_company_transfer_generated_document/
    │   │   ├── stock_reservation/
    │   │   └── transfer_settings/
    │   ├── report/
    │   │   ├── available_vs_reserved/
    │   │   ├── company_wise_stock/
    │   │   ├── intercompany_transfer_report/
    │   │   ├── iocl_procurement_report/
    │   │   ├── negative_stock_report/
    │   │   └── reserved_stock/
    │   ├── page/
    │   │   ├── oil_command_center/
    │   │   └── stock_dashboard/
    │   ├── number_card/
    │   │   ├── swastik_reserved_qty/
    │   │   ├── total_available_qty/
    │   │   ├── total_procurement_value/
    │   │   └── total_sales_value/
    │   ├── dashboard_chart/
    │   │   ├── company_wise_sales_distribution/
    │   │   ├── negative_stock_alerts/
    │   │   ├── sales_vs_procurement_trend/
    │   │   └── top_customers_by_sales/
    │   ├── workspace/
    │   │   └── oil_distribution/
    │   └── workspace_sidebar/
    │       └── __init__.py
    ├── desktop_icon/
    │   └── oil_distribution.json
    ├── workspace_sidebar/
    │   └── oil_distribution.json
    ├── patches/
    │   └── v1_init_setup/
    ├── public/
    │   ├── frontend/ (built Vue assets)
    │   └── images/
    └── www/
        ├── oil-ops.html
        └── oil_ops.py
```

---

## hooks.py (Two Files)

**IMPORTANT**: There are two `hooks.py` files. Frappe uses the **inner** one (`oil_distribution/oil_distribution/hooks.py`).

| Property | Root hooks.py | Inner hooks.py (ACTIVE) |
|----------|---------------|------------------------|
| `app_home` | `/app/oil-operations` | `/oil-ops` |
| `website_route_rules` | Not present | Present (routes `/oil-ops`) |
| `fixtures` | Roles only | Roles + Workspace Sidebar |
| `doc_events` | Stock Entry only | Stock Entry + Stock Reservation |
| `scheduler_events` | Same | Same |

The root hooks.py is effectively dead code. Always edit the inner hooks.py.

---

## Key Technical Decisions

### Frappe 16 Specifics
1. **Page name**: Must be hyphenated (`stock-dashboard`) matching URL convention
2. **Page JS**: `script` field in Page JSON must be `null` — Frappe loads JS from filesystem via `load_assets()`
3. **Report JS**: For `is_standard=No` reports, reads from DB `javascript` column; for `is_standard=Yes`, reads from filesystem
4. **Page JS registration**: `frappe.pages['stock-dashboard']` (hyphenated key)
5. **Frappe 16 defaults**: Use `frappe.defaults.get_default("key")` not `frappe.defaults.get_defaults()`
6. **Socket.io in Codespaces**: Set `socketio_port: 0` to avoid CORS issues

### ERPNext Intercompany APIs
- `make_inter_company_transaction` from `erpnext.selling.doctype.sales_order.sales_order`
- `make_delivery_note` from `erpnext.selling.doctype.sales_order.sales_order`
- `make_inter_company_purchase_receipt` from `erpnext.stock.doctype.delivery_note.delivery_note`

### Controller Logic
- **ICT**: SO must be submitted before `make_delivery_note()`, PO items need `warehouse` set, `purpose` must be set explicitly alongside `stock_entry_type`
- **Stock Reservation**: `validate_warehouse()` in Stock Entry runs BEFORE `set_purpose_for_stock_entry()`, SE `purpose` must be set explicitly

### Design Principles
- Never modify ERPNext core files
- Controller-based logic (not separate API files)
- ERPNext native intercompany APIs for proper linking
- Negative stock: orange warning (non-blocking)
- Warehouse naming convention for reserved warehouses
- Generated Document child table uses Dynamic Link
- `db_set()` not `self.save()` for status updates on submitted docs
- Inter-company Customers/Suppliers need `companies` child table entries
- HSN codes must be 6+ digits for India Compliance

### Stock Tracking
- **Swastik is NOT a company** — it's a tracking concept
- `total_reserved_for_swastik` field shows grand total across ALL companies
- `get_swastik_total_reserved()` sums ALL submitted Stock Reservations (status=Reserved) across all companies/items

---

## Site Config
```json
{
  "installed_apps": ["frappe", "erpnext", "hrms", "india_compliance", "oil_distribution"]
}
```

---

## Useful Commands
```bash
# Build assets
bench build --app oil_distribution

# Force import sidebar
bench --site dev.localhost execute "frappe.client.import_file_by_path('/workspace/frappe-bench/apps/oil_distribution/oil_distribution/workspace_sidebar/oil_distribution.json', force=True)"

# Run report test
bench --site dev.localhost execute "frappe.get_all('Report', filters={'module': 'Oil Distribution'}, fields=['name', 'is_standard', 'report_type'])"

# Check stock
bench --site dev.localhost execute "frappe.get_all('Stock Ledger Entry', fields=['item_code', 'warehouse', 'actual_qty'], limit=10)"

# Check companies
bench --site dev.localhost execute "frappe.get_all('Company', fields=['name', 'abbr'])"
```

---

## Known Issues
1. **Dual hooks.py**: Root hooks.py is dead code; always edit the inner one at `oil_distribution/oil_distribution/hooks.py`
2. **Test file imports broken**: All 3 test files reference `oil_distribution.dashboard_reports.report.*` but should reference `oil_distribution.oil_distribution.report.*`
3. **Number card wrong field**: `swastik_reserved_qty` references `"quantity"` but Stock Reservation doctype field is `"reserved_qty"`
4. **PWA field mismatches**: Frontend views (Procurement, Sales, ICT) read wrong field names from API responses
5. **Hardcoded asset hashes**: `oil-ops.html` has hardcoded JS/CSS hashes that break after rebuild
6. **Package name typo**: `frontend/package.json` says `geo-perations` (missing "p")
7. **Metadata mismatch**: `setup.py` and `info.json` say `admin@example.com` but hooks.py says `dev@geeta.in`

---

## GitHub
- **Repo**: https://github.com/ai-user074/oil-distribution
- **Branch**: `v1`
- **Publisher**: Geeta Enterprise

---

## Future Enhancements (Not Implemented)
- User Permissions configuration (pending user hires)
- Batch-wise stock reservation flow testing
- Re-adding warehouse-company dependency in report filters
- Scheduled stock sync
- Dashboard email reports (infrastructure created)
- Barcode printing for items
