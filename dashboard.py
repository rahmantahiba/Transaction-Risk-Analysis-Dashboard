"""

How to run the code?

Use the local terminal and type the command (make sure your file path is correct)
and type "py -m streamlit run dashboard.py"

DO NOT use the normal run button it will only result in multiple errors

To open the interface click either the local host site or network one.

Make sure the site is on dark mode for the best experience.

If libraries are missing, they will be installed automatically.
If the app does not run, manually install dependencies:

pip install pandas streamlit plotly openpyxl

"""

#To ensure the essential packages exist

import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Auto-install missing packages
try:
    import pandas
except ImportError:
    install("pandas")

try:
    import streamlit
except ImportError:
    install("streamlit")

try:
    import plotly
except ImportError:
    install("plotly")

try:
    import openpyxl
except ImportError:
    install("openpyxl")

#Necessary imports for the dashboard to have key functionality

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

from transaction_risk_analysis import clean_df

st.set_page_config(
    page_title="Transaction Risk Analysis",
    page_icon="Logo/LuxeBeauty/favicon.ico",
    layout="wide"
)

# -----------------------------
# CSS for styling the UI
# -----------------------------
st.markdown("""
<style>
.stApp {
    background-color: #0f172a;
    color: #e5e7eb;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

h1, h2, h3, h4, h5, h6, p, label, span, div {
    color: #e5e7eb !important;
}

section[data-testid="stSidebar"] {
    background-color: #111827;
    border-right: 1px solid #1f2937;
}

section[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}

.metric-card {
    background-color: #1e293b;
    padding: 22px;
    border-radius: 16px;
    border: 1px solid #334155;
    box-shadow: 0px 4px 14px rgba(0,0,0,0.30);
}

.metric-label {
    color: #94a3b8 !important;
    font-size: 0.85rem;
}

.metric-value {
    font-size: 1.9rem;
    font-weight: 700;
    color: #f8fafc !important;
}

.info-box {
    background-color: #1e293b;
    border-left: 5px solid #6366f1;
    padding: 16px;
    border-radius: 12px;
    color: #e5e7eb !important;
    margin-bottom: 20px;
}

.stDataFrame, .stTable {
    background-color: #1e293b;
    color: #e5e7eb;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Shared Chart Theme
# -----------------------------
CHART_LAYOUT = dict(
    paper_bgcolor="#0f172a",
    plot_bgcolor="#1e293b",
    font=dict(color="#e5e7eb"),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.08)",
        tickfont=dict(color="#cbd5e1"),
        title_font=dict(color="#cbd5e1"),
        linecolor="rgba(255,255,255,0.15)"
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.08)",
        tickfont=dict(color="#cbd5e1"),
        title_font=dict(color="#cbd5e1"),
        linecolor="rgba(255,255,255,0.15)"
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e5e7eb")
    ),
    margin=dict(l=10, r=10, t=40, b=10)
)

# -----------------------------
# Data
# -----------------------------
@st.cache_data
def load_data():
    return clean_df.copy()


@st.cache_resource
def get_sim_conn(_df):
    """In-memory SQLite loaded from clean_df — used only for the SQL injection demo."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    _df.to_sql("transactions", conn, index=False, if_exists="replace")
    return conn


df = load_data()
sim_conn = get_sim_conn(df)

RISK_ORDER = ["Low", "Moderate", "High", "Severe"]

RISK_COLORS = {
    "Low": "#22c55e",
    "Moderate": "#eab308",
    "High": "#f97316",
    "Severe": "#ef4444"
}

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.title("Transaction Risk")
    st.caption("Risk scoring dashboard")

    page = st.radio(
        "Navigation",
        ["Overview", "Risk Analysis", "Threat Simulation", "NIST Framework"]
    )

    st.divider()
    st.caption("Python · pandas · Plotly · Streamlit")


# -----------------------------
# Overview
# -----------------------------
if page == "Overview":
    st.title("Transaction Risk Analysis")

    st.markdown(
        """
        <div class="info-box">
        This dashboard evaluates purchase transactions using a rule-based likelihood-impact model.
        It helps identify high-risk activity, review transaction patterns, and support e-commerce risk decisions.
        </div>
        """,
        unsafe_allow_html=True
    )

    total_transactions = len(df)
    total_value = df["Purchase_Amount"].astype(float).sum()
    avg_risk = df["risk_score"].mean()
    high_risk_count = len(df[df["risk_level"].isin(["High", "Severe"])])

    col1, col2, col3, col4 = st.columns(4)

    metrics = [
        ("Total Transactions", f"{total_transactions:,}"),
        ("High / Severe Risks", f"{high_risk_count:,}"),
        ("Average Risk Score", f"{avg_risk:.2f}"),
        ("Total Purchase Value", f"${total_value:,.0f}")
    ]

    for col, (label, value) in zip([col1, col2, col3, col4], metrics):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)

    st.subheader("Risk Level Distribution")

    risk_counts = (
        df["risk_level"]
        .value_counts()
        .reindex(RISK_ORDER)
        .fillna(0)
        .reset_index()
    )
    risk_counts.columns = ["Risk Level", "Count"]

    fig = px.bar(
        risk_counts,
        x="Risk Level",
        y="Count",
        color="Risk Level",
        color_discrete_map=RISK_COLORS,
        text="Count",
        category_orders={"Risk Level": RISK_ORDER}
    )

    fig.update_traces(
        textfont=dict(color="#e5e7eb"),
        textposition="outside"
    )

    fig.update_layout(
        showlegend=False,
        height=400,
        **CHART_LAYOUT
    )

    st.plotly_chart(fig, use_container_width=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Average Risk by Payment Method")

        payment_risk = (
            df.groupby("Payment_Method")["risk_score"]
            .mean()
            .sort_values(ascending=True)
            .reset_index()
        )

        payment_risk["color_rank"] = range(1, len(payment_risk) + 1)

        fig_payment = px.bar(
            payment_risk,
            x="risk_score",
            y="Payment_Method",
            orientation="h",
            color="color_rank",
            color_continuous_scale=["#22c55e", "#eab308", "#f97316", "#ef4444"],
            labels={
                "risk_score": "Average Risk Score",
                "Payment_Method": "Payment Method"
            }
        )

        fig_payment.update_layout(
            height=380,
            paper_bgcolor="#0f172a",
            plot_bgcolor="#1e293b",
            font=dict(color="#e5e7eb", size=12),
            coloraxis=dict(
                colorbar=dict(
                    title="Risk Rank",
                    x=1.08,
                    thickness=14,
                    len=0.75
                )
            ),
            xaxis=dict(
                title="Average Risk Score",
                gridcolor="rgba(255,255,255,0.08)"
            ),
            yaxis=dict(
                title="Payment Method",
                categoryorder="total ascending",
                gridcolor="rgba(255,255,255,0.05)"
            ),
            margin=dict(l=40, r=90, t=20, b=40)
        )

        with col_b:
            st.subheader("Average Risk by Loyalty Tier")

            loyalty_risk = (
                df.groupby("Customer_Loyalty_Tier")["risk_score"]
                .mean()
                .sort_values(ascending=True)
                .reset_index()
            )

            # Create rank (this drives color gradient)
            loyalty_risk["color_rank"] = range(1, len(loyalty_risk) + 1)

            fig_loyalty = px.bar(
                loyalty_risk,
                x="Customer_Loyalty_Tier",
                y="risk_score",
                color="color_rank",
                color_continuous_scale=[
                    "#3b82f6",  # blue
                    "#6366f1",  # purple
                    "#f97316",  # orange
                    "#ef4444"  # red
                ],
                labels={
                    "risk_score": "Average Risk Score",
                    "Customer_Loyalty_Tier": "Loyalty Tier",
                    "color_rank": "Risk Rank"
                }
            )

            fig_loyalty.update_layout(
                height=380,
                paper_bgcolor="#0f172a",
                plot_bgcolor="#1e293b",
                font=dict(color="#e5e7eb", size=12),

                # THIS FIXES THE WEIRD SCALE POSITION
                coloraxis=dict(
                    colorbar=dict(
                        title="Risk Rank",
                        x=1.02,  # closer to chart (not floating far away)
                        thickness=12,
                        len=0.7
                    )
                ),

                xaxis=dict(
                    title="Loyalty Tier",
                    gridcolor="rgba(255,255,255,0.05)"
                ),
                yaxis=dict(
                    title="Average Risk Score",
                    gridcolor="rgba(255,255,255,0.08)"
                ),

                margin=dict(l=40, r=70, t=20, b=40)
            )

            st.plotly_chart(fig_loyalty, use_container_width=True)

        fig_loyalty.update_layout(
            height=380,
            coloraxis_showscale=True,
            paper_bgcolor="#0f172a",
            plot_bgcolor="#1e293b",
            font=dict(color="#e5e7eb", size=12),
            xaxis=dict(
                title="Loyalty Tier",
                title_font=dict(size=13, color="#cbd5e1"),
                tickfont=dict(size=11, color="#cbd5e1"),
                gridcolor="rgba(255,255,255,0.05)"
            ),
            yaxis=dict(
                title="Average Risk Score",
                title_font=dict(size=13, color="#cbd5e1"),
                tickfont=dict(size=11, color="#cbd5e1"),
                gridcolor="rgba(255,255,255,0.08)"
            ),
            margin=dict(l=20, r=20, t=20, b=40)
        )

        st.plotly_chart(fig_loyalty, use_container_width=True)


# -----------------------------
# Risk Analysis
# -----------------------------
elif page == "Risk Analysis":
    st.title("Risk Analysis")
    st.write("Filter and review transactions by risk level, payment method, loyalty tier, and purchase amount.")

    col1, col2, col3 = st.columns(3)

    with col1:
        selected_risks = st.multiselect(
            "Risk Level",
            options=RISK_ORDER,
            default=["High", "Severe"]
        )

    with col2:
        selected_payments = st.multiselect(
            "Payment Method",
            options=sorted(df["Payment_Method"].dropna().unique()),
            default=sorted(df["Payment_Method"].dropna().unique())
        )

    with col3:
        selected_tiers = st.multiselect(
            "Loyalty Tier",
            options=sorted(df["Customer_Loyalty_Tier"].dropna().unique()),
            default=sorted(df["Customer_Loyalty_Tier"].dropna().unique())
        )

    min_amount = float(df["Purchase_Amount"].min())
    max_amount = float(df["Purchase_Amount"].max())

    amount_range = st.slider(
        "Purchase Amount Range",
        min_value=min_amount,
        max_value=max_amount,
        value=(min_amount, max_amount)
    )

    # Filtering
    filtered_df = df[
        (df["risk_level"].isin(selected_risks)) &
        (df["Payment_Method"].isin(selected_payments)) &
        (df["Customer_Loyalty_Tier"].isin(selected_tiers)) &
        (df["Purchase_Amount"].astype(float).between(amount_range[0], amount_range[1]))
    ]

    st.write(f"**{len(filtered_df):,} transactions match the selected filters.**")

    # --- Metrics Calculations ---
    filtered_value = filtered_df["Purchase_Amount"].sum()

    at_risk_value = filtered_df["Purchase_Amount"].sum()

    # % of total dataset (not just filtered)
    total_dataset_value = df["Purchase_Amount"].sum()

    at_risk_pct = (at_risk_value / total_dataset_value * 100) if total_dataset_value > 0 else 0

    avg_likelihood = filtered_df["likelihood"].mean() if len(filtered_df) > 0 else 0
    avg_impact = filtered_df["impact"].mean() if len(filtered_df) > 0 else 0

    # --- Display Metrics ---
    metric1, metric2, metric3, metric4, metric5 = st.columns(5)

    metric1.metric("Filtered Transaction Value", f"${filtered_value:,.2f}")
    metric2.metric("Filtered Value", f"${at_risk_value:,.2f}")
    metric3.metric("% of Total Value", f"{at_risk_pct:.1f}%")
    metric4.metric("Average Likelihood", f"{avg_likelihood:.2f}/5")
    metric5.metric("Average Impact", f"{avg_impact:.2f}/5")

    # --- Table ---
    st.subheader("Highest-Risk Transactions")

    display_columns = [
        "transaction_id_short",
        "customer_id_short",
        "Payment_Method",
        "Customer_Loyalty_Tier",
        "Purchase_Amount",
        "Transaction_Time",
        "likelihood",
        "impact",
        "risk_score",
        "risk_level"
    ]

    available_columns = [col for col in display_columns if col in filtered_df.columns]

    display_df = (
        filtered_df[available_columns]
        .sort_values(by="risk_score", ascending=False)
        .head(200)
    )

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # --- Risk Matrix ---
    st.subheader("Risk Matrix: Likelihood vs. Impact")

    matrix_df = (
        filtered_df.groupby(["likelihood", "impact"])
        .size()
        .reset_index(name="count")
    )

    matrix_df["risk_score"] = matrix_df["likelihood"] * matrix_df["impact"]

    fig_matrix = px.density_heatmap(
        matrix_df,
        x="likelihood",
        y="impact",
        z="risk_score",
        text_auto="count",
        color_continuous_scale=[
            [0.0, "#22c55e"],
            [0.4, "#eab308"],
            [0.7, "#f97316"],
            [1.0, "#ef4444"]
        ],
        labels={
            "likelihood": "Likelihood Score",
            "impact": "Impact Score",
            "count": "Transaction Count",
            "risk_score": "Risk Severity"
        }
    )

    fig_matrix.update_traces(
        textfont=dict(size=16, color="#0f172a")
    )

    fig_matrix.update_layout(
        height=460,
        paper_bgcolor="#0f172a",
        plot_bgcolor="#1e293b",
        font=dict(color="#e5e7eb", size=12),
        xaxis=dict(dtick=1, gridcolor="rgba(255,255,255,0.08)"),
        yaxis=dict(dtick=1, gridcolor="rgba(255,255,255,0.08)"),
        coloraxis_colorbar=dict(title="Risk Severity"),
        margin=dict(l=30, r=30, t=20, b=30)
    )

    st.plotly_chart(fig_matrix, use_container_width=True)

# -----------------------------
# Threat Simulation
# -----------------------------
elif page == "Threat Simulation":
    st.title("Threat Simulation: SQL Injection")
    st.markdown("""<div class="info-box">
        Both queries below execute live against a real in-memory database loaded from your transaction dataset.
        The <strong>vulnerable</strong> side actually runs the injected SQL — you can see the attack succeed in real time.
        The <strong>safe</strong> side shows how parameterized queries neutralize the exact same payload.
        </div>""", unsafe_allow_html=True)

    # ── Attack type selector ────────────────────────────────
    st.markdown("#### Step 1 — Choose an attack type")
    attack_type = st.selectbox("Attack type", [
        "Authentication bypass  (' OR '1'='1)",
        "UNION data extraction",
        "Comment injection",
        "Always-true with comment  (' OR 1=1 --)",
        "Custom payload",
    ])

    PRESETS = {
        "Authentication bypass  (' OR '1'='1)": "' OR '1'='1",
        "UNION data extraction": "' UNION SELECT Transaction_ID, Customer_ID, Payment_Method, risk_level, Purchase_Amount FROM transactions --",
        "Comment injection": "CUST-0001' --",
        "Always-true with comment  (' OR 1=1 --)": "' OR 1=1 --",
        "Custom payload": "",
    }

    EXPLANATIONS = {
        "Authentication bypass  (' OR '1'='1)":
            "Closes the string quote early, then appends `OR '1'='1'` — a condition that is always true. Every row in the database is returned instead of just the target customer.",
        "UNION data extraction":
            "Appends a second `SELECT` via `UNION`. The attacker selects columns they want to steal from the `transactions` table and merges them into the original result set.",
        "Comment injection":
            "Appends `--` which comments out the rest of the SQL. Any trailing conditions (e.g. `AND active=1`) are silently ignored.",
        "Always-true with comment  (' OR 1=1 --)":
            "`1=1` is always true, so the WHERE clause always passes. Combined with `--` it drops any additional filters.",
        "Custom payload":
            "Write your own SQL injection payload and observe the result on both sides.",
    }

    default_val = PRESETS[attack_type]
    st.markdown("#### Step 2 — Edit the payload (optional)")
    user_input = st.text_input("Payload injected as the Customer ID value:", value=default_val,
                               placeholder="Type a custom payload...")

    st.markdown(f"""
        <div style='background:rgba(239,68,68,0.07); border:1px solid rgba(239,68,68,0.25);
                    border-radius:10px; padding:12px 16px; margin:8px 0 20px 0;
                    font-size:0.84rem; color:#fca5a5;'>
            <strong>How this attack works:</strong> {EXPLANATIONS[attack_type]}
        </div>""", unsafe_allow_html=True)

    st.markdown("#### Step 3 — Fire the attack")
    st.markdown("---")

    col_v, col_s = st.columns(2)

    # ── VULNERABLE SIDE ──────────────────────────────────────
    with col_v:
        st.markdown("<span class='attack-badge'>⚠ Vulnerable — String Concatenation</span>", unsafe_allow_html=True)

        vuln_query = f"SELECT * FROM transactions WHERE Customer_ID = '{user_input}' LIMIT 200"
        st.markdown(f"<div class='terminal danger'>{vuln_query}</div>", unsafe_allow_html=True)

        vuln_result = None
        vuln_error = None
        vuln_rows = 0

        try:
            vuln_result = pd.read_sql_query(vuln_query, sim_conn)
            vuln_rows = len(vuln_result)
        except Exception as e:
            vuln_error = str(e)

        if vuln_error:
            st.markdown(f"""<div class='result-box' style='border:1px solid #7f1d1d; color:#fca5a5;'>
                    ✗ Query error — {vuln_error}
                </div>""", unsafe_allow_html=True)
        else:
            injected = vuln_rows > 1
            color = "#fca5a5" if injected else "#86efac"
            icon = "🚨 ATTACK SUCCEEDED" if injected else "✓ No injection detected"
            border = "#7f1d1d" if injected else "#14532d"
            st.markdown(f"""<div class='result-box' style='border:1px solid {border}; color:{color};'>
                    {icon} — <strong>{vuln_rows:,}</strong> row(s) returned
                </div>""", unsafe_allow_html=True)

            if vuln_result is not None and not vuln_result.empty:
                show_cols = [c for c in ["Customer_ID", "Transaction_ID", "Payment_Method",
                                         "risk_level", "risk_score", "Purchase_Amount"]
                             if c in vuln_result.columns]
                st.dataframe(vuln_result[show_cols].head(15),
                             use_container_width=True, hide_index=True)

    # ── SAFE SIDE ────────────────────────────────────────────
    with col_s:
        st.markdown("<span class='safe-badge'>✓ Safe — Parameterized Query</span>", unsafe_allow_html=True)

        safe_query = "SELECT * FROM transactions WHERE Customer_ID = ? LIMIT 200"
        st.markdown(f"<div class='terminal safe'>{safe_query}\n\n-- Bound value → \"{user_input}\"</div>",
                    unsafe_allow_html=True)

        safe_result = None
        safe_error = None
        safe_rows = 0

        try:
            safe_result = pd.read_sql_query(safe_query, sim_conn, params=(user_input,))
            safe_rows = len(safe_result)
        except Exception as e:
            safe_error = str(e)

        if safe_error:
            st.markdown(f"""<div class='result-box' style='border:1px solid #7f1d1d; color:#fca5a5;'>
                    ✗ Query error — {safe_error}
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class='result-box' style='border:1px solid #14532d; color:#86efac;'>
                    ✓ Injection neutralized — <strong>{safe_rows}</strong> row(s) returned
                </div>""", unsafe_allow_html=True)

            if safe_result is not None and not safe_result.empty:
                show_cols = [c for c in ["Customer_ID", "Transaction_ID", "Payment_Method",
                                         "risk_level", "risk_score", "Purchase_Amount"]
                             if c in safe_result.columns]
                st.dataframe(safe_result[show_cols].head(15),
                             use_container_width=True, hide_index=True)
            else:
                st.markdown("""<div style='color:#64748b; font-size:0.82rem; font-family:monospace;
                                               margin-top:12px; text-align:center; padding:20px;'>
                        No matching customer found.<br>Payload treated as a literal string — attack blocked.
                    </div>""", unsafe_allow_html=True)

    # ── What happened ────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### What just happened?")

    if vuln_rows > safe_rows and vuln_rows > 1:
        st.error(f"""
    **Attack succeeded on the vulnerable side.**
    The payload broke out of the intended `WHERE Customer_ID = '...'` filter and returned
    **{vuln_rows:,} rows** from the database — far more than the 0 or 1 the application expected.

    On the safe side, the exact same payload was bound as a plain string value.
    The database driver never parsed it as SQL, so it returned **{safe_rows} row(s)** — attack blocked.
            """)
    elif vuln_error:
        st.warning(
            "The payload caused a SQL syntax error on the vulnerable side — still a sign of injection vulnerability. In a real system, error messages themselves can leak database structure to an attacker.")
    else:
        st.success(
            f"Both queries returned **{safe_rows}** row(s). This payload didn't alter the row count (e.g. `DROP TABLE` is blocked by SQLite's single-statement safety). Try **Authentication bypass** or **UNION data extraction** to see a successful attack.")

    # ── Mitigation checklist ─────────────────────────────────
    st.markdown("---")
    st.markdown("#### Mitigation Checklist")

    st.markdown("""
    - Always use parameterized queries or prepared statements — never concatenate user input into SQL.
    - Validate and sanitize input: type-check, length-limit, and allowlist expected formats.
    - Use an ORM (SQLAlchemy, Django ORM) which parameterizes by default.
    - Apply the principle of least privilege — DB accounts should only have the permissions they need.
    - Log and alert on anomalous query patterns: mass row returns, repeated errors, or UNION keywords.
    """)

# -----------------------------
# NIST Framework
# -----------------------------
elif page == "NIST Framework":
    st.title("NIST Framework Alignment")

    st.write(
        "This project is inspired by NIST cybersecurity risk management principles, especially "
        "the use of likelihood and impact to assess and prioritize risk."
    )

    st.subheader("How the System Aligns with NIST Concepts")

    nist_items = [
        {
            "Function": "Identify",
            "Project Connection": "The system identifies transaction risk indicators such as payment method, loyalty tier, transaction time, and purchase amount."
        },
        {
            "Function": "Protect",
            "Project Connection": "The threat simulation explains how parameterized queries can help protect transaction data from SQL injection."
        },
        {
            "Function": "Detect",
            "Project Connection": "The dashboard detects elevated risk by classifying transactions into Low, Moderate, High, and Severe categories."
        },
        {
            "Function": "Respond",
            "Project Connection": "High-risk and severe transactions are prioritized so they can be reviewed before causing greater financial or operational harm."
        },
        {
            "Function": "Recover",
            "Project Connection": "Risk results can help businesses review patterns and improve future scoring rules, controls, and monitoring processes."
        }
    ]

    st.dataframe(
        pd.DataFrame(nist_items),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Risk Classification Model")

    classification = pd.DataFrame({
        "Risk Score Range": ["1–4", "5–9", "10–16", "17–25"],
        "Risk Level": ["Low", "Moderate", "High", "Severe"],
        "Meaning": [
            "Minimal concern; monitor as normal",
            "Some concern; review if patterns repeat",
            "Important concern; prioritize for review",
            "Critical concern; requires immediate attention"
        ]
    })

    st.dataframe(
        classification,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Risk Score Distribution")

    # High-contrast colors for dark mode
    color_map = {
        "Low": "#00e676",  # bright green
        "Moderate": "#ffd600",  # bright yellow
        "High": "#ff6d00",  # strong orange
        "Severe": "#ff1744"  # bright red
    }

    fig_hist = px.histogram(
        df,
        x="risk_score",
        color="risk_level",
        color_discrete_map=color_map,
        nbins=20,
        barmode="group",  # cleaner than overlap
        opacity=0.9,
        labels={
            "risk_score": "Risk Score",
            "risk_level": "Risk Level"
        },
        category_orders={"risk_level": ["Low", "Moderate", "High", "Severe"]}
    )

    fig_hist.update_layout(
        height=420,
        paper_bgcolor="#0f172a",
        plot_bgcolor="#1e293b",
        font=dict(color="#e5e7eb"),

        xaxis=dict(
            title="Risk Score",
            gridcolor="rgba(255,255,255,0.15)"
        ),
        yaxis=dict(
            title="Count",
            gridcolor="rgba(255,255,255,0.15)"
        ),

        legend=dict(
            title="Risk Level",
            font=dict(size=12)
        ),

        margin=dict(l=30, r=30, t=20, b=30)
    )

    st.plotly_chart(fig_hist, use_container_width=True)