import io
import json
import os
from datetime import datetime, date
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# ---------- STREAMLIT CONFIGURATION ----------
st.set_page_config(
    page_title="NVB CULT | Accounting & ERP Suite",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- CUSTOM CSS (NVB CULT MODERN BLUE / DARK SLATE THEME) ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.stApp {
    background: radial-gradient(circle at 50% 0%, rgba(30, 58, 138, 0.15), transparent 40%),
                radial-gradient(circle at 100% 100%, rgba(37, 99, 235, 0.08), transparent 30%),
                #030712;
    color: #f1f5f9;
}

[data-testid="stSidebar"] {
    background-color: #0b1324;
    border-right: 1px solid #1e293b;
}

.nvb-card {
    background: linear-gradient(180deg, rgba(15, 23, 42, 0.95), rgba(11, 19, 36, 0.95));
    border: 1px solid #1e293b;
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 18px;
    box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
}

.metric-box {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 14px;
    padding: 16px;
    text-align: left;
}

.metric-title {
    font-size: 11px;
    font-weight: 700;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.metric-val {
    font-size: 24px;
    font-weight: 800;
    color: #ffffff;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 4px;
}

div[data-testid="stButton"] button {
    border-radius: 10px;
    font-weight: 700;
    font-size: 13px;
    transition: all 0.2s ease;
}

div[data-testid="stButton"] button[kind="primary"] {
    background: linear-gradient(135deg, #1d4ed8, #2563eb);
    border: 1px solid #3b82f6;
    color: white;
}

div[data-testid="stButton"] button[kind="primary"]:hover {
    background: linear-gradient(135deg, #1e40af, #1d4ed8);
    border-color: #60a5fa;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4);
}

div[data-testid="stDownloadButton"] button {
    border-radius: 10px;
    font-weight: 700;
    font-size: 13px;
    background: #064e3b;
    border: 1px solid #059669;
    color: #ecfdf5;
}

div[data-testid="stDownloadButton"] button:hover {
    background: #047857;
    border-color: #10b981;
}

[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input, [data-testid="stSelectbox"] div {
    background-color: #0b1324 !important;
    color: #f8fafc !important;
    border-color: #1e293b !important;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------- DATA STORAGE MANAGEMENT ----------
DATA_FILE = "accounting_data.json"

def get_default_data():
    return {
        "settings": {
            "companyName": "NVB CULT Streetwear & Tech",
            "gstin": "",
            "pan": "",
            "currency": "₹",
            "invoicePrefix": "NVB-2026-",
            "billPrefix": "BILL-2026-"
        },
        "invoices": [],
        "bills": []
    }

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return get_default_data()
    return get_default_data()

def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        st.error(f"Error saving data: {e}")

# ---------- AUTHENTICATION & SECRETS ----------
# Confidential authentication credentials
AUTH_USER = st.secrets.get("AUTH_USER", "alwin@nvb") if hasattr(st, "secrets") else "alwin@nvb"
AUTH_PASS = st.secrets.get("AUTH_PASS", "nvb2026") if hasattr(st, "secrets") else "nvb2026"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None

def render_login_gate():
    _, col_center, _ = st.columns([1, 1.4, 1])
    with col_center:
        st.markdown("""
        <div style="text-align: center; margin-top: 5rem; margin-bottom: 2rem;">
            <div style="display: inline-block; padding: 16px; border-radius: 20px; background: rgba(37,99,235,0.15); border: 1px solid rgba(59,130,246,0.3); margin-bottom: 1rem;">
                <span style="font-size: 32px;">🔐</span>
            </div>
            <div style="font-size: 30px; font-weight: 900; letter-spacing: -0.5px;">
                NVB <span style="color: #3b82f6;">CULT</span>
            </div>
            <div style="font-size: 13px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 2px; margin-top: 4px;">
                Accounting ERP & Portal Gate
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            st.markdown('<div class="nvb-card">', unsafe_allow_html=True)
            st.markdown("<p style='font-size: 13px; font-weight: 600; color: #94a3b8; margin-bottom: 12px;'>Authorized Sign-In</p>", unsafe_allow_html=True)
            
            user_input = st.text_input("Username", placeholder="Enter your authorized username")
            pass_input = st.text_input("Password", type="password", placeholder="Enter your secure password")
            
            submit_btn = st.form_submit_button("Sign In to NVB Portal", type="primary", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            if submit_btn:
                clean_user = user_input.strip().lower()
                clean_pass = pass_input.strip()
                if clean_user == AUTH_USER.strip().lower() and clean_pass == AUTH_PASS.strip():
                    st.session_state.authenticated = True
                    st.session_state.username = clean_user
                    st.success("Authentication successful. Loading workspace...")
                    st.rerun()
                else:
                    st.error("Invalid username or password. Access denied.")

        st.markdown("""
        <div style="text-align: center; margin-top: 1.5rem; font-size: 11px; color: #64748b;">
            🔒 Encrypted Session • Authorized Personnel Only
        </div>
        """, unsafe_allow_html=True)

if not st.session_state.authenticated:
    render_login_gate()
    st.stop()

# ---------- LOGGED-IN APPLICATION ----------
data = load_data()

# ---------- SIDEBAR NAVIGATION ----------
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 1.5rem;">
        <div style="width: 36px; height: 36px; border-radius: 10px; background: #2563eb; display: flex; align-items: center; justify-content: center; font-weight: 900; color: white;">
            NVB
        </div>
        <div>
            <div style="font-weight: 900; font-size: 18px; color: white; line-height: 1.1;">NVB CULT</div>
            <div style="font-size: 10px; font-weight: 700; color: #3b82f6; text-transform: uppercase;">Accounting ERP</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        [
            "📊 Financial Command Center",
            "🧾 Invoices (Sales Register)",
            "📋 Vendor Bills (Expenses & ITC)",
            "📥 Excel Import & Templates",
            "📑 Full Audit Excel Export",
            "🌐 Live Storefront & ERP Web View"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown(f"""
    <div style="font-size: 11px; color: #94a3b8; margin-bottom: 8px;">
        👤 User: <strong style="color: #f1f5f9;">Alwin</strong><br>
        🛡️ Role: <strong style="color: #60a5fa;">Admin / Owner</strong>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔒 Lock / Sign Out", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()

# ---------- HELPER EXCEL GENERATORS ----------
def generate_excel_download(df_dict):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for sheet_name, df in df_dict.items():
            df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
    return output.getvalue()

# ---------- PAGE 1: FINANCIAL COMMAND CENTER ----------
if page == "📊 Financial Command Center":
    st.markdown("## 📊 Financial Command Center & GST Audit")
    st.caption("Real-time revenue, input tax credits, gross profit, and balance metrics derived strictly from your books.")

    invoices = data["invoices"]
    bills = data["bills"]

    total_revenue = sum(float(i.get("total", 0)) for i in invoices)
    paid_revenue = sum(float(i.get("paidAmount", 0)) for i in invoices)
    ar = sum(float(i.get("balanceDue", 0)) for i in invoices)

    total_expenses = sum(float(b.get("total", 0)) for b in bills)
    paid_expenses = sum(float(b.get("paidAmount", 0)) for b in bills)
    ap = sum(float(b.get("balanceDue", 0)) for b in bills)

    output_gst = sum(float(i.get("taxAmount", 0)) for i in invoices)
    input_gst = sum(float(b.get("taxAmount", 0)) for b in bills)
    net_tax_payable = max(0.0, output_gst - input_gst)

    net_profit = total_revenue - total_expenses
    gross_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0.0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">Total Invoiced Revenue</div>
            <div class="metric-val">₹ {total_revenue:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">Total Vendor Expenses</div>
            <div class="metric-val" style="color: #f87171;">₹ {total_expenses:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">Net Operating Profit</div>
            <div class="metric-val" style="color: {'#34d399' if net_profit >= 0 else '#f87171'};">₹ {net_profit:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">Gross Margin</div>
            <div class="metric-val" style="color: #60a5fa;">{gross_margin:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">GST Output Liability (Sales)</div>
            <div class="metric-val">₹ {output_gst:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with g2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">Input Tax Credit (ITC Available)</div>
            <div class="metric-val" style="color: #34d399;">₹ {input_gst:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with g3:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">Net GST Payable (Output - ITC)</div>
            <div class="metric-val" style="color: #fbbf24;">₹ {net_tax_payable:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

# ---------- PAGE 2: INVOICES (SALES REGISTER) ----------
elif page == "🧾 Invoices (Sales Register)":
    st.markdown("## 🧾 Invoices & Sales Register")
    
    with st.expander("➕ Create New Tax Invoice", expanded=False):
        with st.form("new_invoice_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                inv_num = st.text_input("Invoice Number", value=f"NVB-2026-{len(data['invoices'])+1:04d}")
                client_name = st.text_input("Client / Customer Name")
                client_gstin = st.text_input("Client GSTIN (optional)")
            with col_b:
                issue_date = st.date_input("Issue Date", value=date.today())
                due_date = st.date_input("Due Date", value=date.today())
                inv_status = st.selectbox("Status", ["Sent", "Paid", "Draft"])

            st.markdown("##### Invoice Line Items")
            item_desc = st.text_input("Item Description", placeholder="e.g. 240 GSM French Terry Cotton Oversized Tee")
            col_q, col_r, col_t = st.columns(3)
            with col_q:
                qty = st.number_input("Quantity", min_value=1, value=10, step=1)
            with col_r:
                rate = st.number_input("Unit Rate (₹)", min_value=0.0, value=999.0, step=10.0)
            with col_t:
                tax_rate = st.selectbox("GST Rate (%)", [0, 5, 12, 18, 28], index=3)

            submit_inv = st.form_submit_button("Generate & Post Invoice", type="primary")
            if submit_inv:
                if not client_name.strip():
                    st.error("Please enter a Client Name")
                else:
                    subtotal = qty * rate
                    tax_amount = (subtotal * tax_rate) / 100.0
                    total = subtotal + tax_amount
                    new_inv = {
                        "id": f"inv-{int(datetime.now().timestamp()*1000)}",
                        "invoiceNumber": inv_num,
                        "clientName": client_name,
                        "clientGstin": client_gstin,
                        "issueDate": str(issue_date),
                        "dueDate": str(due_date),
                        "status": inv_status,
                        "subtotal": subtotal,
                        "taxAmount": tax_amount,
                        "total": total,
                        "paidAmount": total if inv_status == "Paid" else 0.0,
                        "balanceDue": 0.0 if inv_status == "Paid" else total,
                        "itemDesc": item_desc,
                        "qty": qty,
                        "rate": rate,
                        "taxRate": tax_rate
                    }
                    data["invoices"].insert(0, new_inv)
                    save_data(data)
                    st.success(f"Invoice {inv_num} posted successfully!")
                    st.rerun()

    if data["invoices"]:
        df_inv = pd.DataFrame(data["invoices"])
        display_cols = ["invoiceNumber", "clientName", "issueDate", "dueDate", "status", "subtotal", "taxAmount", "total", "paidAmount", "balanceDue"]
        valid_cols = [c for c in display_cols if c in df_inv.columns]
        st.dataframe(df_inv[valid_cols], use_container_width=True)

        excel_data = generate_excel_download({"Invoices_Register": df_inv})
        st.download_button(
            label="📥 Export Invoices to Excel (.xlsx)",
            data=excel_data,
            file_name=f"NVB_Invoices_Register_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("No invoices logged yet. Create your first invoice above.")

# ---------- PAGE 3: VENDOR BILLS (EXPENSES & ITC) ----------
elif page == "📋 Vendor Bills (Expenses & ITC)":
    st.markdown("## 📋 Vendor Bills & Expense Tracker")

    with st.expander("➕ Log New Vendor / Purchase Bill", expanded=False):
        with st.form("new_bill_form"):
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                bill_num = st.text_input("Bill / Invoice Number", value=f"BILL-2026-{len(data['bills'])+1:04d}")
                vendor_name = st.text_input("Supplier / Vendor Name")
                category = st.selectbox("Category", [
                    "Raw Materials & Cotton Fabric",
                    "Garment Manufacturing & Stitching",
                    "Titanium & Metal CNC Tooling",
                    "MagSafe Magnet Assemblies",
                    "Packaging & Premium Unboxing",
                    "Logistics & Dark Hub Fleet"
                ])
            with col_v2:
                bill_date = st.date_input("Bill Date", value=date.today())
                bill_due = st.date_input("Due Date", value=date.today())
                bill_status = st.selectbox("Status", ["Unpaid", "Paid"])

            col_amt, col_tax = st.columns(2)
            with col_amt:
                amount = st.number_input("Taxable Amount (₹)", min_value=0.0, value=25000.0, step=500.0)
            with col_tax:
                tax_amt = st.number_input("GST Tax Amount (₹)", min_value=0.0, value=4500.0, step=100.0)

            submit_bill = st.form_submit_button("Save Vendor Bill", type="primary")
            if submit_bill:
                if not vendor_name.strip():
                    st.error("Please enter a Vendor Name")
                else:
                    total_bill = amount + tax_amt
                    new_bill = {
                        "id": f"bill-{int(datetime.now().timestamp()*1000)}",
                        "billNumber": bill_num,
                        "vendorName": vendor_name,
                        "category": category,
                        "billDate": str(bill_date),
                        "dueDate": str(bill_due),
                        "status": bill_status,
                        "amount": amount,
                        "taxAmount": tax_amt,
                        "total": total_bill,
                        "paidAmount": total_bill if bill_status == "Paid" else 0.0,
                        "balanceDue": 0.0 if bill_status == "Paid" else total_bill
                    }
                    data["bills"].insert(0, new_bill)
                    save_data(data)
                    st.success(f"Vendor bill {bill_num} saved successfully!")
                    st.rerun()

    if data["bills"]:
        df_bills = pd.DataFrame(data["bills"])
        display_b_cols = ["billNumber", "vendorName", "category", "billDate", "dueDate", "status", "amount", "taxAmount", "total", "paidAmount", "balanceDue"]
        valid_b_cols = [c for c in display_b_cols if c in df_bills.columns]
        st.dataframe(df_bills[valid_b_cols], use_container_width=True)

        excel_b_data = generate_excel_download({"Vendor_Bills_ITC": df_bills})
        st.download_button(
            label="📥 Export Vendor Bills to Excel (.xlsx)",
            data=excel_b_data,
            file_name=f"NVB_Vendor_Bills_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("No vendor bills logged yet. Log your first purchase bill above.")

# ---------- PAGE 4: EXCEL IMPORT & TEMPLATES ----------
elif page == "📥 Excel Import & Templates":
    st.markdown("## 📥 Excel Bulk Import & Templates Hub")
    st.caption("Upload `.xlsx` or `.csv` files to bulk-import transactions, or download ready-to-fill templates.")

    t1, t2 = st.columns(2)
    with t1:
        st.markdown("### 1. Download Blank Templates")
        # Blank Invoice Template
        df_inv_tpl = pd.DataFrame([{
            "InvoiceNumber": "NVB-2026-0001",
            "ClientName": "Client Name",
            "ClientGSTIN": "33AAACN0000Z1Z5",
            "IssueDate": "2026-10-20",
            "DueDate": "2026-11-20",
            "Status": "Sent",
            "ItemDescription": "240 GSM Cotton Tee",
            "Quantity": 10,
            "UnitRate": 999.0,
            "GSTRate": 18
        }])
        tpl_inv_bytes = generate_excel_download({"Invoice_Template": df_inv_tpl})
        st.download_button("📄 Download Invoice Excel Template", data=tpl_inv_bytes, file_name="NVB_Invoice_Template.xlsx")

        # Blank Bill Template
        df_bill_tpl = pd.DataFrame([{
            "BillNumber": "BILL-2026-0001",
            "VendorName": "Supplier Name",
            "Category": "Raw Materials & Cotton Fabric",
            "BillDate": "2026-10-20",
            "DueDate": "2026-11-10",
            "Status": "Unpaid",
            "Amount": 25000.0,
            "TaxAmount": 4500.0
        }])
        tpl_bill_bytes = generate_excel_download({"Bill_Template": df_bill_tpl})
        st.download_button("📄 Download Vendor Bill Excel Template", data=tpl_bill_bytes, file_name="NVB_Vendor_Bill_Template.xlsx")

    with t2:
        st.markdown("### 2. Bulk Upload & Import")
        import_type = st.selectbox("What are you importing?", ["Invoices", "Vendor Bills"])
        uploaded_file = st.file_uploader("Upload Excel (.xlsx) or CSV file", type=["xlsx", "csv"])

        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    df_up = pd.read_csv(uploaded_file)
                else:
                    df_up = pd.read_excel(uploaded_file)
                
                st.write(f"Previewing {len(df_up)} detected rows:")
                st.dataframe(df_up.head(5), use_container_width=True)

                if st.button("🚀 Commit & Import Rows into ERP", type="primary"):
                    imported_count = 0
                    for idx, row in df_up.iterrows():
                        r = row.to_dict()
                        if import_type == "Invoices":
                            qty = float(r.get("Quantity", r.get("qty", 1)))
                            rate = float(r.get("UnitRate", r.get("rate", 0)))
                            tax_r = float(r.get("GSTRate", r.get("taxRate", 18)))
                            sub = qty * rate
                            tx = (sub * tax_r) / 100.0
                            tot = sub + tx
                            st_stat = str(r.get("Status", "Sent"))
                            inv_obj = {
                                "id": f"inv-imp-{int(datetime.now().timestamp()*1000)}-{idx}",
                                "invoiceNumber": str(r.get("InvoiceNumber", f"NVB-IMP-{idx+1}")),
                                "clientName": str(r.get("ClientName", "Imported Client")),
                                "clientGstin": str(r.get("ClientGSTIN", "")),
                                "issueDate": str(r.get("IssueDate", date.today())),
                                "dueDate": str(r.get("DueDate", date.today())),
                                "status": st_stat,
                                "subtotal": sub,
                                "taxAmount": tx,
                                "total": tot,
                                "paidAmount": tot if st_stat == "Paid" else 0.0,
                                "balanceDue": 0.0 if st_stat == "Paid" else tot
                            }
                            data["invoices"].insert(0, inv_obj)
                            imported_count += 1
                        else:
                            amt = float(r.get("Amount", r.get("amount", 0)))
                            tx_amt = float(r.get("TaxAmount", r.get("taxAmount", 0)))
                            tot_b = amt + tx_amt
                            b_stat = str(r.get("Status", "Unpaid"))
                            bill_obj = {
                                "id": f"bill-imp-{int(datetime.now().timestamp()*1000)}-{idx}",
                                "billNumber": str(r.get("BillNumber", f"BILL-IMP-{idx+1}")),
                                "vendorName": str(r.get("VendorName", "Imported Vendor")),
                                "category": str(r.get("Category", "Raw Materials & Cotton Fabric")),
                                "billDate": str(r.get("BillDate", date.today())),
                                "dueDate": str(r.get("DueDate", date.today())),
                                "status": b_stat,
                                "amount": amt,
                                "taxAmount": tx_amt,
                                "total": tot_b,
                                "paidAmount": tot_b if b_stat == "Paid" else 0.0,
                                "balanceDue": 0.0 if b_stat == "Paid" else tot_b
                            }
                            data["bills"].insert(0, bill_obj)
                            imported_count += 1
                    save_data(data)
                    st.success(f"Successfully imported {imported_count} records into your books!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error parsing uploaded file: {e}")

# ---------- PAGE 5: FULL AUDIT EXCEL EXPORT ----------
elif page == "📑 Full Audit Excel Export":
    st.markdown("## 📑 Full Multi-Tab Financial Audit Workbook")
    st.write("Generate a comprehensive multi-sheet Excel file (`.xlsx`) containing separate tabs for Invoices, Vendor Bills, and P&L Tax Summary.")

    df_invoices = pd.DataFrame(data["invoices"]) if data["invoices"] else pd.DataFrame([{"Notice": "No Invoices Logged"}])
    df_bills = pd.DataFrame(data["bills"]) if data["bills"] else pd.DataFrame([{"Notice": "No Bills Logged"}])
    
    rev = sum(float(i.get("total", 0)) for i in data["invoices"])
    exp = sum(float(b.get("total", 0)) for b in data["bills"])
    df_summary = pd.DataFrame([
        {"Financial Metric": "Gross Invoiced Revenue", "Amount (₹)": rev},
        {"Financial Metric": "Gross Vendor Expenses", "Amount (₹)": exp},
        {"Financial Metric": "Net Operating Profit", "Amount (₹)": rev - exp},
        {"Financial Metric": "Output GST Liability", "Amount (₹)": sum(float(i.get("taxAmount", 0)) for i in data["invoices"])},
        {"Financial Metric": "Input Tax Credit (ITC)", "Amount (₹)": sum(float(b.get("taxAmount", 0)) for b in data["bills"])}
    ])

    audit_bytes = generate_excel_download({
        "Invoices_Register": df_invoices,
        "Vendor_Bills_ITC": df_bills,
        "P&L_and_Tax_Summary": df_summary
    })

    st.download_button(
        label="📥 Download Full Multi-Tab Audit Workbook (.xlsx)",
        data=audit_bytes,
        file_name=f"NVB_Full_Audit_Workbook_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ---------- PAGE 6: LIVE STOREFRONT & ERP WEB VIEW ----------
elif page == "🌐 Live Storefront & ERP Web View":
    st.markdown("## 🌐 NVB Cult Web Portal")
    st.caption("Embedded live web portal connected directly to your Next.js application.")
    
    web_url = st.text_input("Portal URL", value="http://localhost:4000/accounting")
    components.iframe(src=web_url, height=850, scrolling=True)
