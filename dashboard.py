import streamlit as st
import pandas as pd
import plotly.express as px

from transaction_risk_analysis import clean_df

st.set_page_config(
    page_title="Transaction Risk Analysis",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# Dark UI Styling
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

df = load_data()

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

    filtered_df = df[
        (df["risk_level"].isin(selected_risks)) &
        (df["Payment_Method"].isin(selected_payments)) &
        (df["Customer_Loyalty_Tier"].isin(selected_tiers)) &
        (df["Purchase_Amount"].astype(float).between(amount_range[0], amount_range[1]))
    ]

    st.write(f"**{len(filtered_df):,} transactions match the selected filters.**")

    high_value = filtered_df[
        filtered_df["risk_level"].isin(["High", "Severe"])
    ]["Purchase_Amount"].sum()

    avg_likelihood = filtered_df["likelihood"].mean() if len(filtered_df) > 0 else 0
    avg_impact = filtered_df["impact"].mean() if len(filtered_df) > 0 else 0

    metric1, metric2, metric3 = st.columns(3)

    metric1.metric("Filtered At-Risk Value", f"${high_value:,.2f}")
    metric2.metric("Average Likelihood", f"{avg_likelihood:.2f}/5")
    metric3.metric("Average Impact", f"{avg_impact:.2f}/5")

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

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

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

        # 👇 MUST be inside the function
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

    st.write(
        "This section demonstrates how unsafe SQL string concatenation can create a security risk "
        "and how parameterized queries reduce that risk. No database is used and no query is executed."
    )

    user_input = st.text_input(
        "Enter sample customer input",
        value="' OR '1'='1"
    )

    unsafe_query = f"SELECT * FROM transactions WHERE Customer_ID = '{user_input}'"
    safe_query = "SELECT * FROM transactions WHERE Customer_ID = ?"

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Unsafe Query")
        st.code(unsafe_query, language="sql")
        st.warning(
            "This query directly inserts user input into the SQL statement. "
            "Malicious input could change the query behavior."
        )

    with col2:
        st.subheader("Safer Query")
        st.code(safe_query, language="sql")
        st.success(
            "This query uses a placeholder, so the input is treated as data instead of executable SQL code."
        )

    st.subheader("Why This Matters")
    st.write(
        "A transaction risk system may handle sensitive customer and purchase information. "
        "This simulation shows why secure coding practices are important when building systems that store or analyze transaction data."
    )


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