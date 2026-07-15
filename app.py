"""
FILE MANAGER — a local-file utility with a sleek, modern dashboard.

Run with:
    streamlit run file_manager_app.py
"""

from pathlib import Path
from datetime import datetime
import pandas as pd
import streamlit as st

# ----------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="File Manager",
    page_icon="🗃️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state for 'page' if it doesn't exist
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# ----------------------------------------------------------------------
# Design tokens (Updated color palette for a modern look)
# ----------------------------------------------------------------------
BACKGROUND_COLOR = "#1E1E2F"
SIDEBAR_COLOR = "#2C2C3E"
PRIMARY_GRADIENT = ("#4E54C8", "#8F94FB")
SECONDARY_GRADIENT = ("#F7971E", "#FFD200")
ACCENT_COLOR = "#F4A261"
TEXT_COLOR = "#E0E0E0"
MUTED_COLOR = "#A0A0A0"
ERROR_COLOR = "#FF6B6B"

PAGES = {
    "Dashboard": {"emoji": "📊", "grad": PRIMARY_GRADIENT, "hex": PRIMARY_GRADIENT[1]},
    "Create":    {"emoji": "➕", "grad": SECONDARY_GRADIENT, "hex": SECONDARY_GRADIENT[1]},
    "Read":      {"emoji": "📖", "grad": ("#34D399", "#059669"), "hex": "#059669"},
    "Update":    {"emoji": "✏️", "grad": ("#F472B6", "#EC4899"), "hex": "#EC4899"},
    "Delete":    {"emoji": "🗑️", "grad": ("#EF4444", "#B91C1C"), "hex": "#B91C1C"},
}

EXT_COLORS = {
    ".txt": "#60A5FA", ".py": "#34D399", ".md": "#A78BFA", ".csv": "#FBBF24",
    ".json": "#F472B6", ".log": "#94A3B8", ".pdf": "#F87171", ".html": "#FB923C",
}
DEFAULT_EXT_COLOR = "#94A3B8"

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def hex_to_rgba(h, a):
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{a})"

def ext_color(ext):
    return EXT_COLORS.get(ext.lower(), DEFAULT_EXT_COLOR)

