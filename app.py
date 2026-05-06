import os
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px
import streamlit as st

try:
    from groq import Groq
except Exception:
    Groq = None

load_dotenv()

# ── New feature modules ──────────────────────────────────────────────────
from module_export import render_export_page
from module_roi import render_roi_page
from module_copilot import render_copilot_page

st.set_page_config(
    page_title="Inventory Control Tower",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

TODAY = pd.Timestamp("2026-05-05")
PASSWORD = "TP2Balt"  

def check_password():
    def password_entered():
        if st.session_state["password"] == PASSWORD:
            st.session_state["authenticated"] = True
        else:
            st.session_state["authenticated"] = False

    if "authenticated" not in st.session_state:
        st.text_input("Enter Password", type="password", key="password", on_change=password_entered)
        return False
    elif not st.session_state["authenticated"]:
        st.text_input("Enter Password", type="password", key="password", on_change=password_entered)
        st.error("Incorrect password")
        return False
    else:
        return True

if not check_password():
    st.stop()
# -----------------------------
# CSS
# -----------------------------
st.markdown(
    """
<style>
.stApp {
    background: #f4f7fb;
    color: #111827;
}
.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
}
[data-testid="stSidebar"] {
    background: #0b1f3a;
}
[data-testid="stSidebar"] * {
    color: #ffffff !important;
}
h1, h2, h3, h4, h5, h6, p, span, div, label {
    color: #111827;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div {
    color: #ffffff !important;
}
.hero {
   background: linear-gradient(
    135deg,
    #16213E 0%,
    #1A4B84 55%,
    #4EA8DE 100%
);
    padding: 30px;
    border-radius: 24px;
    margin-bottom: 22px;
    box-shadow: 0 12px 28px rgba(11,31,58,0.22);
}
.hero h1 {
    color: #ffffff;
    font-size: 36px;
    margin: 0;
    font-weight: 900;
}
.hero p {
    color: #dbeafe;
    font-size: 15px;
    margin-top: 8px;
    max-width: 950px;
}


.card {
    background: #ffffff;
    border: 1px solid #dbe3ef;
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 8px 24px rgba(16,24,40,0.06);
    margin-bottom: 16px;
}
.card h3, .card h4 {
    color: #0b1f3a;
    margin-top: 0;
}
.card p {
    color: #374151;
}
.kpi {
    background: #ffffff;
    border: 1px solid #dbe3ef;
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 8px 22px rgba(16,24,40,0.05);
    min-height: 125px;
}
.kpi-label {
    font-size: 12px;
    color: #64748b;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: .04em;
}
.kpi-value {
    font-size: 29px;
    color: #0b1f3a;
    font-weight: 900;
    margin-top: 8px;
}
.kpi-sub {
    font-size: 12px;
    color: #64748b;
    margin-top: 6px;
}
.info-box {
    background: #eef6ff;
    border: 1px solid #bfdbfe;
    border-left: 5px solid #1f6fb2;
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 14px;
}
.info-box h4 {
    color: #0b1f3a;
    margin: 0 0 6px 0;
}
.info-box p {
    color: #334155;
    margin: 0;
}
.badge-critical {
    background:#fee2e2;
    color:#991b1b;
    padding:6px 12px;
    border-radius:999px;
    font-weight:800;
    font-size:12px;
}
.badge-high {
    background:#ffedd5;
    color:#9a3412;
    padding:6px 12px;
    border-radius:999px;
    font-weight:800;
    font-size:12px;
}
.badge-medium {
    background:#dbeafe;
    color:#1e40af;
    padding:6px 12px;
    border-radius:999px;
    font-weight:800;
    font-size:12px;
}
.badge-low {
    background:#dcfce7;
    color:#166534;
    padding:6px 12px;
    border-radius:999px;
    font-weight:800;
    font-size:12px;
}
.badge-blocked {
    background:#ede9fe;
    color:#5b21b6;
    padding:6px 12px;
    border-radius:999px;
    font-weight:800;
    font-size:12px;
}
.section-title {
    color: #0b1f3a;
    font-weight: 900;
    font-size: 23px;
    margin-top: 12px;
    margin-bottom: 10px;
}
.small-muted {
    color: #64748b;
    font-size: 13px;
}
.stButton > button {
    border-radius: 12px;
    border: 1px solid #1f6fb2;
    background: #1f6fb2;
    color: white;
    font-weight: 700;
}
.stButton > button:hover {
    background: #155a94;
    border-color: #155a94;
    color: white;
}
div[data-testid="stDataFrame"] {
    background: white;
    border-radius: 16px;
}
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# DATA
# -----------------------------
inventory = [
    ["Germany","Berlin Neuro Center","Hospital","Optima Coil","Aneurysm Treatment","COIL-XL-18","OC-2401","2026-06-30",120,3000,18,"Internal","EU","Clear","Yes",52.5200,13.4050],
    ["Germany","Munich Stroke Hospital","Hospital","Optima Coil","Aneurysm Treatment","COIL-XL-18","OC-2401","2026-06-30",60,3000,10,"Internal","EU","Clear","Yes",48.1351,11.5820],
    ["Spain","Madrid Neuro Hospital","Hospital","Optima Coil","Aneurysm Treatment","COIL-XL-18","OC-2403","2027-12-31",15,3000,45,"Internal","EU","Clear","Yes",40.4168,-3.7038],
    ["Spain","Barcelona Vascular Institute","Hospital","Optima Coil","Aneurysm Treatment","COIL-XL-18","OC-2403","2027-12-31",20,3000,30,"Internal","EU","Clear","Yes",41.3851,2.1734],
    ["France","Lyon Hospital","Hospital","Squid Liquid Embolic","Embolization","SQUID-12","SQ-778","2026-08-15",90,4500,12,"Internal","EU","Clear","Yes",45.7640,4.8357],
    ["Italy","Milan Distributor","Distributor","Squid Liquid Embolic","Embolization","SQUID-12","SQ-778","2026-08-15",200,4500,25,"Distributor","EU","Clear","Conditional",45.4642,9.1900],
    ["France","Paris Warehouse","Warehouse","Optima Coil","Aneurysm Treatment","COIL-XL-18","OC-2405","2027-12-31",350,3000,0,"Internal","EU","Clear","Yes",48.8566,2.3522],
    ["Germany","Frankfurt Warehouse","Warehouse","Eclipse 2L Balloon","Balloon / Remodeling","ECL-2L","EB-992","2026-11-01",180,2200,22,"Internal","EU","Clear","Yes",50.1109,8.6821],
    ["US","Boston Neuro Center","Hospital","Hybrid Guidewire","Access Devices","HYB-GW-14","HG-510","2026-09-20",140,900,65,"Internal","US","Clear","Yes",42.3601,-71.0589],
    ["US","Chicago Stroke Institute","Hospital","Mega Ballast Access Platform","Access Devices","MB-DAP-90","MB-880","2027-01-15",80,1800,20,"Internal","US","Quality Hold","No",41.8781,-87.6298],
]

cols = [
    "Region","Location","Type","Product","Product Family","SKU","Batch","Expiry",
    "Qty","Unit Value","Monthly Usage","Owner","Regulatory Zone","Recall Status",
    "Transfer Allowed","Latitude","Longitude"
]

demand = [
    ["Madrid Neuro Hospital","Spain","COIL-XL-18","Optima Coil",70,0.82,"Procedure trend + low stock","High"],
    ["Barcelona Vascular Institute","Spain","COIL-XL-18","Optima Coil",40,0.76,"Sales velocity + tender demand","High"],
    ["Rome Neuro Hospital","Italy","SQUID-12","Squid Liquid Embolic",60,0.68,"Distributor signal","Medium"],
    ["Lyon Hospital","France","SQUID-12","Squid Liquid Embolic",20,0.55,"Historical usage","Medium"],
    ["Boston Neuro Center","US","HYB-GW-14","Hybrid Guidewire",130,0.88,"High procedure throughput","High"],
]

demand_cols = [
    "Location","Region","SKU","Product","Expected Demand 60D",
    "Confidence","Signal","Urgency"
]

df = pd.DataFrame(inventory, columns=cols)
demand_df = pd.DataFrame(demand, columns=demand_cols)

df["Expiry"] = pd.to_datetime(df["Expiry"])
df["Days to Expiry"] = (df["Expiry"] - TODAY).dt.days
df["Months Remaining"] = (df["Days to Expiry"] / 30).clip(lower=0)
df["Expected Usage Before Expiry"] = (df["Monthly Usage"] * df["Months Remaining"]).round(0)
df["Safety Stock"] = (df["Monthly Usage"] * 0.5).round(0)
df["At Risk Qty"] = (df["Qty"] - df["Expected Usage Before Expiry"] - df["Safety Stock"]).clip(lower=0).round(0)
df["Inventory Value"] = df["Qty"] * df["Unit Value"]
df["Value at Risk"] = df["At Risk Qty"] * df["Unit Value"]
df["Usable Inventory Score"] = (100 - (df["At Risk Qty"] / df["Qty"].replace(0,1) * 100)).clip(lower=0).round(1)

def risk_level(row):
    if row["Recall Status"] != "Clear":
        return "Blocked"
    if row["Value at Risk"] > 250000 and row["Days to Expiry"] < 100:
        return "Critical"
    if row["Value at Risk"] > 150000:
        return "High"
    if row["Value at Risk"] > 50000:
        return "Medium"
    return "Low"

df["Risk Level"] = df.apply(risk_level, axis=1)

# -----------------------------
# HELPERS
# -----------------------------
def euro(x):
    return f"€{x:,.0f}"

def kpi(label, value, sub=""):
    st.markdown(
        f"""
<div class="kpi">
    <div class="kpi-label">{label}</div>
    <div class="kpi-value">{value}</div>
    <div class="kpi-sub">{sub}</div>
</div>
""",
        unsafe_allow_html=True,
    )

def badge(level):
    cls = {
        "Critical": "badge-critical",
        "High": "badge-high",
        "Medium": "badge-medium",
        "Low": "badge-low",
        "Blocked": "badge-blocked",
    }.get(level, "badge-low")
    return f'<span class="{cls}">{level}</span>'

def searchable_table(dataframe, columns, search_key, title=None):
    if dataframe.empty:
        st.info("No records available.")
        return

    if title:
        st.markdown(f"### {title}")

    search = st.text_input(
        "Search table",
        placeholder="Search by location, product, batch, SKU, region, action",
        key=search_key,
    )

    table_df = dataframe.copy()

    if search:
        table_df = table_df[
            table_df.apply(
                lambda r: search.lower() in " ".join(map(str, r.values)).lower(),
                axis=1,
            )
        ]

    if table_df.empty:
        st.warning("No matching records found.")
    else:
        st.dataframe(
            table_df[columns],
            use_container_width=True,
            hide_index=True,
        )

def make_recommendations(inv, dem):
    rows = []
    risky = inv[
        (inv["At Risk Qty"] > 0)
        & (inv["Recall Status"] == "Clear")
        & (inv["Transfer Allowed"].isin(["Yes","Conditional"]))
    ]

    for _, s in risky.iterrows():
        matches = dem[dem["SKU"] == s["SKU"]]
        for _, d in matches.iterrows():
            if d["Location"] == s["Location"]:
                continue

            qty = int(min(s["At Risk Qty"], d["Expected Demand 60D"]))
            if qty <= 0:
                continue

            logistics = 6800 if s["Region"] != d["Region"] else 3200
            if s["Owner"] == "Distributor":
                logistics += 5000

            gross = qty * s["Unit Value"]
            net = gross - logistics
            confidence = round((d["Confidence"] * 100) - (5 if s["Owner"] == "Distributor" else 0), 1)

            rows.append({
                "From": s["Location"],
                "To": d["Location"],
                "Product": s["Product"],
                "SKU": s["SKU"],
                "Batch": s["Batch"],
                "Qty": qty,
                "Gross Value Saved": gross,
                "Logistics Cost": logistics,
                "Net Value Saved": net,
                "Confidence": confidence,
                "Compliance": "Eligible" if s["Regulatory Zone"] == "EU" else "Region Review",
                "Priority": "High" if net > 150000 and confidence > 70 else "Medium",
                "Reason": f"{s['Location']} has {int(s['At Risk Qty'])} units at risk. {d['Location']} has {int(d['Expected Demand 60D'])} units expected demand."
            })

    rec = pd.DataFrame(rows)
    if not rec.empty:
        rec = rec.sort_values(["Net Value Saved","Confidence"], ascending=False).reset_index(drop=True)
    return rec

rec_df = make_recommendations(df, demand_df)

# -----------------------------
# SIDEBAR
# -----------------------------
with st.sidebar:
    st.markdown("## Control Tower")
    st.caption("Enterprise inventory intelligence")

    page = st.radio(
        "Navigation",
        [
            "Executive Overview",
            "Global Search and Investigation",
            "Persona Workspaces",
            "Scenario Simulator",
            "AI Copilot",
            "ROI Calculator",
            "Executive Export",
        ],
    )

    st.markdown("---")

    region_filter = st.multiselect(
        "Region",
        sorted(df["Region"].unique()),
        default=sorted(df["Region"].unique()),
    )

    product_filter = st.multiselect(
        "Product",
        sorted(df["Product"].unique()),
        default=sorted(df["Product"].unique()),
    )

    risk_filter = st.multiselect(
        "Risk Level",
        ["Critical", "High", "Medium", "Low", "Blocked"],
        default=["Critical", "High", "Medium", "Low", "Blocked"],
    )

fdf = df[
    df["Region"].isin(region_filter)
    & df["Product"].isin(product_filter)
    & df["Risk Level"].isin(risk_filter)
].copy()

# -----------------------------
# HEADER
# -----------------------------
st.markdown(
    """
<div class="hero">
    <h1>Inventory Control Tower</h1>
    <p>
    An expiry-aware, demand-matched and compliance-ready intelligence layer for high-value neurovascular inventory across hospitals, distributors and warehouses.
    </p>
</div>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# SECTION TITLE WITH INFO TOOLTIP
# -----------------------------
def section_title_with_info(title, info, level=3):
    tag = "h3" if level == 3 else "h2"
    st.markdown(
        f"""
<style>
.info-section-line {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 16px;
    margin-bottom: 8px;
}}
.info-section-line h2,
.info-section-line h3 {{
    margin: 0;
    color: #0b1f3a;
    font-weight: 900;
}}
.info-wrap {{
    position: relative;
    display: inline-block;
}}
.info-icon {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 19px;
    height: 19px;
    border-radius: 50%;
    background: #e8f1fb;
    color: #1f6fb2;
    font-size: 12px;
    font-weight: 900;
    border: 1px solid #b8d4f2;
    cursor: help;
}}
.info-tooltip {{
    visibility: hidden;
    opacity: 0;
    width: 360px;
    background: #0b1f3a;
    color: #ffffff !important;
    text-align: left;
    border-radius: 10px;
    padding: 11px 13px;
    position: absolute;
    z-index: 9999;
    top: 26px;
    left: 0;
    font-size: 13px;
    line-height: 1.45;
    box-shadow: 0 10px 24px rgba(0,0,0,0.18);
    transition: opacity 0.2s ease;
}}
.info-wrap:hover .info-tooltip {{
    visibility: visible;
    opacity: 1;
}}
</style>
<div class="info-section-line">
    <{tag}>{title}</{tag}>
    <span class="info-wrap">
        <span class="info-icon">i</span>
        <span class="info-tooltip">{info}</span>
    </span>
</div>
""",
        unsafe_allow_html=True,
    )

# -----------------------------
# EXECUTIVE OVERVIEW
# -----------------------------
def executive_overview():
    risk = fdf["Value at Risk"].sum()
    recoverable = rec_df["Net Value Saved"].sum() if not rec_df.empty else 0
    actions = len(rec_df)
    blocked = len(fdf[fdf["Risk Level"] == "Blocked"])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi("Inventory Value at Risk", euro(risk), "Potential expiry or aging exposure")
    with c2:
        kpi("Recoverable Value", euro(recoverable), "Through recommended redistribution")
    with c3:
        kpi("Recommended Actions", actions, "Transfers, reviews and deferrals")
    with c4:
        kpi("Blocked Batches", blocked, "Quality or compliance restriction")

    st.markdown('<div class="section-title">What the system has identified</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            """
<div class="info-box">
    <h4>Aging inventory detected</h4>
    <p>Some high-value batches are unlikely to be consumed before expiry based on current usage patterns.</p>
</div>
""",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
<div class="info-box">
    <h4>Demand exists elsewhere</h4>
    <p>Other hospitals show strong expected demand for the same SKU within the next 60 days.</p>
</div>
""",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
<div class="info-box">
    <h4>Redistribution can protect value</h4>
    <p>The system recommends compliant transfers that reduce expiry losses and defer new production.</p>
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-title">Global Risk Map</div>', unsafe_allow_html=True)

    map_df = fdf.copy()
    map_df["Bubble"] = (map_df["Value at Risk"] / 10000).clip(lower=8, upper=45)

    fig = px.scatter_mapbox(
        map_df,
        lat="Latitude",
        lon="Longitude",
        size="Bubble",
        color="Risk Level",
        hover_name="Location",
        hover_data={
            "Product": True,
            "Batch": True,
            "Qty": True,
            "At Risk Qty": True,
            "Value at Risk": ":,.0f",
            "Days to Expiry": True,
            "Bubble": False,
            "Latitude": False,
            "Longitude": False,
        },
        mapbox_style="carto-positron",
        zoom=2.1,
        height=460,
        color_discrete_map={
            "Critical":"#d92d20",
            "High":"#f79009",
            "Medium":"#2e90fa",
            "Low":"#12b76a",
            "Blocked":"#7a271a",
        },
    )
    fig.update_layout(
        margin=dict(l=0,r=0,t=0,b=0),
        paper_bgcolor="#ffffff",
        font_color="#111827",
    )
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns([1.1, 1])
    with c1:
        st.markdown("### Product-Level Exposure")
        risk_product = (
            fdf.groupby("Product", as_index=False)["Value at Risk"]
            .sum()
            .sort_values("Value at Risk", ascending=False)
        )
        fig = px.bar(
            risk_product,
            x="Product",
            y="Value at Risk",
            text="Value at Risk",
            height=360,
            color_discrete_sequence=["#1f6fb2"],
        )
        fig.update_traces(texttemplate="€%{text:,.0f}", textposition="outside")
        fig.update_layout(
            xaxis_title="",
            yaxis_title="Value at Risk",
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font_color="#111827",
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("### Inventory Health Mix")
        mix = fdf.groupby("Risk Level", as_index=False)["Inventory Value"].sum()
        fig = px.pie(
            mix,
            values="Inventory Value",
            names="Risk Level",
            hole=0.55,
            height=360,
            color="Risk Level",
            color_discrete_map={
                "Critical":"#d92d20",
                "High":"#f79009",
                "Medium":"#2e90fa",
                "Low":"#12b76a",
                "Blocked":"#7a271a",
            },
        )
        fig.update_layout(
            paper_bgcolor="#ffffff",
            font_color="#111827",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">Top Recommendations</div>', unsafe_allow_html=True)
    if rec_df.empty:
        st.info("No recommendation available.")
    else:
        best = rec_df.iloc[0]
        st.markdown(
            f"""
<div class="card">
    <h3>Recommended priority action</h3>
    <p>Transfer <b>{best['Qty']} units</b> of <b>{best['Product']}</b> batch <b>{best['Batch']}</b> from <b>{best['From']}</b> to <b>{best['To']}</b>.</p>
    <p><b>Net value saved:</b> {euro(best['Net Value Saved'])} | <b>Confidence:</b> {best['Confidence']}% | <b>Compliance:</b> {best['Compliance']}</p>
    <p>{best['Reason']}</p>
</div>
""",
            unsafe_allow_html=True,
        )

        searchable_table(
            rec_df,
            [
                "From","To","Product","Batch","Qty",
                "Net Value Saved","Confidence","Compliance","Priority"
            ],
            search_key="executive_top_recommendations_search",
            title="All Recommended Actions",
        )

# -----------------------------
# GLOBAL SEARCH + INVESTIGATION
# -----------------------------
def global_search_component():
    st.markdown('<div class="section-title">Global Inventory Search</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="small-muted">Search by location, product, SKU, batch, region, owner or inventory type.</p>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        type_filter = st.multiselect(
            "Filter by Type",
            options=sorted(fdf["Type"].unique()),
            default=sorted(fdf["Type"].unique()),
            key="gs_type_filter",
        )
    with c2:
        rl_filter = st.multiselect(
            "Filter by Risk Level",
            options=["Critical", "High", "Medium", "Low", "Blocked"],
            default=["Critical", "High", "Medium", "Low", "Blocked"],
            key="gs_risk_filter",
        )
    with c3:
        transfer_filter = st.multiselect(
            "Transfer Allowed",
            options=sorted(fdf["Transfer Allowed"].unique()),
            default=sorted(fdf["Transfer Allowed"].unique()),
            key="gs_transfer_filter",
        )

    search_query = st.text_input(
        "Search inventory",
        placeholder="Example: Berlin, OC-2401, Optima Coil, SQUID-12",
        label_visibility="visible",
        key="gs_text_search",
    )

    results = fdf[
        fdf["Type"].isin(type_filter)
        & fdf["Risk Level"].isin(rl_filter)
        & fdf["Transfer Allowed"].isin(transfer_filter)
    ].copy()

    if search_query:
        results = results[
            results.apply(lambda r: search_query.lower() in " ".join(map(str, r.values)).lower(), axis=1)
        ]

    if results.empty:
        st.warning("No matching inventory records found.")
        return None

    st.dataframe(
        results[
            [
                "Region","Location","Type","Product","SKU","Batch","Expiry","Qty",
                "At Risk Qty","Value at Risk","Risk Level","Transfer Allowed","Recall Status"
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    options = results["Location"] + " | " + results["Product"] + " | " + results["Batch"]
    selected = st.selectbox("Select any record to investigate", options)
    row = results[options == selected].iloc[0]
    return row

def investigation_panel(row):
    st.markdown('<div class="section-title">Selected Inventory Intelligence View</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi("Current Stock", f"{int(row['Qty'])}", "Units available")
    with c2:
        kpi("At-Risk Qty", f"{int(row['At Risk Qty'])}", "Likely unused before expiry")
    with c3:
        kpi("Value at Risk", euro(row["Value at Risk"]), "Potential financial exposure")
    with c4:
        kpi("Days to Expiry", f"{int(row['Days to Expiry'])}", "Decision window")

    risk_badge = badge(row["Risk Level"])

    st.markdown(
        f"""
<div class="card">
    <h3>{row['Product']} | Batch {row['Batch']}</h3>
    <p><b>Location:</b> {row['Location']} | <b>Region:</b> {row['Region']} | <b>Type:</b> {row['Type']}</p>
    <p><b>SKU:</b> {row['SKU']} | <b>Product Family:</b> {row['Product Family']}</p>
    <p><b>Expiry:</b> {row['Expiry'].date()} | <b>Monthly Usage:</b> {int(row['Monthly Usage'])} | <b>Expected Usage Before Expiry:</b> {int(row['Expected Usage Before Expiry'])}</p>
    <p><b>Safety Stock:</b> {int(row['Safety Stock'])} | <b>Usable Inventory Score:</b> {row['Usable Inventory Score']}%</p>
    <p><b>Owner:</b> {row['Owner']} | <b>Transfer Allowed:</b> {row['Transfer Allowed']} | <b>Regulatory Zone:</b> {row['Regulatory Zone']} | <b>Quality Status:</b> {row['Recall Status']}</p>
    <p><b>Risk Level:</b> {risk_badge}</p>
</div>
""",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([1, 1])

    with c1:
        st.markdown("### Why this is at risk")
        risk_bridge = pd.DataFrame({
            "Metric": ["Current Stock", "Expected Usage", "Safety Stock", "At-Risk Qty"],
            "Quantity": [
                row["Qty"],
                row["Expected Usage Before Expiry"],
                row["Safety Stock"],
                row["At Risk Qty"]
            ],
        })
        fig = px.bar(
            risk_bridge,
            x="Metric",
            y="Quantity",
            text="Quantity",
            height=360,
            color_discrete_sequence=["#1f6fb2"],
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font_color="#111827",
            xaxis_title="",
            yaxis_title="Units",
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("### Matching Demand")
        matches = demand_df[demand_df["SKU"] == row["SKU"]].copy()

        if matches.empty:
            st.info("No demand signal found for this SKU.")
        else:
            st.dataframe(matches, use_container_width=True, hide_index=True)

            fig = px.scatter(
                matches,
                x="Expected Demand 60D",
                y="Confidence",
                size="Expected Demand 60D",
                color="Urgency",
                hover_name="Location",
                height=300,
                color_discrete_map={
                    "High": "#d92d20",
                    "Medium": "#f79009",
                    "Low": "#12b76a",
                },
            )
            fig.update_layout(
                paper_bgcolor="#ffffff",
                plot_bgcolor="#ffffff",
                font_color="#111827",
                yaxis_tickformat=".0%",
            )
            st.plotly_chart(fig, use_container_width=True)

    item_recs = pd.DataFrame()
    if not rec_df.empty:
        item_recs = rec_df[
            (rec_df["Batch"] == row["Batch"])
            & (rec_df["From"] == row["Location"])
        ]

    st.markdown("### Recommended Actions for Selected Item")
    if item_recs.empty:
        st.info("No redistribution recommendation available for this selected record.")
    else:
        searchable_table(
            item_recs,
            [
                "From","To","Product","Batch","Qty","Net Value Saved",
                "Confidence","Compliance","Priority","Reason"
            ],
            search_key=f"selected_item_recs_{row['Location']}_{row['Batch']}",
            title=None,
        )

        best = item_recs.iloc[0]
        st.markdown(
            f"""
<div class="info-box">
    <h4>Best Recommended Action</h4>
    <p>Transfer <b>{best['Qty']} units</b> of <b>{best['Product']}</b> batch <b>{best['Batch']}</b> from <b>{best['From']}</b> to <b>{best['To']}</b>. Estimated net value saved: <b>{euro(best['Net Value Saved'])}</b>.</p>
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown("### If No Action Is Taken")
    recoverable = item_recs["Net Value Saved"].sum() if not item_recs.empty else 0
    c1, c2 = st.columns(2)
    with c1:
        kpi("Potential Loss", euro(row["Value at Risk"]), "Estimated exposure if no action is taken")
    with c2:
        kpi("Recoverable Value", euro(recoverable), "Estimated value saved through recommended action")

def search_and_investigation():
    row = global_search_component()
    if row is not None:
        investigation_panel(row)

# -----------------------------
# PERSONA WORKSPACES
# -----------------------------
def persona_workspaces():
    st.markdown('<div class="section-title">Persona Workspaces</div>', unsafe_allow_html=True)

    tabs = st.tabs([
        "Executive",
        "Supply Chain",
        "Finance",
        "Quality and Regulatory",
        "Commercial",
        "Field Team",
    ])

    with tabs[0]:
        searchable_table(
            rec_df,
            ["From","To","Product","Qty","Net Value Saved","Confidence","Priority"],
            search_key="persona_exec_search",
            title="Executive Decisions",
        )

    with tabs[1]:
        c1, c2 = st.columns(2)
        with c1:
            sc_region = st.multiselect(
                "Filter by Region",
                options=sorted(fdf["Region"].unique()),
                default=sorted(fdf["Region"].unique()),
                key="sc_region_filter",
            )
        with c2:
            sc_type = st.multiselect(
                "Filter by Type",
                options=sorted(fdf["Type"].unique()),
                default=sorted(fdf["Type"].unique()),
                key="sc_type_filter",
            )
        sc_df = fdf[fdf["Region"].isin(sc_region) & fdf["Type"].isin(sc_type)].copy()
        searchable_table(
            sc_df,
            [
                "Region","Location","Type","Product","Batch","Expiry",
                "Qty","At Risk Qty","Value at Risk","Risk Level"
            ],
            search_key="persona_supply_chain_search",
            title="Batch-Level Risk Board",
        )

    with tabs[2]:
        st.markdown("### Financial Impact")
        gross = rec_df["Gross Value Saved"].sum() if not rec_df.empty else 0
        logistics = rec_df["Logistics Cost"].sum() if not rec_df.empty else 0
        net = rec_df["Net Value Saved"].sum() if not rec_df.empty else 0

        c1, c2, c3 = st.columns(3)
        with c1:
            kpi("Gross Recovery", euro(gross))
        with c2:
            kpi("Logistics Cost", euro(logistics))
        with c3:
            kpi("Net Value Saved", euro(net))

        impact = pd.DataFrame({
            "Stage": ["Gross Recovery", "Logistics Cost", "Net Value Saved"],
            "Value": [gross, -logistics, net],
        })

        fig = px.bar(
            impact,
            x="Stage",
            y="Value",
            text="Value",
            height=380,
            color_discrete_sequence=["#1f6fb2"],
        )
        fig.update_traces(texttemplate="€%{text:,.0f}", textposition="outside")
        fig.update_layout(
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font_color="#111827",
        )
        st.plotly_chart(fig, use_container_width=True)

        searchable_table(
            rec_df,
            [
                "From","To","Product","Batch","Qty",
                "Gross Value Saved","Logistics Cost","Net Value Saved","Confidence"
            ],
            search_key="persona_finance_search",
            title="Financial Impact Records",
        )

    with tabs[3]:
        comp = fdf.copy()
        comp["Lot Traceability"] = "Passed"
        comp["Expiry Validity"] = comp["Days to Expiry"].apply(lambda x: "Passed" if x > 30 else "Review Required")
        comp["Quality Check"] = comp["Recall Status"].apply(lambda x: "Passed" if x == "Clear" else "Blocked")
        comp["Overall"] = comp["Quality Check"].apply(lambda x: "Blocked" if x == "Blocked" else "Eligible")

        c1, c2 = st.columns(2)
        with c1:
            qr_status = st.multiselect(
                "Filter by Overall Status",
                options=["Eligible","Blocked"],
                default=["Eligible","Blocked"],
                key="qr_status_filter",
            )
        with c2:
            qr_exp = st.multiselect(
                "Filter by Expiry Validity",
                options=["Passed","Review Required"],
                default=["Passed","Review Required"],
                key="qr_exp_filter",
            )
        comp = comp[comp["Overall"].isin(qr_status) & comp["Expiry Validity"].isin(qr_exp)]
        searchable_table(
            comp,
            [
                "Location","Product","Batch","Expiry","Lot Traceability",
                "Expiry Validity","Quality Check","Overall"
            ],
            search_key="persona_quality_search",
            title="Compliance Eligibility",
        )

    with tabs[4]:
        c1, c2 = st.columns(2)
        with c1:
            com_urgency = st.multiselect(
                "Filter by Urgency",
                options=["High","Medium","Low"],
                default=["High","Medium","Low"],
                key="com_urgency_filter",
            )
        with c2:
            com_region = st.multiselect(
                "Filter by Region",
                options=sorted(demand_df["Region"].unique()),
                default=sorted(demand_df["Region"].unique()),
                key="com_region_filter",
            )
        com_df = demand_df[demand_df["Urgency"].isin(com_urgency) & demand_df["Region"].isin(com_region)]
        searchable_table(
            com_df,
            [
                "Location","Region","SKU","Product",
                "Expected Demand 60D","Confidence","Signal","Urgency"
            ],
            search_key="persona_commercial_search",
            title="Demand and Account Signals",
        )

        if not com_df.empty:
            fig = px.bar(
                com_df,
                x="Location",
                y="Expected Demand 60D",
                color="Urgency",
                height=380,
                color_discrete_map={
                    "High": "#d92d20",
                    "Medium": "#f79009",
                    "Low": "#12b76a",
                },
            )
            fig.update_layout(
                paper_bgcolor="#ffffff",
                plot_bgcolor="#ffffff",
                font_color="#111827",
            )
            st.plotly_chart(fig, use_container_width=True)

    with tabs[5]:
        queue = pd.DataFrame([
            ["Berlin Neuro Center","Release 70 Optima Coil units for Madrid","High","€203K"],
            ["Munich Stroke Hospital","Release 40 Optima Coil units for Barcelona","High","€115K"],
            ["Milan Distributor","Negotiate redistribution pool for Squid","Medium","€178K"],
            ["Lyon Hospital","Confirm next 60-day Squid procedure demand","Medium","€72K"],
        ], columns=["Account","Recommended Action","Priority","Potential Value"])

        c1, _ = st.columns(2)
        with c1:
            fq_priority = st.multiselect(
                "Filter by Priority",
                options=["High","Medium","Low"],
                default=["High","Medium","Low"],
                key="fq_priority_filter",
            )
        queue = queue[queue["Priority"].isin(fq_priority)]
        searchable_table(
            queue,
            ["Account","Recommended Action","Priority","Potential Value"],
            search_key="persona_field_team_search",
            title="Daily Field Action Queue",
        )

# -----------------------------
# SCENARIO SIMULATOR
# -----------------------------
def scenario_simulator():
    section_title_with_info(
        "Scenario Decision Room",
        "Compare different actions for one risky inventory batch. The simulator shows which option protects the most value while balancing service level, compliance risk, and execution complexity.",
        level=2,
    )

    st.markdown(
        '<p class="small-muted">Select a batch, add strategies to compare, adjust assumptions, and identify the best action before execution.</p>',
        unsafe_allow_html=True,
    )

    if fdf.empty:
        st.warning("No inventory records available under current filters.")
        return

    # --- Demo framing questions ---
    st.markdown("### Suggested Demo Questions")
    q1, q2, q3, q4 = st.columns(4)
    with q1:
        st.markdown("""
<div class="info-box">
    <h4>Risk if No Action Is Taken</h4>
    <p>Shows the value that may be lost if the selected batch remains where it is.</p>
</div>
""", unsafe_allow_html=True)
    with q2:
        st.markdown("""
<div class="info-box">
    <h4>Redistribution Feasibility</h4>
    <p>Checks whether stock can be moved to a demand location with acceptable compliance and execution risk.</p>
</div>
""", unsafe_allow_html=True)
    with q3:
        st.markdown("""
<div class="info-box">
    <h4>Production Avoidance Opportunity</h4>
    <p>Compares new production against existing usable inventory already available in the network.</p>
</div>
""", unsafe_allow_html=True)
    with q4:
        st.markdown("""
<div class="info-box">
    <h4>Best Business Action</h4>
    <p>Ranks available options using value recovery, service level, compliance, and execution complexity.</p>
</div>
""", unsafe_allow_html=True)

    # --- Step 1: Select batch ---
    section_title_with_info(
        "Step 1: Select a Risky Inventory Batch",
        "Choose the specific hospital, distributor, or warehouse inventory position you want to simulate. All calculations below are based on this selected batch.",
    )

    sim_df = fdf.sort_values("Value at Risk", ascending=False).copy()
    sim_options = sim_df["Location"] + " | " + sim_df["Product"] + " | " + sim_df["Batch"]

    selected = st.selectbox(
        "Select a batch / location for simulation",
        sim_options,
        key="scenario_inventory_selector",
    )

    row = sim_df[sim_options == selected].iloc[0]

    item_recs = pd.DataFrame()
    if not rec_df.empty:
        item_recs = rec_df[
            (rec_df["Batch"] == row["Batch"])
            & (rec_df["From"] == row["Location"])
        ]

    gross_recovery = item_recs["Gross Value Saved"].sum() if not item_recs.empty else 0
    logistics_cost = item_recs["Logistics Cost"].sum() if not item_recs.empty else 0

    base_risk = float(row["Value at Risk"])
    base_qty_risk = float(row["At Risk Qty"])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi("Selected Product", row["Product"], f"Batch {row['Batch']}")
    with c2:
        kpi("At-Risk Quantity", f"{int(base_qty_risk)}", "Likely unused before expiry")
    with c3:
        kpi("Value at Risk", euro(base_risk), "Potential write-off")
    with c4:
        kpi("Days to Expiry", f"{int(row['Days to Expiry'])}", "Decision window")

    # --- Step 2: Adjust assumptions ---
    section_title_with_info(
        "Step 2: Adjust Business Assumptions",
        "Use these sliders to test real-world changes. If transfer success falls, distributor recovery improves, or production cost rises, the recommended action may change.",
    )

    a1, a2, a3, a4 = st.columns(4)
    with a1:
        transfer_success = st.slider(
            "Transfer success probability",
            min_value=40, max_value=100, value=85, step=5,
            help="Probability that transfer can be approved, shipped, received, and consumed in time.",
        ) / 100
    with a2:
        local_usage_lift = st.slider(
            "Local usage lift from incentive",
            min_value=0, max_value=60, value=25, step=5,
            help="Expected increase in local usage if commercial teams run a controlled action.",
        ) / 100
    with a3:
        distributor_recovery = st.slider(
            "Distributor recovery rate",
            min_value=20, max_value=80, value=48, step=5,
            help="Expected recovery if stock is returned or pooled through the distributor network.",
        ) / 100
    with a4:
        production_cost_factor = st.slider(
            "New production cost factor",
            min_value=40, max_value=120, value=90, step=5,
            help="Estimated cost of producing replacement stock relative to current value at risk.",
        ) / 100

    # --- Step 3: Choose strategies ---
    section_title_with_info(
        "Step 3: Choose Strategies to Compare",
        "This works like a comparison basket. Add or remove strategies to compare different operational decisions side by side.",
    )

    all_strategies = [
        "Do Nothing",
        "Redistribute to Demand Locations",
        "Return to Distributor Pool",
        "Local Commercial Incentive",
        "Produce New Inventory",
        "Split Strategy: Redistribute + Local Incentive",
    ]

    selected_strategies = st.multiselect(
        "Select strategies to compare",
        all_strategies,
        default=[
            "Do Nothing",
            "Redistribute to Demand Locations",
            "Return to Distributor Pool",
            "Local Commercial Incentive",
            "Produce New Inventory",
        ],
    )

    if not selected_strategies:
        st.warning("Select at least one strategy to compare.")
        return

    scenarios = []

    if "Do Nothing" in selected_strategies:
        scenarios.append({
            "Scenario": "Do Nothing",
            "Action Logic": "Leave stock at current location",
            "Expiry Loss": base_risk,
            "Recovered Value": 0,
            "Logistics Cost": 0,
            "Commercial Cost": 0,
            "Production Cost": base_risk * 0.55,
            "Service Level": 62,
            "Compliance Risk": "Low",
            "Execution Complexity": "Low",
            "Decision": "Avoid",
        })

    if "Redistribute to Demand Locations" in selected_strategies:
        adjusted_recovery = gross_recovery * transfer_success
        adjusted_logistics = logistics_cost if logistics_cost > 0 else 6800
        scenarios.append({
            "Scenario": "Redistribute to Demand Locations",
            "Action Logic": "Move stock to hospitals with matching demand",
            "Expiry Loss": max(base_risk - adjusted_recovery, 0),
            "Recovered Value": adjusted_recovery,
            "Logistics Cost": adjusted_logistics,
            "Commercial Cost": 0,
            "Production Cost": base_risk * 0.18,
            "Service Level": 88,
            "Compliance Risk": "Low" if row["Recall Status"] == "Clear" else "Blocked",
            "Execution Complexity": "Medium",
            "Decision": "Recommended" if adjusted_recovery > 0 and row["Recall Status"] == "Clear" else "Review",
        })

    if "Return to Distributor Pool" in selected_strategies:
        scenarios.append({
            "Scenario": "Return to Distributor Pool",
            "Action Logic": "Move stock back into distributor network",
            "Expiry Loss": base_risk * (1 - distributor_recovery),
            "Recovered Value": base_risk * distributor_recovery,
            "Logistics Cost": 12000,
            "Commercial Cost": 0,
            "Production Cost": base_risk * 0.30,
            "Service Level": 74,
            "Compliance Risk": "Medium",
            "Execution Complexity": "High",
            "Decision": "Backup",
        })

    if "Local Commercial Incentive" in selected_strategies:
        recovered = base_risk * min(0.25 + local_usage_lift, 0.70)
        scenarios.append({
            "Scenario": "Local Commercial Incentive",
            "Action Logic": "Accelerate usage at current account through controlled commercial action",
            "Expiry Loss": max(base_risk - recovered, 0),
            "Recovered Value": recovered,
            "Logistics Cost": 0,
            "Commercial Cost": base_risk * 0.12,
            "Production Cost": base_risk * 0.35,
            "Service Level": 72,
            "Compliance Risk": "Low",
            "Execution Complexity": "Medium",
            "Decision": "Backup",
        })

    if "Produce New Inventory" in selected_strategies:
        scenarios.append({
            "Scenario": "Produce New Inventory",
            "Action Logic": "Ignore current aging stock and trigger new production",
            "Expiry Loss": base_risk,
            "Recovered Value": 0,
            "Logistics Cost": 0,
            "Commercial Cost": 0,
            "Production Cost": base_risk * production_cost_factor,
            "Service Level": 91,
            "Compliance Risk": "Low",
            "Execution Complexity": "Medium",
            "Decision": "Avoid",
        })

    if "Split Strategy: Redistribute + Local Incentive" in selected_strategies:
        redistribution_recovery = gross_recovery * transfer_success * 0.75
        local_recovery = base_risk * min(local_usage_lift, 0.35)
        total_recovery = min(redistribution_recovery + local_recovery, base_risk)
        scenarios.append({
            "Scenario": "Split Strategy: Redistribute + Local Incentive",
            "Action Logic": "Move part of stock to demand locations and accelerate local usage for remaining quantity",
            "Expiry Loss": max(base_risk - total_recovery, 0),
            "Recovered Value": total_recovery,
            "Logistics Cost": max(logistics_cost * 0.75, 5000),
            "Commercial Cost": base_risk * 0.08,
            "Production Cost": base_risk * 0.16,
            "Service Level": 86,
            "Compliance Risk": "Low" if row["Recall Status"] == "Clear" else "Blocked",
            "Execution Complexity": "High",
            "Decision": "Review",
        })

    scenario_df = pd.DataFrame(scenarios)

    scenario_df["Capital Protected"] = (
        scenario_df["Recovered Value"]
        - scenario_df["Logistics Cost"]
        - scenario_df["Commercial Cost"]
    ).clip(lower=0)

    scenario_df["Net Impact"] = (
        scenario_df["Recovered Value"]
        - scenario_df["Expiry Loss"]
        - scenario_df["Logistics Cost"]
        - scenario_df["Commercial Cost"]
        - scenario_df["Production Cost"]
    )

    def score_scenario(r):
        score = 0
        score += min((r["Capital Protected"] / max(base_risk, 1)) * 40, 40)
        score += min((r["Service Level"] / 100) * 25, 25)
        if r["Compliance Risk"] == "Low":
            score += 15
        elif r["Compliance Risk"] == "Medium":
            score += 8
        if r["Execution Complexity"] == "Low":
            score += 10
        elif r["Execution Complexity"] == "Medium":
            score += 7
        else:
            score += 3
        if r["Net Impact"] > 0:
            score += 10
        return round(score, 1)

    scenario_df["Decision Score"] = scenario_df.apply(score_scenario, axis=1)
    best_scenario = scenario_df.sort_values("Decision Score", ascending=False).iloc[0]

    # --- Step 4: Recommended Decision ---
    section_title_with_info(
        "Step 4: Recommended Decision",
        "The system ranks every strategy using capital protected, service level, compliance risk, execution complexity, and net financial impact.",
    )

    st.markdown(
        f"""
<div class="card">
    <h3>{best_scenario['Scenario']}</h3>
    <p><b>Why:</b> {best_scenario['Action Logic']}</p>
    <p><b>Capital Protected:</b> {euro(best_scenario['Capital Protected'])} | <b>Net Impact:</b> {euro(best_scenario['Net Impact'])} | <b>Service Level:</b> {best_scenario['Service Level']}%</p>
    <p><b>Compliance Risk:</b> {best_scenario['Compliance Risk']} | <b>Execution Complexity:</b> {best_scenario['Execution Complexity']} | <b>Decision Score:</b> {best_scenario['Decision Score']}/100</p>
</div>
""",
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi("Best Strategy", best_scenario["Scenario"], "Highest decision score")
    with c2:
        kpi("Capital Protected", euro(best_scenario["Capital Protected"]), "After direct costs")
    with c3:
        kpi("Service Level", f"{best_scenario['Service Level']}%", "Expected fulfillment impact")
    with c4:
        kpi("Decision Score", f"{best_scenario['Decision Score']}/100", "Weighted recommendation score")

    # --- Step 5: Comparison Table ---
    section_title_with_info(
        "Step 5: Scenario Comparison Table",
        "Shows the full breakdown of every selected strategy, including recovered value, expiry loss, costs, service level, risk, complexity, and score.",
    )

    searchable_table(
        scenario_df,
        [
            "Scenario","Action Logic","Recovered Value","Expiry Loss",
            "Logistics Cost","Commercial Cost","Production Cost",
            "Capital Protected","Net Impact","Service Level",
            "Compliance Risk","Execution Complexity","Decision","Decision Score",
        ],
        search_key="scenario_basket_search",
        title=None,
    )

    # --- Charts ---
    c1, c2 = st.columns([1.2, 1])

    with c1:
        st.markdown("### Financial Outcome by Strategy")
        financial_long = scenario_df.melt(
            id_vars=["Scenario"],
            value_vars=[
                "Recovered Value","Expiry Loss","Logistics Cost",
                "Commercial Cost","Production Cost","Capital Protected","Net Impact",
            ],
            var_name="Metric",
            value_name="Value",
        )

        fig = px.bar(
            financial_long,
            x="Scenario",
            y="Value",
            color="Metric",
            barmode="group",
            height=520,
            text_auto=".2s",
            color_discrete_map={
                "Recovered Value": "#1f6fb2",
                "Expiry Loss": "#d92d20",
                "Logistics Cost": "#9333ea",
                "Commercial Cost": "#f97316",
                "Production Cost": "#f79009",
                "Capital Protected": "#12b76a",
                "Net Impact": "#0f172a",
            },
        )
        fig.update_layout(
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font_color="#111827",
            xaxis_title="Strategy",
            yaxis_title="Financial Value",
            legend_title="Financial Metric",
            legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="left", x=0),
            margin=dict(l=20, r=20, t=100, b=110),
        )
        fig.update_xaxes(tickangle=-20)
        fig.update_yaxes(tickprefix="€", separatethousands=True)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("### Strategic Decision Matrix")
        st.caption("Top-right zone = best outcome: high capital protection and high service level.")

        fig = px.scatter(
            scenario_df,
            x="Capital Protected",
            y="Service Level",
            size="Recovered Value",
            color="Decision",
            hover_name="Scenario",
            hover_data={
                "Capital Protected": ":,.0f",
                "Recovered Value": ":,.0f",
                "Net Impact": ":,.0f",
                "Compliance Risk": True,
                "Execution Complexity": True,
                "Decision Score": True,
            },
            height=520,
            color_discrete_map={
                "Recommended": "#12b76a",
                "Backup": "#f79009",
                "Avoid": "#d92d20",
                "Review": "#2e90fa",
            },
        )
        fig.add_vline(x=scenario_df["Capital Protected"].median(), line_dash="dash", line_color="#94a3b8")
        fig.add_hline(y=scenario_df["Service Level"].median(), line_dash="dash", line_color="#94a3b8")
        fig.update_layout(
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font_color="#111827",
            xaxis_title="Capital Protected",
            yaxis_title="Service Level",
            legend_title="Decision Category",
            legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="left", x=0),
            margin=dict(l=20, r=20, t=100, b=60),
        )
        fig.update_xaxes(tickprefix="€", separatethousands=True)
        fig.update_yaxes(ticksuffix="%")
        st.plotly_chart(fig, use_container_width=True)

    # Decision score ranking
    st.markdown("### Decision Score Ranking")
    score_df = scenario_df.sort_values("Decision Score", ascending=True)
    fig = px.bar(
        score_df,
        x="Decision Score",
        y="Scenario",
        orientation="h",
        color="Decision",
        text="Decision Score",
        height=420,
        color_discrete_map={
            "Recommended": "#12b76a",
            "Backup": "#f79009",
            "Avoid": "#d92d20",
            "Review": "#2e90fa",
        },
    )
    fig.update_layout(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font_color="#111827",
        xaxis_title="Decision Score out of 100",
        yaxis_title="",
        legend_title="Decision Category",
    )
    fig.update_xaxes(range=[0, 100])
    st.plotly_chart(fig, use_container_width=True)

    # --- Step 6: Explain one strategy ---
    section_title_with_info(
        "Step 6: Explain One Strategy",
        "Select any strategy to see the detailed business logic behind it. Useful during a live demo when someone asks why one option is better.",
    )

    selected_scenario = st.selectbox(
        "Select a strategy to explain",
        scenario_df["Scenario"],
        key="scenario_explainer_select",
    )

    selected_row = scenario_df[scenario_df["Scenario"] == selected_scenario].iloc[0]

    st.markdown(
        f"""
<div class="card">
    <h3>{selected_row['Scenario']}</h3>
    <p><b>Action:</b> {selected_row['Action Logic']}</p>
    <p><b>Recovered Value:</b> {euro(selected_row['Recovered Value'])} &nbsp;|&nbsp; <b>Expiry Loss:</b> {euro(selected_row['Expiry Loss'])}</p>
    <p><b>Logistics Cost:</b> {euro(selected_row['Logistics Cost'])} &nbsp;|&nbsp; <b>Commercial Cost:</b> {euro(selected_row['Commercial Cost'])} &nbsp;|&nbsp; <b>Production Cost:</b> {euro(selected_row['Production Cost'])}</p>
    <p><b>Capital Protected:</b> {euro(selected_row['Capital Protected'])} &nbsp;|&nbsp; <b>Net Impact:</b> {euro(selected_row['Net Impact'])}</p>
    <p><b>Service Level:</b> {selected_row['Service Level']}% &nbsp;|&nbsp; <b>Compliance Risk:</b> {selected_row['Compliance Risk']} &nbsp;|&nbsp; <b>Execution Complexity:</b> {selected_row['Execution Complexity']}</p>
    <p><b>Decision Score:</b> {selected_row['Decision Score']}/100</p>
</div>
""",
        unsafe_allow_html=True,
    )

    if selected_row["Scenario"] == "Redistribute to Demand Locations":
        if item_recs.empty:
            st.info("No demand-matched transfer exists for this selected batch. The strategy remains under review.")
        else:
            st.success("This is recommended because matching demand exists, value recovery is high, and transfer reduces expiry exposure before new production is required.")
            st.dataframe(
                item_recs[["From","To","Product","Batch","Qty","Net Value Saved","Confidence","Compliance","Reason"]],
                use_container_width=True,
                hide_index=True,
            )
    elif selected_row["Scenario"] == "Do Nothing":
        st.warning("This keeps execution simple but creates avoidable expiry loss and does not improve working capital.")
    elif selected_row["Scenario"] == "Produce New Inventory":
        st.warning("This protects service levels but is financially weak because existing inventory remains at risk while new production cost is added.")
    elif selected_row["Scenario"] == "Return to Distributor Pool":
        st.info("This can help if hospital-level demand is uncertain, but ownership constraints and execution complexity are higher.")
    elif selected_row["Scenario"] == "Local Commercial Incentive":
        st.info("This can accelerate local usage, but it may reduce margin and does not solve wider network imbalance.")
    elif selected_row["Scenario"] == "Split Strategy: Redistribute + Local Incentive":
        st.info("This is useful when one action is not enough. It combines redistribution for matched demand with local action for remaining inventory.")

# -----------------------------
# ROUTER
# -----------------------------
if page == "Executive Overview":
    executive_overview()
elif page == "Global Search and Investigation":
    search_and_investigation()
elif page == "Persona Workspaces":
    persona_workspaces()
elif page == "Scenario Simulator":
    scenario_simulator()
elif page == "AI Copilot":
    render_copilot_page(df, rec_df, demand_df, TODAY)
elif page == "ROI Calculator":
    render_roi_page(df, rec_df)
elif page == "Executive Export":
    render_export_page(df, rec_df, demand_df, TODAY)

st.markdown("---")
st.caption(
    "Neurovascular Inventory Control Tower — Expiry-aware redistribution, demand matching, compliance validation and working capital protection."
)
