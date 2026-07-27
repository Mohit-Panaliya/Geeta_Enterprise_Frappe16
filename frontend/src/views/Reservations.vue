<template>
  <ion-page>
    <ion-header class="ion-no-border">
      <ion-toolbar>
        <ion-buttons slot="start"><ion-menu-button /></ion-buttons>
        <ion-title>Stock Reservations</ion-title>
        <ion-buttons slot="end">
          <ion-button @click="view = 'list'; selectedRecord = null; resetForm()" v-if="view !== 'list'">
            <span style="font-family:'Montserrat',sans-serif;font-size:11px;font-weight:600;color:#64748b;display:flex;align-items:center;gap:4px;">
              <ion-icon :icon="arrowBackOutline" />Back
            </span>
          </ion-button>
          <ion-button @click="view = 'new'" v-else>
            <span style="font-family:'Montserrat',sans-serif;font-size:11px;font-weight:700;color:#fff;background:#3b82f6;padding:5px 12px;border-radius:8px;display:flex;align-items:center;gap:4px;">
              <ion-icon :icon="addOutline" />New
            </span>
          </ion-button>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>

    <!-- ═══ LIST VIEW ═══ -->
    <ion-content v-if="view === 'list'">
      <div style="padding:12px 16px;">
        <!-- Filters Bar -->
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;flex-wrap:wrap;">
          <!-- Company Multi-Select -->
          <div style="display:flex;align-items:center;gap:6px;">
            <label style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#64748b;">Company</label>
            <div ref="companyMsContainer" style="position:relative;display:inline-block;">
              <div ref="companyMsBtn" class="rv-ms-btn" :class="{ 'rv-ms-open': companyMsOpen }" @click.stop="toggleCompanyMs" v-html="companyBtnLabel"></div>
              <Teleport to="body">
                <div v-if="companyMsOpen" class="rv-ms-backdrop" @click="companyMsOpen = false"></div>
                <div ref="companyMsPanel" class="rv-ms-panel" :class="{ 'rv-ms-show': companyMsOpen }" :style="companyPanelStyle">
                  <input class="rv-ms-search" type="text" placeholder="Search..." v-model="companySearch">
                  <div class="rv-ms-actions">
                    <button class="rv-ms-action" @click.prevent.stop="selectAllCompany">Select All</button>
                    <button class="rv-ms-action" @click.prevent.stop="clearCompany">Clear</button>
                  </div>
                  <label v-for="opt in filteredCompanyOptions" :key="opt.value" class="rv-ms-opt">
                    <input type="checkbox" :value="opt.value" v-model="companySelected" :disabled="companySelected.length === 1 && companySelected[0] === opt.value" @change="onCompanyChange">
                    <span class="rv-ms-opt-label" :style="companySelected.length === 1 && companySelected[0] === opt.value ? { opacity: 0.5 } : {}">{{ opt.label }}</span>
                    <span class="rv-ms-opt-abbr">{{ opt.abbr }}</span>
                  </label>
                </div>
              </Teleport>
            </div>
          </div>

          <!-- Item Multi-Select -->
          <div style="display:flex;align-items:center;gap:6px;">
            <label style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#64748b;">Item</label>
            <div ref="itemMsContainer" style="position:relative;display:inline-block;">
              <div ref="itemMsBtn" class="rv-ms-btn" :class="{ 'rv-ms-open': itemMsOpen }" @click.stop="toggleItemMs" v-html="itemBtnLabel"></div>
              <Teleport to="body">
                <div v-if="itemMsOpen" class="rv-ms-backdrop" @click="itemMsOpen = false"></div>
                <div ref="itemMsPanel" class="rv-ms-panel" :class="{ 'rv-ms-show': itemMsOpen }" :style="itemPanelStyle">
                  <input class="rv-ms-search" type="text" placeholder="Search..." v-model="itemSearch">
                  <div class="rv-ms-actions">
                    <button class="rv-ms-action" @click.prevent.stop="selectAllItem">Select All</button>
                    <button class="rv-ms-action" @click.prevent.stop="clearItemFilter">Clear</button>
                  </div>
                  <label v-for="opt in filteredItemOptions" :key="opt.value" class="rv-ms-opt">
                    <input type="checkbox" :value="opt.value" v-model="itemSelected" :disabled="itemSelected.length === 1 && itemSelected[0] === opt.value" @change="onItemChange">
                    <span class="rv-ms-opt-label" :style="itemSelected.length === 1 && itemSelected[0] === opt.value ? { opacity: 0.5 } : {}">{{ opt.label }}</span>
                  </label>
                  <div v-if="!itemOptions.length" style="text-align:center;padding:10px;color:#64748b;font-size:10px;">Loading items...</div>
                </div>
              </Teleport>
            </div>
          </div>

          <div style="margin-left:auto;display:flex;align-items:center;gap:8px;">
            <span v-if="selectedNames.size" style="font-size:9px;font-weight:700;color:#3b82f6;">{{ selectedNames.size }} selected</span>
            <button v-if="selectedNames.size" @click="releaseSelected" :disabled="bulkReleasing"
              style="padding:4px 10px;border-radius:6px;border:none;background:#10b981;color:#fff;font-family:'Montserrat',sans-serif;font-size:10px;font-weight:700;cursor:pointer;display:flex;align-items:center;gap:4px;">
              <span v-if="bulkReleasing">...</span>
              <span v-else>Release {{ selectedNames.size }}</span>
            </button>
            <button v-if="selectedNames.size" @click="unreserveSelected" :disabled="bulkUnreserving"
              style="padding:4px 10px;border-radius:6px;border:none;background:#f59e0b;color:#fff;font-family:'Montserrat',sans-serif;font-size:10px;font-weight:700;cursor:pointer;display:flex;align-items:center;gap:4px;">
              <span v-if="bulkUnreserving">...</span>
              <span v-else>Unreserve {{ selectedNames.size }}</span>
            </button>
            <span style="font-size:9px;font-weight:700;color:#64748b;">{{ items.length }} reservations</span>
          </div>
        </div>

        <!-- KPIs -->
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:12px;">
          <div v-for="s in stats" :key="s.label" style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:10px 12px;">
            <div style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#64748b;">{{ s.label }}</div>
            <div style="font-size:18px;font-weight:800;color:#0f172a;margin-top:2px;">{{ s.value }}</div>
          </div>
        </div>

        <!-- Table -->
        <div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;overflow:hidden;" v-if="items.length">
          <table style="width:100%;border-collapse:collapse;font-size:11px;font-family:'Montserrat',sans-serif;">
            <thead>
              <tr style="background:#f8fafc;">
                <th style="width:30px;padding:8px 6px;">
                  <input type="checkbox" :checked="selectedNames.size === items.length && items.length > 0"
                    @change="e => { selectedNames = e.target.checked ? new Set(items.map(i => i.name)) : new Set() }"
                    style="accent-color:#3b82f6;width:14px;height:14px;cursor:pointer;" />
                </th>
                <th style="text-align:left;padding:8px 10px;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#64748b;">ID</th>
                <th style="text-align:left;padding:8px 10px;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#64748b;">Company</th>
                <th style="text-align:left;padding:8px 10px;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#64748b;">Item</th>
                <th style="text-align:right;padding:8px 10px;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#64748b;">Qty</th>
                <th style="text-align:left;padding:8px 10px;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#64748b;">For</th>
                <th style="text-align:left;padding:8px 10px;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#64748b;">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in items" :key="item.name"
                style="border-top:1px solid #f1f5f9;cursor:pointer;transition:background 0.15s;"
                @mouseenter="$event.currentTarget.style.background='#f8fafc'"
                @mouseleave="$event.currentTarget.style.background=''">
                <td style="width:30px;padding:8px 6px;text-align:center;" @click.stop>
                  <input type="checkbox" :checked="selectedNames.has(item.name)" @change="toggleRow(item.name)"
                    style="accent-color:#3b82f6;width:14px;height:14px;cursor:pointer;" />
                </td>
                <td style="padding:8px 10px;font-weight:700;color:#3b82f6;" @click="openDetail(item)">{{ item.name }}</td>
                <td style="padding:8px 10px;color:#334155;" @click="openDetail(item)">{{ item.company }}</td>
                <td style="padding:8px 10px;color:#475569;" @click="openDetail(item)">{{ item.item }}</td>
                <td style="padding:8px 10px;text-align:right;font-weight:800;color:#0f172a;" @click="openDetail(item)">{{ item.reserved_qty }}</td>
                <td style="padding:8px 10px;color:#475569;" @click="openDetail(item)">{{ item.reserved_for || '—' }}</td>
                <td style="padding:8px 10px;" @click="openDetail(item)">
                  <span :style="statusStyle(item.status)">{{ item.status }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:40px;text-align:center;color:#64748b;font-size:12px;font-family:'Montserrat',sans-serif;">
          No reservations found
        </div>
      </div>
    </ion-content>

    <!-- ═══ DETAIL VIEW ═══ -->
    <ion-content v-if="view === 'detail' && selectedRecord">
      <div style="padding:12px 16px;">

        <!-- Header card -->
        <div style="background:linear-gradient(135deg,#3b82f6,#7c3aed);border-radius:14px;padding:20px;color:#fff;margin-bottom:14px;">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;">
            <div>
              <div style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:1px;opacity:0.7;">Reservation</div>
              <div style="font-size:20px;font-weight:800;margin-top:2px;">{{ selectedRecord.name }}</div>
            </div>
            <span :style="detailStatusStyle(selectedRecord.status)">{{ selectedRecord.status }}</span>
          </div>
          <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;">
            <div>
              <div style="font-size:8px;font-weight:700;text-transform:uppercase;opacity:0.7;">Quantity</div>
              <div style="font-size:18px;font-weight:800;margin-top:2px;">{{ selectedRecord.reserved_qty }}</div>
              <div style="font-size:9px;opacity:0.7;">{{ selectedRecord.stock_uom || '' }}</div>
            </div>
            <div>
              <div style="font-size:8px;font-weight:700;text-transform:uppercase;opacity:0.7;">Reserved For</div>
              <div style="font-size:13px;font-weight:700;margin-top:4px;">{{ selectedRecord.reserved_for || '—' }}</div>
            </div>
            <div>
              <div style="font-size:8px;font-weight:700;text-transform:uppercase;opacity:0.7;">Date</div>
              <div style="font-size:13px;font-weight:700;margin-top:4px;">{{ selectedRecord.posting_date || '—' }}</div>
            </div>
            <div>
              <div style="font-size:8px;font-weight:700;text-transform:uppercase;opacity:0.7;">Company</div>
              <div style="font-size:13px;font-weight:700;margin-top:4px;">{{ selectedRecord.company }}</div>
            </div>
          </div>
        </div>

        <!-- ═══ TRANSFER FLOW ═══ -->
        <div style="background:#fff;border:1.5px solid #e2e8f0;border-radius:14px;padding:20px;margin-bottom:14px;">
          <div style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#3b82f6;margin-bottom:14px;font-family:'Montserrat',sans-serif;">Stock Transfer Flow</div>
          <div style="display:flex;align-items:stretch;gap:0;">
            <!-- Source warehouse -->
            <div style="flex:1;padding:16px;border:1.5px solid #10b981;border-radius:12px;background:linear-gradient(135deg,#ecfdf5,#f0fdf4);text-align:center;display:flex;flex-direction:column;justify-content:center;">
              <div style="width:36px;height:36px;border-radius:50%;background:#10b981;display:flex;align-items:center;justify-content:center;margin:0 auto 8px;">
                <span style="color:#fff;font-size:14px;">&#8592;</span>
              </div>
              <div style="font-size:8px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#10b981;margin-bottom:4px;">From (Source)</div>
              <div style="font-size:13px;font-weight:800;color:#065f46;">{{ getWarehouseShortName(selectedRecord.warehouse) }}</div>
              <div style="font-size:9px;color:#64748b;margin-top:2px;word-break:break-all;">{{ selectedRecord.warehouse }}</div>
              <div style="margin-top:10px;padding:6px 12px;background:#fff;border:1px solid #a7f3d0;border-radius:8px;display:inline-block;">
                <span style="font-size:18px;font-weight:800;color:#059669;">{{ selectedRecord.reserved_qty }}</span>
                <span style="font-size:9px;font-weight:600;color:#64748b;"> {{ selectedRecord.stock_uom || '' }}</span>
              </div>
            </div>

            <!-- Arrow -->
            <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:0 8px;min-width:80px;">
              <div style="font-size:11px;font-weight:800;color:#3b82f6;margin-bottom:4px;">{{ selectedRecord.reserved_qty }} units</div>
              <div style="position:relative;width:60px;height:24px;">
                <div style="position:absolute;top:11px;left:0;right:8px;height:3px;background:linear-gradient(90deg,#10b981,#3b82f6);border-radius:2px;"></div>
                <div style="position:absolute;top:5px;right:0;width:0;height:0;border-top:7px solid transparent;border-bottom:7px solid transparent;border-left:12px solid #3b82f6;"></div>
              </div>
              <div style="font-size:8px;font-weight:600;color:#64748b;margin-top:4px;">Reserved</div>
            </div>

            <!-- Destination warehouse -->
            <div style="flex:1;padding:16px;border:1.5px solid #3b82f6;border-radius:12px;background:linear-gradient(135deg,#eff6ff,#f0f9ff);text-align:center;display:flex;flex-direction:column;justify-content:center;">
              <div style="width:36px;height:36px;border-radius:50%;background:#3b82f6;display:flex;align-items:center;justify-content:center;margin:0 auto 8px;">
                <span style="color:#fff;font-size:14px;">&#8594;</span>
              </div>
              <div style="font-size:8px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#3b82f6;margin-bottom:4px;">To (Reserved)</div>
              <div style="font-size:13px;font-weight:800;color:#1e40af;">{{ getWarehouseShortName(selectedRecord.reserved_warehouse) }}</div>
              <div style="font-size:9px;color:#64748b;margin-top:2px;word-break:break-all;">{{ selectedRecord.reserved_warehouse }}</div>
              <div style="margin-top:10px;padding:6px 12px;background:#fff;border:1px solid #bfdbfe;border-radius:8px;display:inline-block;">
                <span style="font-size:18px;font-weight:800;color:#3b82f6;">+{{ selectedRecord.reserved_qty }}</span>
                <span style="font-size:9px;font-weight:600;color:#64748b;"> {{ selectedRecord.stock_uom || '' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- ═══ UNRESERVE FLOW (if released) ═══ -->
        <div v-if="selectedRecord.status === 'Released' && selectedRecord.unreserve_stock_entry" style="background:#fff;border:1.5px solid #e2e8f0;border-radius:14px;padding:20px;margin-bottom:14px;">
          <div style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#f59e0b;margin-bottom:14px;font-family:'Montserrat',sans-serif;">Unreserve Flow</div>
          <div style="display:flex;align-items:stretch;gap:0;">
            <!-- From Reserved -->
            <div style="flex:1;padding:16px;border:1.5px solid #f59e0b;border-radius:12px;background:linear-gradient(135deg,#fffbeb,#fef3c7);text-align:center;display:flex;flex-direction:column;justify-content:center;">
              <div style="width:36px;height:36px;border-radius:50%;background:#f59e0b;display:flex;align-items:center;justify-content:center;margin:0 auto 8px;">
                <span style="color:#fff;font-size:14px;">&#8592;</span>
              </div>
              <div style="font-size:8px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#d97706;margin-bottom:4px;">From (Reserved)</div>
              <div style="font-size:13px;font-weight:800;color:#92400e;">{{ getWarehouseShortName(selectedRecord.reserved_warehouse) }}</div>
              <div style="font-size:9px;color:#64748b;margin-top:2px;word-break:break-all;">{{ selectedRecord.reserved_warehouse }}</div>
            </div>

            <!-- Arrow -->
            <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:0 8px;min-width:80px;">
              <div style="font-size:11px;font-weight:800;color:#f59e0b;margin-bottom:4px;">{{ selectedRecord.reserved_qty }} units</div>
              <div style="position:relative;width:60px;height:24px;">
                <div style="position:absolute;top:11px;left:0;right:8px;height:3px;background:linear-gradient(90deg,#f59e0b,#10b981);border-radius:2px;"></div>
                <div style="position:absolute;top:5px;right:0;width:0;height:0;border-top:7px solid transparent;border-bottom:7px solid transparent;border-left:12px solid #10b981;"></div>
              </div>
              <div style="font-size:8px;font-weight:600;color:#64748b;margin-top:4px;">Unreserved</div>
            </div>

            <!-- To Unreserved -->
            <div style="flex:1;padding:16px;border:1.5px solid #10b981;border-radius:12px;background:linear-gradient(135deg,#ecfdf5,#f0fdf4);text-align:center;display:flex;flex-direction:column;justify-content:center;">
              <div style="width:36px;height:36px;border-radius:50%;background:#10b981;display:flex;align-items:center;justify-content:center;margin:0 auto 8px;">
                <span style="color:#fff;font-size:14px;">&#8594;</span>
              </div>
              <div style="font-size:8px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#10b981;margin-bottom:4px;">To (Unreserved)</div>
              <div style="font-size:13px;font-weight:800;color:#065f46;">{{ getUnreservedWhName(selectedRecord.company) }}</div>
              <div style="font-size:9px;color:#64748b;margin-top:2px;word-break:break-all;">{{ getUnreservedWhName(selectedRecord.company, true) }}</div>
              <div style="margin-top:10px;padding:6px 12px;background:#fff;border:1px solid #a7f3d0;border-radius:8px;display:inline-block;">
                <span style="font-size:18px;font-weight:800;color:#059669;">+{{ selectedRecord.reserved_qty }}</span>
                <span style="font-size:9px;font-weight:600;color:#64748b;"> {{ selectedRecord.stock_uom || '' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Item + Details -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px;">
          <div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;">
            <div style="font-size:8px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#64748b;margin-bottom:4px;">Item</div>
            <div style="font-size:14px;font-weight:800;color:#0f172a;">{{ selectedRecord.item }}</div>
            <div v-if="selectedRecord.item_name" style="font-size:10px;color:#64748b;margin-top:2px;">{{ selectedRecord.item_name }}</div>
          </div>
          <div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;">
            <div style="font-size:8px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#64748b;margin-bottom:4px;">Batch No</div>
            <div style="font-size:14px;font-weight:800;color:#0f172a;">{{ selectedRecord.batch_no || '—' }}</div>
          </div>
        </div>

        <!-- Linked Records -->
        <div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;margin-bottom:14px;">
          <div style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#64748b;margin-bottom:10px;">Linked Records</div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
            <div style="padding:10px;background:#f8fafc;border-radius:8px;border:1px solid #e2e8f0;">
              <div style="font-size:8px;font-weight:700;text-transform:uppercase;color:#64748b;margin-bottom:4px;">Sales Order</div>
              <div v-if="selectedRecord.sales_order" style="font-size:12px;font-weight:700;color:#3b82f6;cursor:pointer;" @click="frappe.set_route('Form','Sales Order',selectedRecord.sales_order)">{{ selectedRecord.sales_order }}</div>
              <div v-else style="font-size:12px;color:#94a3b8;">—</div>
            </div>
            <div style="padding:10px;background:#f8fafc;border-radius:8px;border:1px solid #e2e8f0;">
              <div style="font-size:8px;font-weight:700;text-transform:uppercase;color:#64748b;margin-bottom:4px;">Stock Entry</div>
              <div v-if="selectedRecord.stock_entry" style="font-size:12px;font-weight:700;color:#3b82f6;cursor:pointer;" @click="frappe.set_route('Form','Stock Entry',selectedRecord.stock_entry)">{{ selectedRecord.stock_entry }}</div>
              <div v-else style="font-size:12px;color:#94a3b8;">—</div>
            </div>
            <div v-if="selectedRecord.unreserve_stock_entry" style="padding:10px;background:#fffbeb;border-radius:8px;border:1px solid #fde68a;">
              <div style="font-size:8px;font-weight:700;text-transform:uppercase;color:#d97706;margin-bottom:4px;">Unreserve Stock Entry</div>
              <div style="font-size:12px;font-weight:700;color:#f59e0b;cursor:pointer;" @click="frappe.set_route('Form','Stock Entry',selectedRecord.unreserve_stock_entry)">{{ selectedRecord.unreserve_stock_entry }}</div>
            </div>
          </div>
        </div>

        <!-- Remarks -->
        <div v-if="selectedRecord.remarks" style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;margin-bottom:14px;">
          <div style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#64748b;margin-bottom:6px;">Remarks</div>
          <div style="font-size:12px;color:#334155;line-height:1.5;">{{ selectedRecord.remarks }}</div>
        </div>

        <!-- Timestamps -->
        <div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;margin-bottom:14px;">
          <div style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#64748b;margin-bottom:8px;">Timestamps</div>
          <div style="display:flex;gap:20px;">
            <div>
              <div style="font-size:8px;color:#64748b;">Created</div>
              <div style="font-size:11px;font-weight:600;color:#334155;">{{ formatDate(selectedRecord.creation) }}</div>
            </div>
            <div>
              <div style="font-size:8px;color:#64748b;">Modified</div>
              <div style="font-size:11px;font-weight:600;color:#334155;">{{ formatDate(selectedRecord.modified) }}</div>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div style="display:flex;gap:8px;">
          <button @click="view='list';selectedRecord=null" style="flex:1;padding:10px;border-radius:8px;border:1px solid #e2e8f0;background:#fff;color:#64748b;font-family:'Montserrat',sans-serif;font-size:11px;font-weight:700;cursor:pointer;">Back to List</button>
          <button v-if="selectedRecord.status === 'Reserved'" @click="releaseSingle(selectedRecord)" :disabled="singleReleasing"
            style="flex:1;padding:10px;border-radius:8px;border:none;background:#10b981;color:#fff;font-family:'Montserrat',sans-serif;font-size:11px;font-weight:700;cursor:pointer;">
            <span v-if="singleReleasing">...</span>
            <span v-else>Release Stock</span>
          </button>
          <button @click="frappe.set_route('Form','Stock Reservation',selectedRecord.name)" style="flex:1;padding:10px;border-radius:8px;border:none;background:#3b82f6;color:#fff;font-family:'Montserrat',sans-serif;font-size:11px;font-weight:700;cursor:pointer;">Open in Frappe</button>
        </div>
      </div>
    </ion-content>

    <!-- ═══ NEW RESERVATION FORM ═══ -->
    <ion-content v-if="view === 'new'">
      <div style="padding:12px 16px;">
        <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:20px;">
          <div style="font-size:14px;font-weight:800;color:#0f172a;margin-bottom:16px;font-family:'Montserrat',sans-serif;">New Reservation</div>

          <!-- Row 1: Company + Date -->
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:14px;">
            <div>
              <label style="display:block;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#64748b;margin-bottom:4px;font-family:'Montserrat',sans-serif;">Company</label>
              <select v-model="form.company" @change="onFormCompanyChange" style="width:100%;padding:8px 28px 8px 10px;border-radius:7px;border:1px solid #e2e8f0;background:#fff;color:#334155;font-family:'Montserrat',sans-serif;font-size:12px;font-weight:600;appearance:none;cursor:pointer;
                background-image:url('data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 width=%278%27 height=%275%27%3E%3Cpath d=%27M0 0l4 5 4-5z%27 fill=%27%2364748b%27/%3E%3C/svg%3E');
                background-repeat:no-repeat;background-position:right 8px center;">
                <option value="" disabled>Select company</option>
                <option v-for="c in companies" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
            <div>
              <label style="display:block;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#64748b;margin-bottom:4px;font-family:'Montserrat',sans-serif;">Date</label>
              <input v-model="form.posting_date" type="date"
                style="width:100%;padding:8px 10px;border-radius:7px;border:1px solid #e2e8f0;background:#fff;color:#334155;font-family:'Montserrat',sans-serif;font-size:12px;font-weight:600;outline:none;" />
            </div>
          </div>

          <!-- Row 2: Item -->
          <div style="margin-bottom:14px;">
            <label style="display:block;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#64748b;margin-bottom:4px;font-family:'Montserrat',sans-serif;">Item</label>
            <div style="position:relative;">
              <input v-model="query" @focus="open = true" @input="open = true" placeholder="Search item..."
                style="width:100%;padding:8px 10px;border-radius:7px;border:1px solid #e2e8f0;background:#fff;color:#334155;font-family:'Montserrat',sans-serif;font-size:12px;font-weight:600;outline:none;" />
              <div v-if="open && filteredFormItems.length" style="position:absolute;top:100%;left:0;right:0;z-index:50;background:#fff;border:1px solid #e2e8f0;border-radius:8px;box-shadow:0 8px 24px rgba(0,20,40,0.12);max-height:200px;overflow-y:auto;margin-top:4px;">
                <div v-for="item in filteredFormItems" :key="item.name" @mousedown.prevent="selectFormItem(item)"
                  style="padding:8px 10px;cursor:pointer;font-size:11px;font-weight:600;color:#334155;border-bottom:1px solid #f8fafc;transition:background 0.1s;font-family:'Montserrat',sans-serif;"
                  @mouseenter="$event.currentTarget.style.background='#f1f5f9'" @mouseleave="$event.currentTarget.style.background=''">
                  <div>{{ item.name }}</div>
                  <div style="font-size:9px;color:#64748b;">{{ item.item_name }}</div>
                </div>
              </div>
            </div>
            <div v-if="formItemSelected" style="margin-top:6px;display:flex;align-items:center;gap:6px;font-size:11px;font-weight:600;color:#0f172a;padding:6px 8px;background:#eff6ff;border-radius:6px;font-family:'Montserrat',sans-serif;">
              <span>&#10003; {{ formItemSelected.name }} <span style="font-weight:400;color:#64748b;">— {{ formItemSelected.item_name }}</span></span>
              <button @click="clearFormItem" style="margin-left:auto;font-size:9px;color:#ef4444;background:none;border:none;cursor:pointer;font-weight:700;">Remove</button>
            </div>
          </div>

          <!-- ═══ WAREHOUSE STOCK VISUAL ═══ -->
          <div v-if="form.company && formWarehousesLoading" style="margin-bottom:14px;padding:14px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;text-align:center;">
            <span style="font-size:11px;color:#64748b;font-family:'Montserrat',sans-serif;">Loading warehouses...</span>
          </div>

          <div v-else-if="form.company && formWarehouses.length" style="margin-bottom:14px;">
            <!-- Header -->
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
              <label style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#64748b;font-family:'Montserrat',sans-serif;">
                {{ formItemSelected ? 'Select Source Warehouse' : 'Warehouses' }} — {{ formWarehouses.length }}
              </label>
              <span v-if="formItemSelected" style="font-size:9px;font-weight:700;color:#64748b;font-family:'Montserrat',sans-serif;">
                {{ itemStockByCompany.filter(s => s.actual_qty > 0).length }} with stock
              </span>
            </div>

            <!-- Loading stock -->
            <div v-if="formItemSelected && itemStockByCompanyLoading" style="padding:14px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;text-align:center;">
              <span style="font-size:11px;color:#64748b;font-family:'Montserrat',sans-serif;">Loading stock data...</span>
            </div>

            <!-- Warehouse cards with stock bars -->
            <div v-else style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:8px;">
              <div v-for="w in formWarehouses" :key="w.name"
                @click="onWarehouseCardClick(w)"
                style="border-radius:10px;border:1.5px solid #e2e8f0;background:#fff;cursor:pointer;transition:all 0.15s;overflow:hidden;"
                :style="getWarehouseCardStyle(w)">

                <!-- Card header -->
                <div style="padding:10px 12px 6px;display:flex;align-items:center;justify-content:space-between;">
                  <div style="flex:1;min-width:0;">
                    <div style="font-size:11px;font-weight:700;color:#0f172a;font-family:'Montserrat',sans-serif;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{{ w.warehouse_name || w.name }}</div>
                    <div style="font-size:8px;color:#64748b;margin-top:1px;font-family:'Montserrat',sans-serif;">{{ w.name }}</div>
                  </div>
                  <!-- Selection indicator -->
                  <div v-if="form.warehouse === w.name" style="width:20px;height:20px;border-radius:50%;background:#3b82f6;display:flex;align-items:center;justify-content:center;margin-left:8px;">
                    <span style="color:#fff;font-size:10px;font-weight:700;">&#10003;</span>
                  </div>
                  <div v-else-if="formItemSelected && getItemStockForWarehouse(w.name) <= 0" style="width:20px;height:20px;border-radius:50%;background:#fee2e2;display:flex;align-items:center;justify-content:center;margin-left:8px;">
                    <span style="color:#ef4444;font-size:10px;font-weight:700;">&#10007;</span>
                  </div>
                </div>

                <!-- Stock bar (only when item selected) -->
                <div v-if="formItemSelected" style="padding:0 12px 10px;">
                  <div style="display:flex;align-items:baseline;gap:6px;margin-bottom:6px;">
                    <span style="font-size:20px;font-weight:800;font-family:'Montserrat',sans-serif;" :style="getItemStockForWarehouse(w.name) > 0 ? 'color:#059669' : 'color:#94a3b8'">
                      {{ getItemStockForWarehouse(w.name) }}
                    </span>
                    <span style="font-size:9px;font-weight:600;color:#64748b;font-family:'Montserrat',sans-serif;">{{ getStockUomLabel(w.name) }}</span>
                    <span style="font-size:9px;font-weight:600;color:#94a3b8;font-family:'Montserrat',sans-serif;margin-left:auto;">&#8377;{{ fmt(getItemStockValueForWarehouse(w.name)) }}</span>
                  </div>
                  <!-- Progress bar -->
                  <div style="height:6px;background:#f1f5f9;border-radius:3px;overflow:hidden;">
                    <div style="height:100%;border-radius:3px;transition:width 0.4s ease;"
                      :style="`width:${getStockBarWidth(w.name)}%;background:${getStockBarColor(w.name)}`"></div>
                  </div>
                  <!-- Status text -->
                  <div style="font-size:8px;margin-top:4px;font-weight:600;font-family:'Montserrat',sans-serif;"
                    :style="form.warehouse === w.name ? 'color:#3b82f6' : getItemStockForWarehouse(w.name) > 0 ? 'color:#059669' : getItemStockForWarehouse(w.name) < 0 ? 'color:#ef4444' : 'color:#94a3b8'">
                    {{ form.warehouse === w.name ? 'Selected as source' : getItemStockForWarehouse(w.name) > 0 ? 'Click to select as source' : getItemStockForWarehouse(w.name) < 0 ? 'Negative stock — click to select' : 'No stock — click to select' }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Total bar -->
            <div v-if="formItemSelected" style="margin-top:8px;padding:10px 14px;background:linear-gradient(135deg,#eff6ff,#f0fdf4);border:1px solid #e2e8f0;border-radius:8px;display:flex;align-items:center;justify-content:space-between;">
              <div>
                <div style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#64748b;font-family:'Montserrat',sans-serif;">Total Stock</div>
                <div style="font-size:16px;font-weight:800;color:#0f172a;font-family:'Montserrat',sans-serif;">{{ totalStockQty }} <span style="font-size:10px;font-weight:600;color:#64748b;">{{ totalStockUomLabel }}</span></div>
              </div>
              <div style="text-align:right;">
                <div style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#64748b;font-family:'Montserrat',sans-serif;">Total Value</div>
                <div style="font-size:14px;font-weight:800;color:#0f172a;font-family:'Montserrat',sans-serif;">&#8377;{{ fmt(totalStockValue) }}</div>
              </div>
            </div>
          </div>

          <!-- ═══ TRANSFER FLOW DIAGRAM ═══ -->
          <div v-if="form.warehouse && formItemSelected" style="margin-bottom:14px;padding:16px;background:linear-gradient(135deg,#eff6ff,#f0fdf4);border:1.5px solid #bfdbfe;border-radius:12px;">
            <div style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#3b82f6;margin-bottom:12px;font-family:'Montserrat',sans-serif;">Stock Transfer Flow</div>
            <div style="display:flex;align-items:center;gap:12px;">
              <!-- Source -->
              <div style="flex:1;padding:12px;background:#fff;border:1.5px solid #10b981;border-radius:10px;text-align:center;">
                <div style="font-size:8px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#10b981;margin-bottom:4px;font-family:'Montserrat',sans-serif;">From (Source)</div>
                <div style="font-size:11px;font-weight:700;color:#0f172a;font-family:'Montserrat',sans-serif;">{{ getWarehouseShortName(form.warehouse) }}</div>
                <div style="font-size:18px;font-weight:800;margin-top:4px;font-family:'Montserrat',sans-serif;" :style="getItemStockForWarehouse(form.warehouse) >= 0 ? 'color:#059669' : 'color:#ef4444'">
                  {{ getItemStockForWarehouse(form.warehouse) }}
                </div>
                <div style="font-size:8px;color:#64748b;font-family:'Montserrat',sans-serif;">{{ formItemSelected.stock_uom || 'units' }} available</div>
              </div>

              <!-- Arrow -->
              <div style="display:flex;flex-direction:column;align-items:center;gap:2px;min-width:60px;">
                <div style="font-size:9px;font-weight:700;color:#3b82f6;font-family:'Montserrat',sans-serif;">{{ form.reserved_qty || 0 }} units</div>
                <div style="display:flex;align-items:center;gap:0;">
                  <div style="width:16px;height:2px;background:#3b82f6;"></div>
                  <div style="width:0;height:0;border-top:6px solid transparent;border-bottom:6px solid transparent;border-left:10px solid #3b82f6;"></div>
                </div>
                <div style="font-size:8px;color:#64748b;font-family:'Montserrat',sans-serif;">Reserved</div>
              </div>

              <!-- Destination -->
              <div style="flex:1;padding:12px;background:#fff;border:1.5px solid #3b82f6;border-radius:10px;text-align:center;">
                <div style="font-size:8px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#3b82f6;margin-bottom:4px;font-family:'Montserrat',sans-serif;">To (Reserved)</div>
                <div style="font-size:11px;font-weight:700;color:#0f172a;font-family:'Montserrat',sans-serif;">{{ getReservedWhName() }}</div>
                <div style="font-size:18px;font-weight:800;color:#3b82f6;margin-top:4px;font-family:'Montserrat',sans-serif;">+{{ form.reserved_qty || 0 }}</div>
                <div style="font-size:8px;color:#64748b;font-family:'Montserrat',sans-serif;">incoming stock</div>
              </div>
            </div>
          </div>

          <!-- Row 3: Quantity + Reserved For -->
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:16px;">
            <div>
              <label style="display:block;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#64748b;margin-bottom:4px;font-family:'Montserrat',sans-serif;">Quantity to Reserve</label>
              <input v-model.number="form.reserved_qty" type="number" min="1"
                style="width:100%;padding:8px 10px;border-radius:7px;border:1px solid #e2e8f0;background:#fff;color:#334155;font-family:'Montserrat',sans-serif;font-size:12px;font-weight:600;outline:none;" />
            </div>
            <div>
              <label style="display:block;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#64748b;margin-bottom:4px;font-family:'Montserrat',sans-serif;">Reserved For</label>
              <div style="padding:8px 10px;border-radius:7px;border:1.5px solid #10b981;background:#ecfdf5;color:#065f46;font-family:'Montserrat',sans-serif;font-size:12px;font-weight:700;display:flex;align-items:center;gap:6px;">
                <span style="width:18px;height:18px;border-radius:50%;background:#10b981;display:inline-flex;align-items:center;justify-content:center;color:#fff;font-size:9px;font-weight:700;">S</span>
                Swastik
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div style="display:flex;gap:8px;">
            <button @click="view='list';resetForm()" style="flex:1;padding:10px;border-radius:8px;border:1px solid #e2e8f0;background:#fff;color:#64748b;font-family:'Montserrat',sans-serif;font-size:11px;font-weight:700;cursor:pointer;">Cancel</button>
            <button @click="submit" :disabled="saving || !canSubmit" style="flex:1;padding:10px;border-radius:8px;border:none;background:#3b82f6;color:#fff;font-family:'Montserrat',sans-serif;font-size:11px;font-weight:700;cursor:pointer;opacity:canSubmit?1:.5;">
              {{ saving ? 'Submitting...' : 'Create Reservation' }}
            </button>
          </div>

          <div v-if="fError" style="margin-top:12px;padding:10px;background:#fef2f2;border:1px solid #fecaca;border-radius:8px;font-size:11px;color:#ef4444;font-weight:600;font-family:'Montserrat',sans-serif;">{{ fError }}</div>
          <div v-if="fDone" style="margin-top:12px;padding:10px;background:#ecfdf5;border:1px solid #a7f3d0;border-radius:8px;font-size:11px;color:#059669;font-weight:600;font-family:'Montserrat',sans-serif;">&#10003; {{ fDone }}</div>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from "vue"
import { IonPage, IonHeader, IonToolbar, IonTitle, IonButtons, IonMenuButton, IonButton, IonIcon, IonContent } from "@ionic/vue"
import { addOutline, arrowBackOutline } from "ionicons/icons"
import { frappeRequest } from "frappe-ui"
import { getReservationKpis, createStockReservation, getCompanyWarehouses, getItemStockByCompany, unreserveStockReservations, releaseStockReservations } from "@/api/reservations"
import { getCompanies, getItems } from "@/api/common"

const API = "oil_distribution.api.oil_ops"
const ALL_CO = ["Geeta Enterprise", "Global Export", "Shubham Enterprise"]
const CO_MAP = { "Geeta Enterprise": "GE", "Global Export": "GEX", "Shubham Enterprise": "SHE" }

const view = ref("list")
const selectedRecord = ref(null)
const stats = ref([])
const items = ref([])
const companies = ref([])
const allItems = ref([])

/* ── Company Multi-Select ── */
const companyMsOpen = ref(false)
const companySelected = ref([...ALL_CO])
const companySearch = ref("")
const companyOptions = ALL_CO.map(c => ({ value: c, label: c, abbr: CO_MAP[c] || c.substring(0,3) }))
const companyMsContainer = ref(null)
const companyMsBtn = ref(null)
const companyMsPanel = ref(null)
const companyPanelPos = reactive({ left: 0, top: 0 })
const companyPanelStyle = computed(() => ({ left: companyPanelPos.left + "px", top: companyPanelPos.top + "px" }))
const filteredCompanyOptions = computed(() => {
  const q = companySearch.value.toLowerCase()
  return companyOptions.filter(o => o.label.toLowerCase().indexOf(q) !== -1)
})
const companyBtnLabel = computed(() => {
  const sel = companySelected.value
  if (sel.length === 0 || sel.length === ALL_CO.length) return "All"
  if (sel.length === 1) return (CO_MAP[sel[0]] || sel[0]) + ' <span class="rv-ms-count">' + sel.length + "</span>"
  return "Selected " + sel.length + ' <span class="rv-ms-count">' + sel.length + "</span>"
})
function toggleCompanyMs() {
  if (companyMsOpen.value) { companyMsOpen.value = false; return }
  itemMsOpen.value = false
  nextTick(() => {
    const btn = companyMsBtn.value
    if (btn) { const r = btn.getBoundingClientRect(); companyPanelPos.left = r.left; companyPanelPos.top = r.bottom + 4 }
    companyMsOpen.value = true
  })
}
function selectAllCompany() { companySelected.value = [...ALL_CO]; onCompanyChange() }
function clearCompany() { companySelected.value = [ALL_CO[0]]; onCompanyChange() }

/* ── Item Multi-Select ── */
const itemMsOpen = ref(false)
const itemSelected = ref([])
const itemSearch = ref("")
const itemOptions = ref([])
const itemMsContainer = ref(null)
const itemMsBtn = ref(null)
const itemMsPanel = ref(null)
const itemPanelPos = reactive({ left: 0, top: 0 })
const itemPanelStyle = computed(() => ({ left: itemPanelPos.left + "px", top: itemPanelPos.top + "px" }))
const filteredItemOptions = computed(() => {
  const q = itemSearch.value.toLowerCase()
  return itemOptions.value.filter(o => o.label.toLowerCase().indexOf(q) !== -1)
})
const itemBtnLabel = computed(() => {
  const sel = itemSelected.value
  const total = itemOptions.value.length
  if (sel.length === 0 || (total > 0 && sel.length === total)) return "All Items"
  if (sel.length === 1) return sel[0] + ' <span class="rv-ms-count">' + sel.length + "</span>"
  return "Selected " + sel.length + ' <span class="rv-ms-count">' + sel.length + "</span>"
})
function toggleItemMs() {
  if (itemMsOpen.value) { itemMsOpen.value = false; return }
  companyMsOpen.value = false
  nextTick(() => {
    const btn = itemMsBtn.value
    if (btn) { const r = btn.getBoundingClientRect(); itemPanelPos.left = r.left; itemPanelPos.top = r.bottom + 4 }
    itemMsOpen.value = true
  })
}
function selectAllItem() { itemSelected.value = itemOptions.value.map(o => o.value); onItemChange() }
function clearItemFilter() { itemSelected.value = itemOptions.value.length ? [itemOptions.value[0].value] : []; onItemChange() }

function getCompanyFilter() {
  const sel = companySelected.value
  if (sel.length === 0 || sel.length === ALL_CO.length) return "All"
  return sel.join(",")
}
function getItemFilter() {
  const sel = itemSelected.value
  const total = itemOptions.value.length
  if (sel.length === 0 || (total > 0 && sel.length === total)) return "All"
  return sel.join(",")
}
function onCompanyChange() { load() }
function onItemChange() { load() }

function handleDocClick(e) {
  if (companyMsOpen.value) {
    const c = companyMsContainer.value, p = companyMsPanel.value
    if (c && !c.contains(e.target) && p && !p.contains(e.target)) companyMsOpen.value = false
  }
  if (itemMsOpen.value) {
    const c = itemMsContainer.value, p = itemMsPanel.value
    if (c && !c.contains(e.target) && p && !p.contains(e.target)) itemMsOpen.value = false
  }
}

/* ── Form ── */
const form = ref({ company: "", warehouse: "", reserved_qty: 1, reserved_for: "Swastik", posting_date: new Date().toISOString().slice(0, 10) })
const query = ref("")
const formItemSelected = ref(null)
const open = ref(false)
const saving = ref(false)
const fError = ref("")
const fDone = ref("")
const formWarehouses = ref([])
const formWarehousesLoading = ref(false)
const itemStockByCompany = ref([])
const itemStockByCompanyLoading = ref(false)

/* ── Selection for Unreserve ── */
const selectedNames = ref(new Set())
const bulkUnreserving = ref(false)
const bulkReleasing = ref(false)
const singleReleasing = ref(false)

function toggleRow(name) {
  const s = new Set(selectedNames.value)
  if (s.has(name)) s.delete(name); else s.add(name)
  selectedNames.value = s
}

async function unreserveSelected() {
  const names = [...selectedNames.value]
  if (!names.length) return
  bulkUnreserving.value = true
  try {
    const r = await unreserveStockReservations(names)
    selectedNames.value = new Set()
    await load()
  } catch(e) {
    console.error(e)
  } finally {
    bulkUnreserving.value = false
  }
}

async function releaseSelected() {
  const names = [...selectedNames.value]
  if (!names.length) return
  bulkReleasing.value = true
  try {
    const r = await releaseStockReservations(names)
    selectedNames.value = new Set()
    await load()
  } catch(e) {
    console.error(e)
  } finally {
    bulkReleasing.value = false
  }
}

async function releaseSingle(rec) {
  singleReleasing.value = true
  try {
    await releaseStockReservations([rec.name])
    selectedRecord.value = null
    view.value = "list"
    await load()
  } catch(e) {
    console.error(e)
  } finally {
    singleReleasing.value = false
  }
}

const totalStockQty = computed(() => itemStockByCompany.value.reduce((s, r) => s + (r.actual_qty || 0), 0))
const totalStockValue = computed(() => itemStockByCompany.value.reduce((s, r) => s + (r.stock_value || 0), 0))
const totalAltQty = computed(() => {
  const first = itemStockByCompany.value.find(r => r.alt_qty != null)
  if (!first) return null
  return itemStockByCompany.value.reduce((s, r) => s + ((r.alt_qty || 0)), 0)
})
const totalAltUom = computed(() => {
  const first = itemStockByCompany.value.find(r => r.alt_uom)
  return first ? first.alt_uom : null
})
const totalStockUomLabel = computed(() => {
  let label = formItemSelected.value?.stock_uom || 'units'
  if (totalAltUom.value && totalAltQty.value != null) {
    label += ` (${fmtFloat(totalAltQty.value)} ${totalAltUom.value})`
  }
  return label
})

const canSubmit = computed(() => {
  return form.value.company && form.value.warehouse && formItemSelected.value && form.value.reserved_qty > 0
})

const filteredFormItems = computed(() => {
  if (!query.value) return allItems.value.slice(0, 20)
  const q = query.value.toLowerCase()
  return allItems.value.filter(i => i.name.toLowerCase().includes(q) || (i.item_name||"").toLowerCase().includes(q)).slice(0, 25)
})

const fmt = v => "\u20B9" + Number(v || 0).toLocaleString("en-IN",{maximumFractionDigits:0})
const fmtFloat = v => v != null ? Number(v).toLocaleString("en-IN",{maximumFractionDigits:2,minimumFractionDigits:1}) : ""

function formatDate(d) {
  if (!d) return "\u2014"
  return new Date(d).toLocaleString("en-IN", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" })
}

function statusStyle(s) {
  const m = {
    Reserved: "background:#d1fae5;color:#065f46;padding:3px 8px;border-radius:20px;font-size:9px;font-weight:700;font-family:'Montserrat',sans-serif;",
    Released: "background:#f1f5f9;color:#475569;padding:3px 8px;border-radius:20px;font-size:9px;font-weight:700;font-family:'Montserrat',sans-serif;",
    Sold: "background:#dbeafe;color:#1e40af;padding:3px 8px;border-radius:20px;font-size:9px;font-weight:700;font-family:'Montserrat',sans-serif;",
    Draft: "background:#fef3c7;color:#92400e;padding:3px 8px;border-radius:20px;font-size:9px;font-weight:700;font-family:'Montserrat',sans-serif;",
    Cancelled: "background:#fee2e2;color:#991b1b;padding:3px 8px;border-radius:20px;font-size:9px;font-weight:700;font-family:'Montserrat',sans-serif;",
  }
  return m[s] || "background:#f1f5f9;color:#475569;padding:3px 8px;border-radius:20px;font-size:9px;font-weight:700;font-family:'Montserrat',sans-serif;"
}

function detailStatusStyle(s) {
  const m = {
    Reserved: "background:rgba(255,255,255,0.2);color:#fff;padding:4px 12px;border-radius:20px;font-size:10px;font-weight:700;font-family:'Montserrat',sans-serif;",
    Released: "background:rgba(255,255,255,0.15);color:rgba(255,255,255,0.8);padding:4px 12px;border-radius:20px;font-size:10px;font-weight:700;font-family:'Montserrat',sans-serif;",
    Sold: "background:rgba(255,255,255,0.2);color:#fff;padding:4px 12px;border-radius:20px;font-size:10px;font-weight:700;font-family:'Montserrat',sans-serif;",
    Draft: "background:rgba(255,255,255,0.15);color:rgba(255,255,255,0.8);padding:4px 12px;border-radius:20px;font-size:10px;font-weight:700;font-family:'Montserrat',sans-serif;",
  }
  return m[s] || "background:rgba(255,255,255,0.15);color:rgba(255,255,255,0.8);padding:4px 12px;border-radius:20px;font-size:10px;font-weight:700;font-family:'Montserrat',sans-serif;"
}

function openDetail(item) { selectedRecord.value = item; view.value = "detail" }

function selectFormItem(item) {
  formItemSelected.value = item
  query.value = item.name
  open.value = false
  loadItemStockByCompany()
}

function clearFormItem() {
  formItemSelected.value = null
  query.value = ""
  itemStockByCompany.value = []
}

function resetForm() {
  form.value = { company: "", warehouse: "", reserved_qty: 1, reserved_for: "Swastik", posting_date: new Date().toISOString().slice(0, 10) }
  formItemSelected.value = null
  query.value = ""
  formWarehouses.value = []
  itemStockByCompany.value = []
  fError.value = ""
  fDone.value = ""
}

function getItemStockForWarehouse(whName) {
  const s = itemStockByCompany.value.find(r => r.warehouse === whName)
  return s ? s.actual_qty : 0
}

function getItemAltQtyForWarehouse(whName) {
  const s = itemStockByCompany.value.find(r => r.warehouse === whName)
  return s && s.alt_qty != null ? s.alt_qty : null
}

function getStockUomLabel(whName) {
  const s = itemStockByCompany.value.find(r => r.warehouse === whName)
  if (!s) return 'units'
  let label = s.stock_uom || 'units'
  if (s.alt_uom && s.alt_qty != null) {
    label += ` (${fmtFloat(s.alt_qty)} ${s.alt_uom})`
  }
  return label
}

function getItemStockValueForWarehouse(whName) {
  const s = itemStockByCompany.value.find(r => r.warehouse === whName)
  return s ? s.stock_value : 0
}

function getStockBarWidth(whName) {
  const qty = getItemStockForWarehouse(whName)
  if (qty === 0) return 0
  const absMax = Math.max(...itemStockByCompany.value.map(r => Math.abs(r.actual_qty || 0)), 1)
  return Math.max((Math.abs(qty) / absMax) * 100, 4)
}

function getStockBarColor(whName) {
  const qty = getItemStockForWarehouse(whName)
  if (qty < 0) return "#ef4444"
  if (qty === 0) return "#e2e8f0"
  const maxStock = Math.max(...itemStockByCompany.value.map(r => r.actual_qty || 0), 1)
  const ratio = qty / maxStock
  if (ratio > 0.6) return "#10b981"
  if (ratio > 0.3) return "#f59e0b"
  return "#ef4444"
}

function getWarehouseCardStyle(w) {
  if (form.warehouse === w.name) {
    return "border-color:#3b82f6;background:#eff6ff;box-shadow:0 0 0 3px rgba(59,130,246,0.1);"
  }
  return ""
}

function onWarehouseCardClick(w) {
  form.value.warehouse = w.name
}

function getWarehouseShortName(whName) {
  if (!whName) return ""
  const parts = whName.split(" - ")
  return parts.length > 1 ? parts.slice(-1)[0] : whName
}

function getReservedWhName() {
  const abbrMap = { "Geeta Enterprise": "GE", "Global Export": "GEX", "Shubham Enterprise": "SHE" }
  const abbr = abbrMap[form.value.company] || ""
  return `Reserved WH - ${abbr}`
}

function getUnreservedWhName(company, fullName = false) {
  const abbrMap = { "Geeta Enterprise": "GE", "Global Export": "GEX", "Shubham Enterprise": "SHE" }
  const abbr = abbrMap[company] || company.substring(0, 3)
  const wh = `Unreserved WH - ${abbr}`
  if (fullName) return wh
  return abbr
}

async function onFormCompanyChange() {
  form.value.warehouse = ""
  formWarehouses.value = []
  itemStockByCompany.value = []
  if (!form.value.company) return
  formWarehousesLoading.value = true
  try {
    formWarehouses.value = await getCompanyWarehouses(form.value.company)
  } catch(e) { console.error(e) }
  finally { formWarehousesLoading.value = false }
  if (formItemSelected.value) loadItemStockByCompany()
}

async function loadItemStockByCompany() {
  if (!formItemSelected.value || !form.value.company) return
  itemStockByCompanyLoading.value = true
  try {
    itemStockByCompany.value = await getItemStockByCompany(formItemSelected.value.name, form.value.company)
  } catch(e) { console.error(e) }
  finally { itemStockByCompanyLoading.value = false }
}

async function submit() {
  fError.value = ""; fDone.value = ""; saving.value = true
  try {
    const r = await createStockReservation({
      company: form.value.company,
      warehouse: form.value.warehouse,
      item: formItemSelected.value.name,
      reserved_qty: form.value.reserved_qty || 1,
      reserved_for: "Swastik",
      posting_date: form.value.posting_date,
    })
    fDone.value = `Reservation ${r.name} created (${r.status})`
    view.value = "list"
    resetForm()
    await load()
  } catch(e) { fError.value = e.messages?.[0] || e.message || "Failed" }
  finally { saving.value = false }
}

async function load() {
  try {
    const co = getCompanyFilter()
    const item = getItemFilter()
    const args = { limit: 100 }
    if (co !== "All") args.company = co
    if (item !== "All") args.item = item
    const [rows, k] = await Promise.all([
      frappeRequest({ url: `${API}.get_active_reservations`, params: args }),
      getReservationKpis(co === "All" ? "All" : co, item === "All" ? "" : item),
    ])
    items.value = rows
    stats.value = [
      { label: "Reserved Qty", value: k.total_reserved_qty },
      { label: "Total Value", value: fmt(k.total_reserved_value) },
      { label: "Utilization", value: k.utilization_pct + "%" },
      { label: "Active", value: k.active_count },
    ]
  } catch(e) { console.error(e) }
}

onMounted(async () => {
  document.addEventListener("click", handleDocClick)
  try {
    const [c, i] = await Promise.all([
      getCompanies(),
      getItems(),
    ])
    companies.value = c
    allItems.value = i
    itemOptions.value = i.map(item => ({ value: item.name, label: item.name + (item.item_name ? " - " + item.item_name : "") }))
    itemSelected.value = itemOptions.value.map(o => o.value)
    await load()
  } catch(e) { console.error(e) }
})
onUnmounted(() => { document.removeEventListener("click", handleDocClick) })
</script>

<style>
.rv-ms-btn { display:flex;align-items:center;gap:6px;padding:5px 28px 5px 10px;border-radius:7px;border:1px solid #e2e8f0;background:#fff;color:#334155;font-size:11px;font-weight:600;cursor:pointer;min-width:120px;white-space:nowrap;font-family:'Montserrat',sans-serif;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='8' height='5'%3E%3Cpath d='M0 0l4 5 4-5z' fill='%2364748b'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 8px center;transition:border-color 0.2s; }
.rv-ms-btn:hover { border-color:#cbd5e1; }
.rv-ms-btn.rv-ms-open { border-color:#3b82f6;box-shadow:0 0 0 3px rgba(59,130,246,0.1); }
.rv-ms-btn .rv-ms-count { background:#10b981;color:#fff;font-size:9px;font-weight:700;padding:1px 5px;border-radius:10px; }
.rv-ms-panel { display:none;position:fixed;z-index:9999;min-width:220px;max-height:280px;overflow-y:auto;background:#fff;border:1px solid #e2e8f0;border-radius:10px;box-shadow:0 8px 24px rgba(0,20,40,0.12);padding:6px; }
.rv-ms-panel.rv-ms-show { display:block; }
.rv-ms-search { width:100%;padding:6px 10px;border:1px solid #e2e8f0;border-radius:6px;font-size:11px;font-family:'Montserrat',sans-serif;outline:none;margin-bottom:4px; }
.rv-ms-search:focus { border-color:#3b82f6; }
.rv-ms-actions { display:flex;gap:4px;padding:4px 0;border-bottom:1px solid #f1f5f9;margin-bottom:4px; }
.rv-ms-action { padding:3px 8px;border-radius:5px;border:none;background:transparent;font-size:9px;font-weight:700;cursor:pointer;color:#3b82f6;font-family:'Montserrat',sans-serif; }
.rv-ms-action:hover { background:#dbeafe; }
.rv-ms-opt { display:flex;align-items:center;gap:8px;padding:5px 8px;border-radius:6px;cursor:pointer;transition:background 0.1s; }
.rv-ms-opt:hover { background:#f1f5f9; }
.rv-ms-opt input[type="checkbox"] { accent-color:#3b82f6;width:14px;height:14px;cursor:pointer; }
.rv-ms-opt-label { font-size:11px;font-weight:600;color:#334155;flex:1; }
.rv-ms-opt-abbr { font-size:9px;font-weight:700;color:#64748b; }
</style>