# ----------------------------------------------------------------------
# Global CSS (Updated for cleaner and modern look)
# ----------------------------------------------------------------------
st.markdown(
    f"""
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans&display=swap" rel="stylesheet">
    <style>
        body {{
            background-color: {BACKGROUND_COLOR};
            font-family: 'IBM Plex Sans', sans-serif;
            color: {TEXT_COLOR};
        }}
        [data-testid="stSidebar"] {{
            background-color: {SIDEBAR_COLOR};
            border-right: 1px solid {MUTED_COLOR};
        }}
        /* Sidebar Buttons */
        .stButton>button {{
            background-color: transparent;
            color: {TEXT_COLOR};
            border: 1px solid {MUTED_COLOR};
            border-radius: 8px;
            padding: 0.6rem 1rem;
            margin-bottom: 0.4rem;
            width: 100%;
            font-family: 'IBM Plex Mono', monospace;
            font-weight: 600;
            font-size: 0.9rem;
            transition: all 0.2s ease-in-out;
        }}
        .stButton>button:hover {{
            background-color: {ACCENT_COLOR};
            color: #fff;
            border-color: {ACCENT_COLOR};
        }}
        /* Hero Banner */
        .hero {{
            border-radius: 14px;
            padding: 2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 8px 24px rgba(0,0,0,0.2);
        }}
        .badge {{
            display:inline-flex; align-items:center; justify-content:center;
            width:52px; height:52px; border-radius:50%;
            background: rgba(255,255,255,0.2);
            font-size: 1.8rem; margin-bottom: 1rem;
            color: {TEXT_COLOR};
        }}
        .hero h1 {{
            font-family:'IBM Plex Mono', monospace;
            color: {TEXT_COLOR}; font-size: 2rem; margin: 0.3rem 0 0.2rem 0;
        }}
        .hero p {{
            color: rgba(255,255,255,0.8); margin:0; font-size: 1rem;
        }}
        /* Stat Cards */
        .stat {{
            border-radius: 12px;
            padding: 1.3rem;
            background-color: rgba(255,255,255,0.05);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }}
        .stat .label {{
            font-family:'IBM Plex Mono', monospace;
            font-size: 0.75rem; letter-spacing:0.08em;
            opacity: 0.8; margin-bottom: 0.4rem;
        }}
        .stat .value {{
            font-family:'IBM Plex Mono', monospace;
            font-size: 2rem; font-weight:700;
            color: {TEXT_COLOR};
        }}
        /* File Row */
        .filerow {{
            display:flex; justify-content:space-between; align-items:center;
            padding: 0.5rem 0.2rem; border-bottom: 1px solid {MUTED_COLOR};
            font-family:'IBM Plex Mono', monospace; font-size:0.85rem; color:{TEXT_COLOR};
        }}
        .tag {{
            padding: 2px 8px; border-radius: 20px; font-size: 0.75rem;
            font-family:'IBM Plex Mono', monospace; color: #fff; font-weight:700;
        }}
        /* Input Fields */
        .stTextInput>div>div>input, .stTextArea textarea {{
            background: {BACKGROUND_COLOR} !important; 
            color: {TEXT_COLOR} !important;
            border: 1px solid {MUTED_COLOR} !important; border-radius: 6px !important;
            font-family: 'IBM Plex Mono', monospace !important;
        }}
        label {{ color: {TEXT_COLOR} !important; }}
        /* Buttons */
        .stButton>button[kind="primary"] {{
            border: none !important; font-weight: 600;
            font-family:'IBM Plex Mono', monospace; border-radius: 8px;
            background-color: {ACCENT_COLOR}; color: #fff;
        }}
        .stButton>button[kind="primary"]:disabled {{
            background: {MUTED_COLOR} !important; color: {TEXT_COLOR};
        }}
        /* Caption and HR */
        [data-testid="stCaptionContainer"] {{ color: {MUTED_COLOR}; }}
        hr {{ border-color: {MUTED_COLOR}; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        f"""<div style="font-family:'IBM Plex Mono',monospace;font-size:1.35rem;font-weight:700;color:{TEXT_COLOR};margin-bottom:1.2rem;">🗃️ FILE MANAGER</div>""",
        unsafe_allow_html=True,
    )
    for name, meta_ in PAGES.items():
        if st.button(f"{meta_['emoji']}   {name}", key=f"nav_{name}", use_container_width=True):
            st.session_state.page = name

    st.markdown("<hr style='margin:1.2rem 0 0.9rem 0;'>", unsafe_allow_html=True)
    cwd = Path(".").resolve()
    st.markdown(
        f"<div style='font-family:\"IBM Plex Mono\",monospace;font-size:0.7rem;"
        f"color:{MUTED_COLOR};word-break:break-all;'>{cwd}</div>",
        unsafe_allow_html=True,
    )

# Get current page
page = st.session_state.page
meta = PAGES[page]
c1, c2 = meta["grad"]

# ----------------------------------------------------------------------
# Hero banner
# ----------------------------------------------------------------------
SUBS = {
    "Dashboard": "A quick overview of what's in your working folder.",
    "Create": "Start a brand new record in the working folder.",
    "Read": "Open a record and view its contents.",
    "Update": "Rename, append to, or overwrite an existing record.",
    "Delete": "Permanently remove a record from the folder.",
}
st.markdown(
    f"""
    <div class="hero" style="background:linear-gradient(135deg, {c1}, {c2});">
        <div class="badge">{meta['emoji']}</div>
        <h1>{page}</h1>
        <p>{SUBS[page]}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# PAGE CONTENT
# ----------------------------------------------------------------------
cwd = Path(".").resolve()

if page == "Dashboard":
    files = [p for p in cwd.iterdir() if p.is_file()]
    total_files = len(files)
    total_size = sum(p.stat().st_size for p in files)
    largest = max(files, key=lambda p: p.stat().st_size) if files else None
    ext_counts = {}
    for p in files:
        ext_counts[p.suffix or "(none)"] = ext_counts.get(p.suffix or "(none)", 0) + 1

    def fmt_size(n):
        if n < 1024:
            return f"{n} B"
        if n < 1024 ** 2:
            return f"{n / 1024:.1f} KB"
        return f"{n / (1024 ** 2):.1f} MB"

    stat_defs = [
        ("TOTAL FILES", str(total_files), "#3B82F6", "#2563EB"),
        ("TOTAL SIZE", fmt_size(total_size), "#10B981", "#059669"),
        ("LARGEST FILE", largest.name[:16] if largest else "—", "#8B5CF6", "#7C3AED"),
        ("FILE TYPES", str(len(ext_counts)), "#F59E0B", "#D97706"),
    ]
    cols = st.columns(4)
    for col, (label, value, g1, g2) in zip(cols, stat_defs):
        col.markdown(
            f"""<div class="stat" style="background:linear-gradient(135deg,{g1},{g2});">
            <div class="label">{label}</div><div class="value">{value}</div></div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([1.3, 1])

    with left:
        st.markdown(f"<div class='card' style='background:{BACKGROUND_COLOR};border:1px solid {MUTED_COLOR};border-radius:12px;padding:1rem;'>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='color:{TEXT_COLOR};font-family:\"IBM Plex Mono\",monospace;font-weight:600;margin-bottom:0.6rem;'>RECENT FILES</div>",
            unsafe_allow_html=True,
        )
        if files:
            recents = sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[:8]
            for p in recents:
                ext = p.suffix or "misc"
                color = ext_color(p.suffix)
                mtime = datetime.fromtimestamp(p.stat().st_mtime).strftime("%b %d, %H:%M")
                st.markdown(
                    f"""<div class="filerow">
                        <span>📄 {p.name}</span>
                        <span><span class="tag" style="background:{color};">{ext}</span>
                        &nbsp; <span style="color:{MUTED_COLOR};">{mtime}</span></span>
                    </div>""",
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No files yet — create one from the sidebar.")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown(f"<div class='card' style='background:{BACKGROUND_COLOR};border:1px solid {MUTED_COLOR};border-radius:12px;padding:1rem;'>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='color:{TEXT_COLOR};font-family:\"IBM Plex Mono\",monospace;font-weight:600;margin-bottom:0.6rem;'>FILE TYPE BREAKDOWN</div>",
            unsafe_allow_html=True,
        )
        if ext_counts:
            df = pd.DataFrame({"extension": list(ext_counts.keys()), "count": list(ext_counts.values())})
            df = df.set_index("extension")
            st.bar_chart(df, color=meta["hex"])
        else:
            st.caption("Nothing to chart yet.")
        st.markdown("</div>", unsafe_allow_html=True)

else:
    # For Create, Read, Update, Delete pages
    card_bg = hex_to_rgba(meta["hex"], 0.1)
    card_border = hex_to_rgba(meta["hex"], 0.4)
    st.markdown(
        f"<div class='card' style='background:{card_bg};border:1px solid {card_border};border-radius:12px;padding:1.2rem;'>",
        unsafe_allow_html=True,
    )

    if page == "Create":
        filename = st.text_input("File name", placeholder="example.txt")
        mode = st.radio("What do you want to do?", ["Just create an empty file", "Create and write content"])
        content = st.text_area("Content to write", height=150) if mode == "Create and write content" else ""

        if st.button("Create file", type="primary"):
            if not filename.strip():
                st.warning("Please enter a file name.")
            else:
                path = Path(filename)
                try:
                    if path.exists():
                        st.error(f"'{filename}' already exists.")
                    elif mode == "Just create an empty file":
                        with open(path, "x"):
                            pass
                        st.success(f"File **{filename}** created successfully.")
                    else:
                        with open(path, "w+") as f:
                            f.write(content)
                        st.success(f"File **{filename}** created and written successfully.")
                except Exception as err:
                    st.error(f"An error occurred: {err}")

    elif page == "Read":
        filename = st.text_input("File name", placeholder="example.txt")
        if st.button("Read file", type="primary"):
            if not filename.strip():
                st.warning("Please enter a file name.")
            else:
                path = Path(filename)
                try:
                    if not path.exists():
                        st.error("No such file exists.")
                    else:
                        with open(path, "r") as f:
                            data = f.read()
                        stat = path.stat()
                        st.success(f"Opened **{filename}**")
                        st.caption(
                            f"{stat.st_size} bytes · modified "
                            f"{datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')}"
                        )
                        st.code(data if data else "(file is empty)", language="text")
                except Exception as err:
                    st.error(f"An error occurred: {err}")

    elif page == "Update":
        filename = st.text_input("File name", placeholder="example.txt")
        update_choice = st.radio(
            "What do you want to do?",
            ["Rename the file", "Append to the file", "Overwrite the file"],
        )
        new_name = ""
        append_text = ""
        overwrite_text = ""

        if update_choice == "Rename the file":
            new_name = st.text_input("New file name", placeholder="new_example.txt")
        elif update_choice == "Append to the file":
            append_text = st.text_area("Text to append", height=120)
        else:
            overwrite_text = st.text_area("New content (replaces existing content)", height=150)

        if st.button("Apply update", type="primary"):
            if not filename.strip():
                st.warning("Please enter a file name.")
            else:
                path = Path(filename)
                try:
                    if not path.exists():
                        st.error(f"'{filename}' does not exist.")
                    elif update_choice == "Rename the file":
                        if not new_name.strip():
                            st.warning("Please enter a new file name.")
                        else:
                            new_path = Path(new_name)
                            if new_path.exists():
                                st.error(f"'{new_name}' already exists.")
                            else:
                                path.rename(new_name)
                                st.success(f"Renamed **{filename}** → **{new_name}** successfully.")
                    elif update_choice == "Append to the file":
                        with open(path, "a") as f:
                            f.write(" " + append_text)
                        st.success(f"Appended to **{filename}** successfully.")
                    else:
                        with open(path, "w") as f:
                            f.write(overwrite_text)
                        st.success(f"Overwrote **{filename}** successfully.")
                except Exception as err:
                    st.error(f"An error occurred: {err}")

    elif page == "Delete":
        filename = st.text_input("File name", placeholder="example.txt")
        confirm = st.checkbox("I understand this action cannot be undone.")
        if st.button("Delete file", type="primary", disabled=not confirm):
            if not filename.strip():
                st.warning("Please enter a file name.")
            else:
                path = Path(filename)
                try:
                    if not path.exists():
                        st.error("File doesn't exist.")
                    else:
                        path.unlink()
                        st.success(f"File **{filename}** deleted successfully.")
                except Exception as err:
                    st.error(f"An error occurred: {err}")

    st.markdown("</div>", unsafe_allow_html=True)

# Footer Note
st.markdown(
    f"<div style='color:{MUTED_COLOR};font-family:\"IBM Plex Mono\",monospace;"
    f"font-size:0.72rem;margin-top:1.3rem;'>FILE MANAGER · local utility · "
    f"operates on the folder the app is run from</div>",
    unsafe_allow_html=True,
)