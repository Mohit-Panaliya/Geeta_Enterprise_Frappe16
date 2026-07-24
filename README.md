# Oil Distribution

A **Frappe 16** app for managing oil distribution operations — stock tracking, inter-company transfers, reservations, releases, and dispatch/return management across multiple warehouses and companies.

## Features

- **Dashboard** — Real-time stock KPIs (Nos + Litres), stacked bar charts, donut charts with interactive tooltips
- **Command Center** — Sales/Procurement trend analysis, monthly variance, MoM change, share bars
- **Stock by Company** — Per-company stock breakdown with warehouse grouping (Available / Unreserved / Reserved)
- **Stock by Item** — Item-level stock across companies with dual UOM (Nos / Litres / Value)
- **Stock Reservations** — Reserve stock for customers with auto-validation and UOM conversion
- **Stock Releases** — Release reserved stock with partial fulfilment support
- **Inter-Company Transfers** — Transfer stock between Geeta Enterprise, Global Export, and Shubham Enterprise
- **Dispatch / Return** — Customer dispatch and return management with delivery note integration
- **Swastik Reserved** — Dedicated view for Swastik reserved stock tracking with detailed item/company breakdown
- **Dual UOM** — All stock views show both Nos/Pcs and Litres with conversion factor integration

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
```

## Development

Built on Frappe 16 with Vue.js frontend components.
