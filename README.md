# Oil Distribution

A **Frappe 16** app for managing oil distribution operations — stock tracking, inter-company transfers, reservations, releases, dispatch/return management, and master data CRUD across multiple warehouses and companies.

## Features

- **PWA Frontend** (`/oil-ops`) — Ionic Vue SPA with sidebar navigation, user profile, searchable menu
- **Dashboard** — Real-time stock KPIs (Nos + Litres), stacked bar charts, donut charts with interactive tooltips
- **Command Center** — Sales/Procurement trend analysis, monthly variance, MoM change, share bars
- **Stock by Company** — Per-company stock breakdown with warehouse grouping (Available / Unreserved / Reserved)
- **Stock by Item** — Item-level stock across companies with dual UOM (Nos / Litres / Value)
- **Stock Reservations** — Reserve stock for customers with auto-validation, UOM conversion, and bulk release
- **Stock Releases** — Release reserved stock with partial fulfilment support
- **Inter-Company Transfers** — Transfer stock between Geeta Enterprise, Global Export, and Shubham Enterprise
- **Dispatch / Return** — Customer dispatch and return management with delivery note integration
- **Swastik Reserved** — Dedicated view for Swastik reserved stock tracking with detailed item/company breakdown
- **Dual UOM** — All stock views show both Nos/Pcs and Litres with conversion factor integration
- **Master Data CRUD** — Generic list/detail views for Items, Customers, Suppliers with:
  - Sortable columns, quick search, multi-field filters
  - Inline edit/view toggle, field-level save, delete with confirmation
  - Dynamic tabbed detail pages
  - Shimmer loading skeleton

## Companies

- **Geeta Enterprise (GE)**
- **Global Export (GEX)**
- **Shubham Enterprise (SHE)**

## Warehouse Naming Convention

`{Type} WH - {Company Abbr}`  
e.g. `Available WH - GE`, `Unreserved WH - GE`, `Reserved WH - GE`

## Installation

```bash
bench get-app https://github.com/Mohit-Panaliya/Geeta_Enterprise_Frappe16.git
bench --site yoursite install-app oil_distribution
bench --site yoursite migrate
bench --site yoursite import-fixtures
```

The `import-fixtures` step loads master data (Items, Customers, Suppliers, Item Groups, etc.) from the bundled fixture files.

## Development

Built on Frappe 16 with Vue.js (Ionic Vue) frontend components.

### Frontend build

```bash
cd apps/oil_distribution/frontend
npm install
npm run build
```

The PWA is served at `https://yoursite/oil-ops`.
