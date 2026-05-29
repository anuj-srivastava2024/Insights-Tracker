import streamlit as st
import json
import os
from datetime import date, datetime
import pandas as pd

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Trade Contract Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Constants ─────────────────────────────────────────────────────────────────
DATA_FILE = "data.json"

TAGS = {
    "Absorption":     "#6366f1",   # indigo
    "Iceberg":        "#0ea5e9",   # sky blue
    "Tool":           "#f59e0b",   # amber
    "Extreme Delta":  "#ef4444",   # red
    "Extreme Volume": "#8b5cf6",   # violet
    "Bullish":        "#22c55e",   # green
    "Bearish":        "#f97316",   # orange
}

# ── Persistence helpers ───────────────────────────────────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)

# ── Session state bootstrap ───────────────────────────────────────────────────
if "db" not in st.session_state:
    st.session_state.db = load_data()
    # db = { page_name: { columns: [...], rows: { date_str: { col: {text, tags} } } } }

if "current_page" not in st.session_state:
    st.session_state.current_page = None

if "editing_cell" not in st.session_state:
    st.session_state.editing_cell = None   # (date_str, col_name)

db = st.session_state.db

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Sora:wght@300;400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Sora', sans-serif; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0f172a;
    border-right: 1px solid #1e293b;
}
section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
section[data-testid="stSidebar"] .stButton button {
    background: #1e293b;
    border: 1px solid #334155;
    color: #e2e8f0 !important;
    border-radius: 6px;
    font-size: 13px;
    text-align: left;
    width: 100%;
    margin-bottom: 4px;
    transition: all .15s;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: #334155;
    border-color: #6366f1;
}

