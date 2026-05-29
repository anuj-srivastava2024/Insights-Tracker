import streamlit as st
import json
import os
from datetime import date, datetime

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

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)

if "db" not in st.session_state:
    st.session_state.db = load_data()
if "current_page" not in st.session_state:
    st.session_state.current_page = None
if "edits" not in st.session_state:
    st.session_state.edits = {}   # key "dstr__col" -> {"text":..,"tags":[..]}
if "has_unsaved" not in st.session_state:
    st.session_state.has_unsaved = False

db = st.session_state.db

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Sora:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Sora', sans-serif; }

section[data-testid="stSidebar"] { background:#0f172a; border-right:1px solid #1e293b; }
section[data-testid="stSidebar"] * { color:#e2e8f0 !important; }
section[data-testid="stSidebar"] .stButton button {
    background:#1e293b; border:1px solid #334155; color:#e2e8f0 !important;
    border-radius:6px; font-size:13px; width:100%; margin-bottom:4px;
}
section[data-testid="stSidebar"] .stButton button:hover { background:#334155; border-color:#6366f1; }

.main { background:#0f172a; }

/* col header box */
.col-header {
    background:#1e293b; color:#94a3b8;
    padding:8px 12px; border:1px solid #334155;
    font-family:'JetBrains Mono',monospace; font-size:11px;
    text-transform:uppercase; letter-spacing:.08em;
    text-align:center; border-radius:6px 6px 0 0;
    margin-bottom:2px;
}
.date-header {
    background:#1e293b; color:#6366f1;
    padding:10px 12px; border:1px solid #334155;
    font-family:'JetBrains Mono',monospace; font-size:12px;
    font-weight:600; border-radius:6px; white-space:nowrap;
    text-align:center;
}

/* tag pills */
.tag-pill {
    display:inline-block; padding:2px 9px; border-radius:20px;
    font-size:11px; font-weight:600; margin:2px 2px 2px 0;
    color:#fff; letter-spacing:.04em;
}

/* save banner */
.save-banner {
    background:#1e1b4b; border:1px solid #6366f1; border-radius:8px;
    padding:10px 16px; margin-bottom:14px; color:#a5b4fc; font-size:13px;
}

/* row separator */
.row-sep { border-top:1px solid #1e293b; margin:6px 0 10px; }

.stButton button {
    background:#1e293b !important; color:#e2e8f0 !important;
    border:1px solid #334155 !important; border-radius:6px !important;
}
.stButton button:hover { border-color:#6366f1 !important; background:#334155 !important; }


.stTextArea textarea {
    background:#111827 !important; color:#e2e8f0 !important;
    border-color:#334155 !important; font-size:13px !important;
    min-height:60px !important; overflow-y:hidden !important;
    resize:none !important; line-height:1.5 !important;
}
.stTextArea textarea:focus { border-color:#6366f1 !important; box-shadow:none !important; }
[data-testid="column"] { align-items:stretch; }

/* multiselect */
[data-baseweb="select"] { background:#111827 !important; }
[data-baseweb="tag"] { background:#334155 !important; color:#e2e8f0 !important; }

.page-title { font-size:26px; font-weight:700; color:#e2e8f0; letter-spacing:-.02em; margin-bottom:4px; }
.page-sub { font-size:12px; color:#475569; font-family:'JetBrains Mono',monospace; margin-bottom:16px; }

/* hide streamlit widget labels we don't need */
.hide-label label { display:none !important; }
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

# ── Universal Save Banner ─────────────────────────────────────────────────────
if st.session_state.has_unsaved:
    st.markdown(f'<div class="save-banner">⚠️ <b>{len(st.session_state.edits)}</b> unsaved cell(s) — hit <b>💾 Save All</b> when done.</div>', unsafe_allow_html=True)
    s1, s2 = st.columns([1, 1])
    with s1:
        if st.button("💾 Save All Changes", type="primary"):
            for key, val in st.session_state.edits.items():
                dstr, col = key.split("__", 1)
                if dstr not in page_data["rows"]:
                    page_data["rows"][dstr] = {}
                page_data["rows"][dstr][col] = val
            save_data(db)
            st.session_state.edits = {}
            st.session_state.has_unsaved = False
            st.success("✅ Saved!")
            st.rerun()
    with s2:
        if st.button("✖ Discard All"):
            st.session_state.edits = {}
            st.session_state.has_unsaved = False
            st.rerun()

# ── Manage Columns ────────────────────────────────────────────────────────────
with st.expander("⚙️ Manage Columns", expanded=len(page_data["columns"]) == 0):
    cu1, cu2 = st.columns([4, 1])
    with cu1:
        new_col = st.text_input("Contract / column name", placeholder="e.g. NQ Dec-24", key="new_col")
    with cu2:
        st.write(""); st.write("")
        if st.button("Add") and new_col.strip():
            cn = new_col.strip()
            if cn not in page_data["columns"]:
                page_data["columns"].append(cn)
                save_data(db)
                st.rerun()
    if page_data["columns"]:
        rc = st.selectbox("Remove column", ["—"] + page_data["columns"], key="remove_col")
        if st.button("Remove") and rc != "—":
            page_data["columns"].remove(rc)
            for rd in page_data["rows"].values():
                rd.pop(rc, None)
            save_data(db)
            st.rerun()

# ── Add Date Row ──────────────────────────────────────────────────────────────
with st.expander("➕ Add Date Row", expanded=False):
    dc1, dc2 = st.columns([3, 1])
    with dc1:
        chosen_date = st.date_input("Date", value=date.today(), key="date_picker")
    with dc2:
        st.write(""); st.write("")
        if st.button("Add Row"):
            dstr = str(chosen_date)
            if dstr not in page_data["rows"]:
                page_data["rows"][dstr] = {}
            save_data(db)
            st.rerun()

if not page_data["columns"]:
    st.info("Add at least one contract column above.")
    st.stop()

if not page_data["rows"]:
    st.info("Add a date row to begin entering observations.")
    st.stop()

# ── THE GRID ──────────────────────────────────────────────────────────────────
sorted_dates = sorted(page_data["rows"].keys())
cols_list = page_data["columns"]
N = len(cols_list)

# Column headers: date col + one per contract
# widths: date col is ~1.4 units, others equal
col_widths = [1.4] + [2] * N
header_cols = st.columns(col_widths)
header_cols[0].markdown('<div class="col-header">📅 Date</div>', unsafe_allow_html=True)
for i, col in enumerate(cols_list):
    header_cols[i + 1].markdown(f'<div class="col-header">{col}</div>', unsafe_allow_html=True)

st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)

# One row per date
for dstr in sorted_dates:
    row_data = page_data["rows"][dstr]
    try:
        d = datetime.strptime(dstr, "%Y-%m-%d")
        date_display = d.strftime("%a\n%b %d\n%Y")
    except:
        date_display = dstr

    row_cols = st.columns(col_widths)

    # Date cell
    with row_cols[0]:
        st.markdown(f'<div class="date-header">{date_display}</div>', unsafe_allow_html=True)

    # Data cells — each is a text area + multiselect tag picker
    for i, col in enumerate(cols_list):
        edit_key = f"{dstr}__{col}"
        # resolve current value: draft > saved
        if edit_key in st.session_state.edits:
            current = st.session_state.edits[edit_key]
        else:
            current = row_data.get(col, {"text": "", "tags": []})

        with row_cols[i + 1]:
            # Text area — directly editable
            new_text = st.text_area(
                label=edit_key,
                value=current.get("text", ""),
                key=f"txt_{edit_key}",
                placeholder="Write observation…",
                label_visibility="collapsed",
                height=100,
            )
            # Tag picker only — no separate preview (tags already show inside multiselect)
            new_tags = st.multiselect(
                label=f"tags_{edit_key}",
                options=list(TAGS.keys()),
                default=current.get("tags", []),
                key=f"tags_{edit_key}",
                label_visibility="collapsed",
                placeholder="Add tags…",
            )

        # Track changes into edits dict
        draft = {"text": new_text, "tags": new_tags}
        saved = row_data.get(col, {"text": "", "tags": []})
        if draft != saved:
            st.session_state.edits[edit_key] = draft
            st.session_state.has_unsaved = True
        elif edit_key in st.session_state.edits:
            # reverted to original — remove from edits
            del st.session_state.edits[edit_key]
            if not st.session_state.edits:
                st.session_state.has_unsaved = False

    # Row separator + delete button
    with st.expander("", expanded=False):
        if st.button(f"🗑 Delete row {dstr}", key=f"del_row_{dstr}"):
            del page_data["rows"][dstr]
            save_data(db)
            st.rerun()

    st.markdown('<div class="row-sep"></div>', unsafe_allow_html=True)

# ── Auto-resize textareas via JS ──────────────────────────────────────────────
st.markdown("""
<script>
function autoResize() {
    document.querySelectorAll('textarea').forEach(function(ta) {
        if (ta._autoResizeAttached) return;
        ta._autoResizeAttached = true;
        function resize() {
            ta.style.height = 'auto';
            ta.style.height = (ta.scrollHeight) + 'px';
        }
        ta.addEventListener('input', resize);
        resize();
    });
}
// Run on load and whenever Streamlit re-renders
const observer = new MutationObserver(autoResize);
observer.observe(document.body, { childList: true, subtree: true });
autoResize();
</script>
""", unsafe_allow_html=True)
