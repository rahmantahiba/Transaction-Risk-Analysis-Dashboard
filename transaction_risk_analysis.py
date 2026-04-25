import pandas as pd

"""

Note:

Ensure the dataset file is located
in the "Dataset" folder relative to this script.

"""

raw_df = pd.read_excel("Dataset/luxury_cosmetics_fraud_analysis_2025.xlsx")

"""
Data Cleaning
"""

# Drop duplicates
clean_df = raw_df.drop_duplicates()

# Fill missing values with "Unknown"
clean_df = clean_df.fillna("Unknown")

# Drop fraud column from cleaned dataset
clean_df = clean_df.drop(columns=["Fraud_Flag"])

# Shorten ID strings for easier processing
clean_df["transaction_id_short"] = clean_df["Transaction_ID"].astype(str).str[:8]
clean_df["customer_id_short"] = clean_df["Customer_ID"].astype(str).str[:8]

"""
Risk calculation logic
"""

def calculate_likelihood(payment_method, loyalty_tier, transaction_time):
    score = 0

    if payment_method == "Gift Card":
        score += 2
    elif payment_method == "Mobile Payment":
        score += 1
    elif payment_method == "None":
        score += 2

    if loyalty_tier == "None":
        score += 2
    elif loyalty_tier == "Bronze":
        score += 1

    hour = int(str(transaction_time).split(":")[0])

    if hour < 6 or hour > 22:
        score += 1

    return min(score, 5)

def calculate_impact(amount):
    if amount < 50:
        return 1
    elif amount < 150:
        return 2
    elif amount < 300:
        return 3
    elif amount < 500:
        return 4
    else:
        return 5

def calculate_risk(likelihood, impact):
    return likelihood * impact

clean_df["likelihood"] = clean_df.apply(
    lambda row: calculate_likelihood(
        row["Payment_Method"],
        row["Customer_Loyalty_Tier"],
        row["Transaction_Time"]
    ),
    axis=1
)

def categorize_risk(score):
    if score <= 3:
        return "Low"
    elif score <= 6:
        return "Moderate"
    elif score <= 12:
        return "High"
    else:
        return "Severe"

# Calculate impact score based on purchase amount
clean_df["impact"] = clean_df["Purchase_Amount"].apply(calculate_impact)

# Calculate final risk score
clean_df["risk_score"] = clean_df.apply(
    lambda row: calculate_risk(row["likelihood"], row["impact"]),
    axis=1
)

"""
Sanity check
"""

clean_df["risk_level"] = clean_df["risk_score"].apply(categorize_risk)

high_risk_transactions = []

for _, row in clean_df.iterrows():
    if row["risk_level"] in ["High", "Severe"]:
        high_risk_transactions.append(row["Transaction_ID"])

print("Number of high-risk transactions:", len(high_risk_transactions))

print(clean_df[["likelihood", "impact", "risk_score"]].describe())
print(clean_df["risk_level"].value_counts())

print(clean_df.sample(5)[[
    "Payment_Method",
    "Customer_Loyalty_Tier",
    "Transaction_Time",
    "Purchase_Amount",
    "likelihood",
    "impact",
    "risk_score",
    "risk_level"
]])