/* Main area */
.main { background: #0f172a; }

/* Tracker table */
.tracker-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.tracker-table th {
    background: #1e293b;
    color: #94a3b8;
    padding: 10px 14px;
    border: 1px solid #334155;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: .08em;
    min-width: 140px;
    position: sticky;
    top: 0;
}
.tracker-table td {
    border: 1px solid #1e293b;
    padding: 8px 12px;
    vertical-align: top;
    color: #e2e8f0;
    background: #0f172a;
    white-space: pre-wrap;
    word-break: break-word;
    min-width: 140px;
    min-height: 40px;
}
.tracker-table td.date-cell {
    background: #1e293b;
    color: #6366f1;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    white-space: nowrap;
}
.tracker-table td.date-cell:hover { background: #334155; }
.tracker-table tr:hover td { background: #111827; }
.tracker-table tr:hover td.date-cell { background: #1e3a5f; }

/* Tags */
.tag-pill {
    display: inline-block;
    padding: 2px 9px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    margin: 2px 2px 2px 0;
    color: #fff;
    letter-spacing: .04em;
}

/* Buttons */
.stButton button {
    background: #1e293b !important;
    color: #e2e8f0 !important;
    border: 1px solid #334155 !important;
    border-radius: 6px !important;
}
.stButton button:hover {
    border-color: #6366f1 !important;
    background: #334155 !important;
}

/* Inputs */
.stTextInput input, .stTextArea textarea, .stMultiSelect [data-baseweb="tag"] {
    background: #1e293b !important;
    color: #e2e8f0 !important;
    border-color: #334155 !important;
}

/* Title */
.page-title {
    font-size: 26px;
    font-weight: 700;
    color: #e2e8f0;
    letter-spacing: -.02em;
    margin-bottom: 4px;
}
.page-sub {
    font-size: 12px;
    color: #475569;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 20px;
}

/* Active page highlight */
.active-page button {
    border-color: #6366f1 !important;
    background: #1e1b4b !important;
}
</style>
""", unsafe_allow_html=True)


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📊 Trade Tracker")
    st.markdown("---")

    # New page
    with st.expander("➕ New Page", expanded=False):
        new_name = st.text_input("Page name", key="new_page_name", placeholder="e.g. NQ Contracts")
        if st.button("Create Page") and new_name.strip():
            name = new_name.strip()
            if name not in db:
                db[name] = {"columns": [], "rows": {}}
                save_data(db)
                st.session_state.current_page = name
                st.rerun()
            else:
                st.warning("Page already exists.")

    st.markdown("**Pages**")
    if not db:
        st.caption("No pages yet. Create one above.")
    for pg in list(db.keys()):
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(f"📄 {pg}", key=f"nav_{pg}"):
                st.session_state.current_page = pg
                st.session_state.editing_cell = None
                st.rerun()
        with col2:
            if st.button("🗑", key=f"del_{pg}"):
                del db[pg]
                if st.session_state.current_page == pg:
                    st.session_state.current_page = next(iter(db), None)
                save_data(db)
                st.rerun()

    st.markdown("---")
    st.markdown("**Tag Legend**")
    for tag, color in TAGS.items():
        st.markdown(
            f'<span class="tag-pill" style="background:{color}">{tag}</span>',
            unsafe_allow_html=True
        )


# ── MAIN ──────────────────────────────────────────────────────────────────────
page = st.session_state.current_page

if page is None:
    st.markdown("""
    <div style="text-align:center; padding:80px 0; color:#475569;">
        <div style="font-size:52px; margin-bottom:16px;">📊</div>
        <div style="font-size:22px; font-weight:700; color:#94a3b8; margin-bottom:8px;">Trade Contract Tracker</div>
        <div style="font-size:14px;">Create a page from the sidebar to get started.</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

page_data = db[page]

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(f'<div class="page-title">📄 {page}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="page-sub">observation tracker • {len(page_data["rows"])} rows</div>', unsafe_allow_html=True)

# ── Column management ─────────────────────────────────────────────────────────
with st.expander("⚙️ Manage Columns", expanded=len(page_data["columns"]) == 0):
    cols_ui = st.columns([4, 1])
    with cols_ui[0]:
        new_col = st.text_input("Column name (contract)", placeholder="e.g. NQ Dec-24", key="new_col")
    with cols_ui[1]:
        st.write("")
        st.write("")
        if st.button("Add Column") and new_col.strip():
            col_name = new_col.strip()
            if col_name not in page_data["columns"]:
                page_data["columns"].append(col_name)
                save_data(db)
                st.rerun()

    if page_data["columns"]:
        st.write("**Current columns:**")
        remove_col = st.selectbox("Remove column", ["—"] + page_data["columns"], key="remove_col")
        if st.button("Remove") and remove_col != "—":
            page_data["columns"].remove(remove_col)
            for row_data in page_data["rows"].values():
                row_data.pop(remove_col, None)
            save_data(db)
            st.rerun()

# ── Add row (date) ────────────────────────────────────────────────────────────
st.markdown("### Add / Select Date Row")
c1, c2 = st.columns([2, 1])
with c1:
    chosen_date = st.date_input("Pick a date", value=date.today(), key="date_picker")
with c2:
    st.write("")
    st.write("")
    if st.button("➕ Add Date Row"):
        dstr = str(chosen_date)
        if dstr not in page_data["rows"]:
            page_data["rows"][dstr] = {}
        save_data(db)
        st.rerun()

# ── Guard: need columns ───────────────────────────────────────────────────────
if not page_data["columns"]:
    st.info("Add at least one contract column above to start tracking.")
    st.stop()

if not page_data["rows"]:
    st.info("Pick a date above and click **Add Date Row** to create your first entry.")
    st.stop()

# ── Cell editor (shown when a cell is selected) ───────────────────────────────
ec = st.session_state.editing_cell
if ec:
    edate, ecol = ec
    cell_key = f"{edate}__{ecol}"
    cell = page_data["rows"].get(edate, {}).get(ecol, {"text": "", "tags": []})

    with st.container():
        st.markdown(f"#### ✏️ Editing — `{edate}` × **{ecol}**")
        new_text = st.text_area("Notes / Insights", value=cell.get("text", ""), height=120, key=f"txt_{cell_key}")
        new_tags = st.multiselect(
            "Tags",
            options=list(TAGS.keys()),
            default=cell.get("tags", []),
            key=f"tags_{cell_key}",
        )
        bcol1, bcol2 = st.columns([1, 5])
        with bcol1:
            if st.button("💾 Save"):
                if edate not in page_data["rows"]:
                    page_data["rows"][edate] = {}
                page_data["rows"][edate][ecol] = {"text": new_text, "tags": new_tags}
                save_data(db)
                st.session_state.editing_cell = None
                st.rerun()
        with bcol2:
            if st.button("✖ Cancel"):
                st.session_state.editing_cell = None
                st.rerun()
        st.markdown("---")

# ── Render tracker table ──────────────────────────────────────────────────────
sorted_dates = sorted(page_data["rows"].keys())

# Build HTML table
header_cells = '<th>📅 Date</th>' + "".join(f"<th>{c}</th>" for c in page_data["columns"])

rows_html = ""
for dstr in sorted_dates:
    row_data = page_data["rows"][dstr]
    # Format date nicely
    try:
        d = datetime.strptime(dstr, "%Y-%m-%d")
        date_display = d.strftime("%a, %b %d %Y")
    except:
        date_display = dstr

    row_cells = f'<td class="date-cell">📅 {date_display}</td>'
    for col in page_data["columns"]:
        cell = row_data.get(col, {"text": "", "tags": []})
        text = cell.get("text", "")
        tags = cell.get("tags", [])
        tags_html = "".join(
            f'<span class="tag-pill" style="background:{TAGS.get(t, "#555")}">{t}</span>'
            for t in tags
        )
        content = f"{tags_html}<div style='margin-top:4px;color:#cbd5e1;font-size:13px'>{text}</div>" if (tags or text) else '<span style="color:#334155">click to edit</span>'
        row_cells += f'<td>{content}</td>'
    rows_html += f"<tr>{row_cells}</tr>"

table_html = f"""
<div style="overflow-x:auto; border-radius:10px; border:1px solid #1e293b; margin-top:8px;">
<table class="tracker-table">
  <thead><tr>{header_cells}</tr></thead>
  <tbody>{rows_html}</tbody>
</table>
</div>
"""
st.markdown(table_html, unsafe_allow_html=True)

# ── Click-to-edit controls (below table) ─────────────────────────────────────
st.markdown("### 🖊️ Edit a Cell")
st.caption("Select a date and column to open the cell editor.")

ec1, ec2, ec3 = st.columns([2, 2, 1])
with ec1:
    sel_date = st.selectbox("Date row", sorted_dates, key="sel_date",
                            format_func=lambda d: datetime.strptime(d, "%Y-%m-%d").strftime("%a, %b %d %Y"))
with ec2:
    sel_col = st.selectbox("Column (contract)", page_data["columns"], key="sel_col")
with ec3:
    st.write("")
    st.write("")
    if st.button("Open Cell ✏️"):
        st.session_state.editing_cell = (sel_date, sel_col)
        st.rerun()

# ── Delete row ────────────────────────────────────────────────────────────────
with st.expander("🗑️ Delete a Date Row"):
    del_date = st.selectbox("Select row to delete", sorted_dates, key="del_date",
                            format_func=lambda d: datetime.strptime(d, "%Y-%m-%d").strftime("%a, %b %d %Y"))
    if st.button("Delete Row", type="primary"):
        del page_data["rows"][del_date]
        save_data(db)
        st.rerun()
