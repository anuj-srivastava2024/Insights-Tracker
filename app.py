import streamlit as st
import json
import os
from datetime import date, datetime

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Trade Contract Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = "data.json"

TAGS = {
    "Absorption":     "#6366f1",
    "Iceberg":        "#0ea5e9",
    "Tool":           "#f59e0b",
    "Extreme Delta":  "#ef4444",
    "Extreme Volume": "#8b5cf6",
    "Bullish":        "#22c55e",
    "Bearish":        "#f97316",
}

# ── Persistence ───────────────────────────────────────────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)

# ── Session state ─────────────────────────────────────────────────────────────
if "db" not in st.session_state:
    st.session_state.db = load_data()
if "current_page" not in st.session_state:
    st.session_state.current_page = None
# active_cell = (date_str, col) or None
if "active_cell" not in st.session_state:
    st.session_state.active_cell = None
# unsaved edits: { "date__col": {"text": ..., "tags": [...]} }
if "edits" not in st.session_state:
    st.session_state.edits = {}
if "has_unsaved" not in st.session_state:
    st.session_state.has_unsaved = False

db = st.session_state.db

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Sora:wght@300;400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Sora', sans-serif; }

section[data-testid="stSidebar"] { background: #0f172a; border-right: 1px solid #1e293b; }
section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
section[data-testid="stSidebar"] .stButton button {
    background: #1e293b; border: 1px solid #334155; color: #e2e8f0 !important;
    border-radius: 6px; font-size: 13px; text-align: left;
    width: 100%; margin-bottom: 4px; transition: all .15s;
}
section[data-testid="stSidebar"] .stButton button:hover { background: #334155; border-color: #6366f1; }

.main { background: #0f172a; }

/* ── tracker table ── */
.tracker-table { width: 100%; border-collapse: collapse; font-size: 13px; table-layout: auto; }
.tracker-table th {
    background: #1e293b; color: #94a3b8;
    padding: 10px 14px; border: 1px solid #334155;
    font-family: 'JetBrains Mono', monospace; font-size: 11px;
    text-transform: uppercase; letter-spacing: .08em;
    min-width: 160px; position: sticky; top: 0; z-index: 2;
}
.tracker-table td {
    border: 1px solid #1e293b; padding: 0;
    vertical-align: top; background: #0f172a;
    min-width: 160px;
}
.tracker-table td.date-cell {
    background: #1e293b; color: #6366f1;
    font-family: 'JetBrains Mono', monospace; font-size: 12px;
    font-weight: 600; white-space: nowrap; padding: 10px 14px;
    min-width: 170px;
}
.tracker-table tr:hover td { background: #0d1525; }
.tracker-table tr:hover td.date-cell { background: #1a2744; }

/* cell inner */
.cell-view {
    padding: 8px 12px; min-height: 44px; cursor: pointer;
    transition: background .12s;
}
.cell-view:hover { background: #1a2232 !important; }
.cell-view.active { background: #1e1b4b !important; border: none; outline: 2px solid #6366f1; outline-offset: -2px; }
.cell-placeholder { color: #334155; font-size: 12px; }

/* tags */
.tag-pill {
    display: inline-block; padding: 2px 9px; border-radius: 20px;
    font-size: 11px; font-weight: 600; margin: 2px 2px 2px 0;
    color: #fff; letter-spacing: .04em;
}

/* save banner */
.save-banner {
    background: #1e1b4b; border: 1px solid #6366f1;
    border-radius: 8px; padding: 10px 16px; margin-bottom: 14px;
    display: flex; align-items: center; gap: 12px;
    color: #a5b4fc; font-size: 13px;
}

/* buttons */
.stButton button {
    background: #1e293b !important; color: #e2e8f0 !important;
    border: 1px solid #334155 !important; border-radius: 6px !important;
}
.stButton button:hover { border-color: #6366f1 !important; background: #334155 !important; }

/* inputs */
.stTextInput input, .stTextArea textarea {
    background: #1e293b !important; color: #e2e8f0 !important; border-color: #334155 !important;
}

.page-title { font-size: 26px; font-weight: 700; color: #e2e8f0; letter-spacing: -.02em; margin-bottom: 4px; }
.page-sub { font-size: 12px; color: #475569; font-family: 'JetBrains Mono', monospace; margin-bottom: 16px; }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📊 Trade Tracker")
    st.markdown("---")

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
        st.caption("No pages yet.")
    for pg in list(db.keys()):
        c1, c2 = st.columns([4, 1])
        with c1:
            if st.button(f"📄 {pg}", key=f"nav_{pg}"):
                st.session_state.current_page = pg
                st.session_state.active_cell = None
                st.session_state.edits = {}
                st.session_state.has_unsaved = False
                st.rerun()
        with c2:
            if st.button("🗑", key=f"del_{pg}"):
                del db[pg]
                if st.session_state.current_page == pg:
                    st.session_state.current_page = next(iter(db), None)
                save_data(db)
                st.rerun()

    st.markdown("---")
    st.markdown("**Tag Legend**")
    for tag, color in TAGS.items():
        st.markdown(f'<span class="tag-pill" style="background:{color}">{tag}</span>', unsafe_allow_html=True)

# ── MAIN ──────────────────────────────────────────────────────────────────────
page = st.session_state.current_page

if page is None:
    st.markdown("""
    <div style="text-align:center;padding:80px 0;color:#475569;">
        <div style="font-size:52px;margin-bottom:16px;">📊</div>
        <div style="font-size:22px;font-weight:700;color:#94a3b8;margin-bottom:8px;">Trade Contract Tracker</div>
        <div style="font-size:14px;">Create a page from the sidebar to get started.</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

page_data = db[page]

st.markdown(f'<div class="page-title">📄 {page}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="page-sub">observation tracker • {len(page_data["rows"])} rows</div>', unsafe_allow_html=True)

# ── Universal Save button (shown when there are unsaved changes) ──────────────
if st.session_state.has_unsaved:
    sb1, sb2, sb3 = st.columns([2, 1, 6])
    with sb1:
        if st.button("💾 Save All Changes", type="primary"):
            # flush all edits into db
            for key, val in st.session_state.edits.items():
                dstr, col = key.split("__", 1)
                if dstr not in page_data["rows"]:
                    page_data["rows"][dstr] = {}
                page_data["rows"][dstr][col] = val
            save_data(db)
            st.session_state.edits = {}
            st.session_state.has_unsaved = False
            st.session_state.active_cell = None
            st.success("✅ All changes saved!")
            st.rerun()
    with sb2:
        if st.button("✖ Discard"):
            st.session_state.edits = {}
            st.session_state.has_unsaved = False
            st.session_state.active_cell = None
            st.rerun()
    st.markdown(f'<div class="save-banner">⚠️ You have <b>{len(st.session_state.edits)}</b> unsaved cell(s). Click <b>Save All Changes</b> when done editing.</div>', unsafe_allow_html=True)

# ── Column management ─────────────────────────────────────────────────────────
with st.expander("⚙️ Manage Columns", expanded=len(page_data["columns"]) == 0):
    cu1, cu2 = st.columns([4, 1])
    with cu1:
        new_col = st.text_input("Column name (contract)", placeholder="e.g. NQ Dec-24", key="new_col")
    with cu2:
        st.write(""); st.write("")
        if st.button("Add Column") and new_col.strip():
            col_name = new_col.strip()
            if col_name not in page_data["columns"]:
                page_data["columns"].append(col_name)
                save_data(db)
                st.rerun()
    if page_data["columns"]:
        remove_col = st.selectbox("Remove column", ["—"] + page_data["columns"], key="remove_col")
        if st.button("Remove") and remove_col != "—":
            page_data["columns"].remove(remove_col)
            for rd in page_data["rows"].values():
                rd.pop(remove_col, None)
            save_data(db)
            st.rerun()

# ── Add date row ──────────────────────────────────────────────────────────────
with st.expander("➕ Add Date Row", expanded=False):
    dc1, dc2 = st.columns([3, 1])
    with dc1:
        chosen_date = st.date_input("Pick a date", value=date.today(), key="date_picker")
    with dc2:
        st.write(""); st.write("")
        if st.button("Add Row"):
            dstr = str(chosen_date)
            if dstr not in page_data["rows"]:
                page_data["rows"][dstr] = {}
            save_data(db)
            st.rerun()

if not page_data["columns"]:
    st.info("Add at least one contract column above to start tracking.")
    st.stop()

if not page_data["rows"]:
    st.info("Add a date row to begin entering observations.")
    st.stop()

# ── Build interactive table ───────────────────────────────────────────────────
sorted_dates = sorted(page_data["rows"].keys())
active = st.session_state.active_cell   # (dstr, col) or None

# Header row
header_html = '<th>📅 Date</th>' + "".join(f"<th>{c}</th>" for c in page_data["columns"])

# We render the table as HTML for display, but place Streamlit widgets
# for the active cell inline using st.columns layout below the table.

table_rows_html = ""
for dstr in sorted_dates:
    row_data = page_data["rows"][dstr]
    try:
        d = datetime.strptime(dstr, "%Y-%m-%d")
        date_display = d.strftime("%a, %b %d %Y")
    except:
        date_display = dstr

    row_cells = f'<td class="date-cell">📅 {date_display}</td>'
    for col in page_data["columns"]:
        edit_key = f"{dstr}__{col}"
        # Use edited value if exists, else db value
        if edit_key in st.session_state.edits:
            cell = st.session_state.edits[edit_key]
        else:
            cell = row_data.get(col, {"text": "", "tags": []})

        text = cell.get("text", "")
        tags = cell.get("tags", [])
        is_active = (active == (dstr, col))

        tags_html = "".join(
            f'<span class="tag-pill" style="background:{TAGS.get(t,"#555")}">{t}</span>'
            for t in tags
        )
        if tags or text:
            content_inner = f"{tags_html}<div style='margin-top:4px;color:#cbd5e1;font-size:13px;white-space:pre-wrap'>{text}</div>"
        else:
            content_inner = '<span class="cell-placeholder">click to edit</span>'

        active_class = "active" if is_active else ""
        row_cells += f'<td><div class="cell-view {active_class}">{content_inner}</div></td>'

    table_rows_html += f"<tr>{row_cells}</tr>"

st.markdown(f"""
<div style="overflow-x:auto;border-radius:10px;border:1px solid #1e293b;margin-bottom:4px;">
<table class="tracker-table">
  <thead><tr>{header_html}</tr></thead>
  <tbody>{table_rows_html}</tbody>
</table>
</div>
""", unsafe_allow_html=True)

# ── Click selector — replaces "double click" in Streamlit ────────────────────
st.markdown("<div style='font-size:12px;color:#475569;margin-bottom:6px;'>👆 Click a cell to edit — select the row & column below</div>", unsafe_allow_html=True)

sel_cols = st.columns([2, 2, 1])
with sel_cols[0]:
    sel_date = st.selectbox(
        "Row (date)", sorted_dates, key="sel_date",
        format_func=lambda d: datetime.strptime(d, "%Y-%m-%d").strftime("%a, %b %d %Y"),
        label_visibility="collapsed"
    )
with sel_cols[1]:
    sel_col = st.selectbox("Column", page_data["columns"], key="sel_col", label_visibility="collapsed")
with sel_cols[2]:
    if st.button("✏️ Open"):
        st.session_state.active_cell = (sel_date, sel_col)
        st.rerun()

# ── Inline cell editor (appears when a cell is active) ───────────────────────
if active:
    adate, acol = active
    edit_key = f"{adate}__{acol}"

    # Pull current value: edited draft > db
    if edit_key in st.session_state.edits:
        current = st.session_state.edits[edit_key]
    else:
        current = page_data["rows"].get(adate, {}).get(acol, {"text": "", "tags": []})

    try:
        d = datetime.strptime(adate, "%Y-%m-%d")
        cell_label = d.strftime("%a, %b %d %Y")
    except:
        cell_label = adate

    st.markdown(f"<div style='margin:12px 0 6px;font-size:13px;color:#a5b4fc;font-weight:600;'>✏️ Editing: <code>{cell_label}</code> × <b>{acol}</b></div>", unsafe_allow_html=True)

    ec1, ec2 = st.columns([3, 2])
    with ec1:
        new_text = st.text_area(
            "Notes", value=current.get("text", ""),
            height=110, key=f"edit_text_{edit_key}",
            placeholder="Type your observation here…",
            label_visibility="collapsed"
        )
    with ec2:
        new_tags = st.multiselect(
            "Tags", options=list(TAGS.keys()),
            default=current.get("tags", []),
            key=f"edit_tags_{edit_key}",
            label_visibility="collapsed"
        )
        # preview tags
        if new_tags:
            st.markdown("".join(
                f'<span class="tag-pill" style="background:{TAGS[t]}">{t}</span>'
                for t in new_tags
            ), unsafe_allow_html=True)

    # Update draft in real time (on any widget interaction Streamlit reruns)
    draft = {"text": new_text, "tags": new_tags}
    if draft != current:
        st.session_state.edits[edit_key] = draft
        st.session_state.has_unsaved = True

    btn1, btn2 = st.columns([1, 8])
    with btn1:
        if st.button("Close ✖"):
            st.session_state.active_cell = None
            st.rerun()

st.markdown("---")

# ── Delete row ────────────────────────────────────────────────────────────────
with st.expander("🗑️ Delete a Date Row"):
    del_date = st.selectbox(
        "Select row", sorted_dates, key="del_date",
        format_func=lambda d: datetime.strptime(d, "%Y-%m-%d").strftime("%a, %b %d %Y")
    )
    if st.button("Delete Row", type="primary"):
        del page_data["rows"][del_date]
        save_data(db)
        st.rerun()
