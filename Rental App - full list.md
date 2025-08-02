**Rental App \- ERPNext** 

# BLUSH N GLOW BRIDAL RENTALS – BACKEND ERP SYSTEM SPECIFICATION (FINAL REVISION)

Powered By: ERPNext (customized)  
 Frontend: Virtual Store Interface (salesperson-facing)  
 Backend: ERPNext-based full business suite per store

---

## 👤 USER ROLES & ACCESS LEVELS

### 🔒 1\. Super Admin (HQ – Brand Owner)

* Manages all stores

* Has access to all branches’ data and reports

* Controls item listing approvals (item visible on store only after this)

* Creates account structure & company-wide settings

### 🔑 2\. Store Admin (One per Store)

* Controls one store

* Manages bookings, invoices, items, payments

* Views store-wise reports (P\&L, balance sheet)

* Has access only to that branch’s data

---

## 🧾 ACCOUNTING STRUCTURE (STORE-WISE)

### ✅ Chart of Accounts Setup

Each store maintains independent accounting. The following is replicated per company (store).

| Account Name | Account Type | Parent Group | Purpose |
| ----- | ----- | ----- | ----- |
| Capital Account | Equity | Equity | Initial investment by store owner |
| Bank Account | Asset | Current Asset | Store’s bank or current account |
| Cash Account | Asset | Current Asset | Cash on hand |
| Money Hand Account | Asset | Current Asset | Salesman or delivery person cash wallet |
| Inventory (Dresses) | Asset | Stock Assets | Physical stock including third-party |
| Inventory (Ornaments) | Asset | Stock Assets | Owned or consigned ornaments |
| Owner Commission Payable | Liability | Current Liability | Share owed to third-party item owners |
| Caution Deposit Received | Liability | Current Liability | Refundable deposit from customers |
| Rental Income | Income | Direct Income | Earnings from rentals |
| Dry Wash Charge Income | Income | Direct Income | Collected from customers |
| Dry Wash Expense | Expense | Indirect Expenses | Paid to laundry vendors |
| Salaries & Wages | Expense | Indirect Expenses | Staff salary |
| Electricity Expense | Expense | Indirect Expenses | Store power bills |
| EMI Payments (Vehicles) | Expense | Indirect Expenses | Monthly EMI for store vehicle (if any) |
| Repairs & Maintenance | Expense | Indirect Expenses | Item/furniture repairs |

🔧 NOTE: All these are created within each company separately in ERPNext, so P\&L and BS are store-specific.

---

## 📦 ITEM MANAGEMENT FLOW (INVENTORY \+ SERVICE AUTO SETUP)

### ✅ Add Item (From Store Admin Panel)

| Field Name | Type | Purpose |
| ----- | ----- | ----- |
| Item Name | Text | Eg: Blue Bridal Gown |
| Item Type | Select | Dress / Ornament |
| Is Third-Party Item? | Checkbox | Yes if owned by outsider (consignment) |
| Vendor (Purchase From) | Link | Owner, added as unpaid purchase (credit) |
| Owner Ledger Name | Text/Link | Track share of this owner via payable account |
| Rental Charge | Currency | Eg: ₹5000 (auto-used in rental service item) |
| Images | Attachment | Multiple high-quality images |
| Description / Notes | Text | Optional item notes |
| Requires Approval | Auto | “Yes” until Super Admin approves listing |

### 🛠️ Backend Automation on Save:

Once the item is saved:

1. Auto-create a Stock Item entry (own inventory)

2. Record Purchase of item from vendor on credit  
    → Inventory value \= Vendor liability (asset \= liability)

3. Auto-create Rental Service Item (eg: “Blue Gown Rental – ₹5000”) under Service Items

4. Hide item in frontend until Super Admin approves

### 🔐 Item Approval (Super Admin Workflow)

* Items are marked as `Pending Approval`

* Only on approval → item is shown in virtual store

---

## 🛍️ CUSTOMER BOOKING & RENTAL FLOW

### Booking Example:

Pooja’s Wedding on 20 August  
 Visits store on 28 July  
 Selects gown \+ ring  
 System checks booking availability → Available  
 Creates invoice with:

