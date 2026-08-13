# GEOperations - Frappe 16 PWA

## Overview
GEOperations is a PWA built with Ionic Vue 8 + frappe-ui on Frappe 16/ERPNext for oil distribution operations management. It provides real-time dashboards, stock intelligence, inter-company transfers, and stock reservation management.

## Tech Stack
- **Frontend**: Ionic Vue 8, frappe-ui, Tailwind CSS, Vite
- **Backend**: Frappe 16, ERPNext, Python
- **PWA**: Service worker, offline-capable, mobile-first

## App Structure
Located at `apps/oil_distribution/frontend/src/`

### Views (Pages)
| Route | View | Description |
|-------|------|-------------|
| `/dashboards` | Dashboards.vue | Operations dashboard with module cards + master data links |
| `/command-center` | CommandCenter.vue | Sales/Procurement/Stock/ICT/Reservations - exact original Frappe page designs |
| `/stock` | StockDashboard.vue | Stock intelligence with donut/bar charts, warehouse tables |
| `/procurement` | Procurement.vue | Purchase orders list |
| `/sales` | Sales.vue | Sales orders list |
| `/ict` | ICT.vue (List/Form/Dashboard) | Inter-company transfer management |
| `/reservations` | Reservations.vue | Stock reservation list + create form |
| `/customers` | Customers.vue | Customer master data list |
| `/suppliers` | Suppliers.vue | Supplier master data list |
| `/items` | Items.vue | Item master data list |

### API Layer (`oil_distribution/api/oil_ops.py`)
Key endpoints:
- `get_command_center_kpis` - Main KPI data (sales, procurement, stock, ICT, P&L with variance)
- `get_stock_kpis` - Stock intelligence KPIs
- `get_stock_by_company` / `get_stock_by_warehouse` - Stock breakdowns
- `get_negative_stock` - Negative stock alerts
- `get_ict_kpis` / `get_ict_routes` / `get_ict_list` - ICT operations
- `get_reservation_kpis` / `get_reserved_by_company` / `get_active_reservations` - Reservations
- `get_customers` / `get_suppliers` / `get_items` - Master data
- `create_stock_reservation` - Create new reservation

## Design Pattern
- Command Center and Stock Dashboard use exact copy-paste original Frappe HTML/CSS (.oz-*, .sd-* classes, SVG donuts/bar charts, period selectors, multi-select dropdowns)
- Reservations, Customers, Suppliers, Items use compact ERP-style (Vue reactive, table layout, search bars, sortable columns)

## Key Features
- Period-based data views (MTD/QTD/YTD) with comparison
- Multi-company filtering
- Real-time KPI animations (oz_count)
- SVG bar charts (stacked sales vs procurement)
- SVG donut charts (stock distribution)
- Sparklines for trends
- Stock pipeline funnel visualization

## Database
- Frappe 16 with MariaDB
- Custom doctypes: Inter Company Transfer, Stock Reservation, Transfer Settings
- Site: dev.localhost (Codespace /oil-ops URL)

## Branch History
- `14_july` - Master data pages, stock/CC fixes, variance API (current)
- `13_July` - Redesign Stock Reservations, remove CC/Stock pages
- `main` - Original setup
- `v1` - Initial version