| Component | Type | Amount (₹) |
| ----- | ----- | ----- |
| Gown Rental | Service Item | 5000 |
| Ring Rental | Service Item | 2000 |
| Dry Cleaning Charge | Service Item | 500 |
| Caution Deposit | Liability | 2000 |
| Total |  | 9500 |
| Advance Paid |  | 4500 |
| Balance on Delivery |  | 5000 |

### ✅ Invoice Custom Fields:

| Field | Type | Notes |
| ----- | ----- | ----- |
| Function Date | Date | Customer's wedding date |
| Rental Duration | Integer | Default: 3 days |
| Advance Paid | Currency | Collected during booking |
| Caution Deposit | Currency | Auto-routed to liability account |
| Balance Due | Currency | Calculated: total \- advance |
| Booking Status | Select | Booked, Out for Rental, Returned |
| Is Exchange Booking? | Checkbox | For booking swaps only |

---

## 🔁 ITEM STATUS TRACKING

All items maintain status-based visibility internally, while remaining listed publicly.

| Status | Backend Status | Visible in Frontend |
| ----- | ----- | ----- |
| Available | Ready to Rent | ✅ Yes |
| Booked | Reserved | ✅ Yes |
| Out for Rental | With Customer | ✅ Yes (marked) |
| Under Dry Wash | Maintenance Phase | ✅ Yes (marked) |

---

## 📊 ITEM DASHBOARD

Each item in backend must have:

* Item images

* Booking calendar (future \+ past)

* Transaction history

* Current status

* Owner ledger (if third-party)

* Sales/Rental stats

---

## 💰 OWNER SHARE (Commission Payouts)

* Owner gets 30–50% of rental charge

* Based on item field: `Owner Commission %`

* Linked to “Owner Commission Payable” (Liability)

* Paid monthly via Payment Entry

📘 In ERPNext:

* Track item owner in custom field

* When rental invoice is created, system:

  * Books owner's share as liability

---

## 🔁 RETURN \+ DRY CLEANING FLOW

1. Customer returns product

2. Staff marks return

3. Item status changes to Under Dry Wash

4. After dry wash:

   * Staff updates item as “Available”

   * Or use Stock Entry: Transfer from Dry Wash to Main Store

---

## 🔁 EXCHANGE BOOKING POLICY

* No refunds

* If customer changes mind, allow:

  * Cancel initial booking

  * Advance is moved to new invoice

  * Previous invoice marked as Exchanged

* System ensures accurate tracking

---

## 📊 REPORTS REQUIRED (Store-level)

| Report Name | Purpose |
| ----- | ----- |
| Booking Calendar | View item availability |
| Rental Income Report | Income per day/month/year |
| Owner Payout Ledger | Track amounts owed to owners |
| Dry Cleaning Expenses | Track service provider payouts |
| Caution Deposit Ledger | Pending refunds |
| Item Usage History | Which item was used how often |
| Exchange Report | All booking swaps |
| Profit & Loss Statement | Per-store financial report |
| Balance Sheet | Per-store assets & liabilities |

---

## 🔧 MODULES TO CUSTOM-BUILD

| Module Name | Function |
| ----- | ----- |
| Item Approval Workflow | Super Admin verifies before publishing |
| Booking Conflict Checker | Checks availability across all branches |
| Invoice Auto-builder | Auto-pull rental, dry wash, deposit |
| Rental Status Automator | Handles movement: Booked → Out → Returned → Wash |
| Per-item Dashboard | Shows usage, status, owner ledger |
| Owner Commission Engine | Calculates & posts owner's % share |
| Store Accounting Shell | Accounts only store-specific |
| Exchange Booking Handler | Allow booking swap via same advance |

---

## 🧠 SYSTEM BEHAVIOR SUMMARY

1. All stores operate independently

2. Items are added per store; approval needed from super admin

3. Salespeople use frontend (virtual store wall)

4. Bookings always need date availability check

5. Payments include deposit, rental, dry wash

6. No refund → exchange only

7. Items tracked per lifecycle

8. Full accounting inside ERPNext — no external apps

---

## ✅ NEXT STEPS FOR DEVELOPER

* Build custom item addition page with automation (rental item, service item, vendor entry)

* Add approval workflow for item listing

* Create custom fields in invoice

* Implement rental booking Doctype with linked invoices

* Build item dashboard view

* Create multi-status tracker for stock movement

* Setup per-store accounting structures

* Add exchange booking flow

* Integrate booking availability calendar check

* Generate all required reports

