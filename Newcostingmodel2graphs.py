import streamlit as st
import pandas as pd
import altair as alt

# App Title
st.set_page_config(page_title="Costing Model: On-Prem vs Cloud API", layout="wide")

# 🔹 Custom CSS to Change Sidebar Color
sidebar_css = """
<style>
    [data-testid="stSidebar"] {
        background-color: #009999; /* Turquoise */
    }
    [data-testid="stSidebar"] * {
        color: white !important; /* White Sidebar Text */
    }
    
    /* Fix dropdown text color */
    [data-baseweb="select"] div {
        color: black !important; /* Keep dropdown text black */
    }
    
    /* Fix dropdown background */
    [data-baseweb="select"] {
        background-color: white !important; /* White Dropdown Background */
    }
    
    /* Make input boxes white with black text */
    input[type="text"], input[type="number"], textarea, .stTextInput input, .stNumberInput input {
        background-color: white !important;  /* White background */
        color: black !important;  /* Black text */
        border: 1px solid white !important;  /* White border */
    }

    /* Fix selectbox (dropdown) input field */
    .stSelectbox div[data-baseweb="select"] {
        background-color: white !important;
        color: black !important;
    }
</style>
"""

# Apply Sidebar Styling
st.markdown(sidebar_css, unsafe_allow_html=True)

st.title("📊 Cost Comparison: On-Premise vs Cloud API Deployment")

# Upload and Read Excel File
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    df = pd.read_excel(xls, sheet_name="Sheet1", header=None)
    
    # Extract cost tables from Excel
    gpu_costs = {"Nvidia A100 GPU": 23000, "Nvidia H100 GPU": 30000}
    cpu_costs = {"AMD EPYC 7282": 5000, "Intel Xeon Gold 6426Y": 1100}
    ram_costs = {"DDR4": 5000, "DDR5": 3000}
    server_initial_cost = 50000
    server_recurring_cost = 200
    maintenance_initial_cost = 0
    maintenance_recurring_cost = 850
    software_initial_cost = 1000
    software_recurring_cost = 850
    powerandcooling_initial_cost = 0
    powerandcooling_recurring_cost = 200
    storage_inital_cost = 150
    storage_recurring_cost = 0
    redundancy_initial_cost = 10000
    redundancy_recurring_cost = 0
    backup_intial_cost = 0
    backup_recurring_cost = 25
    staff_initial_cost = 0
    staff_recurring_cost = 12500
    switch_intial_cost = 5000
    switch_recurring_cost = 0
    cable_intial_cost = 1000
    cable_recurring_cost = 0

    api_costs = {
        "GPT-4o": {"input": 0.0000025, "output": 0.00000125},
        "GPT-4": {"input": 0.00003, "output": 0.00006},
        "3.2 Turbo (3B)": {"input": 0.00000006, "output": 0.00000006},
        "3.2 Reference (8B)": {"input": 0.0000002, "output": 0.0000002},
        "Claude 3.5 Sonnet": {"input": 0.000003, "output": 0.000015},
        "Claude 3.5 Haiku": {"input": 0.0000008, "output": 0.000004},
        "Claude 3 Opus": {"input": 0.000015, "output": 0.00001},
        "Gemini 1.5 Pro": {"input": 0.0000025, "output": 0.000004},
        "Gemini 1.0 Pro": {"input": 0.0000005, "output": 0.0000015},
        "DeepSeek chat": {"input": 0.00000027, "output": 0.0000011},
        "DeepSeek reasoner": {"input": 0.00000014, "output": 0.00000219},
    }
    
    # On-Prem Inputs
    st.sidebar.header("🔧 On-Premise Deployment")
    num_gpus = st.sidebar.number_input("Number of GPUs", min_value=1, value=8)
    num_cpus = st.sidebar.number_input("Number of CPUs", min_value=1, value=16)
    num_ram = st.sidebar.number_input("RAM (TB)", min_value=1, value=10)
    months_onprem = st.sidebar.number_input("📅 Months of Usage", min_value=1, value=24)
    selected_gpu = st.sidebar.selectbox("🖥️ Select GPU Provider", list(gpu_costs.keys()))
    selected_cpu = st.sidebar.selectbox("🧠 Select CPU Provider", list(cpu_costs.keys()))
    selected_ram = st.sidebar.selectbox("💾 Select RAM Type", list(ram_costs.keys()))
    
    # Compute total on-premise cost (split into initial and recurring)
    onprem_initial_cost = (
        (num_gpus * gpu_costs[selected_gpu]) + 
        (num_cpus * cpu_costs[selected_cpu]) +
        (num_ram * ram_costs[selected_ram]) + 
        server_initial_cost + maintenance_initial_cost + software_initial_cost + 
        powerandcooling_initial_cost + storage_inital_cost + redundancy_initial_cost + 
        backup_intial_cost + staff_initial_cost + switch_intial_cost + cable_intial_cost
    )
    
    onprem_recurring_cost = months_onprem * (
       server_recurring_cost + maintenance_recurring_cost + software_recurring_cost +
       powerandcooling_recurring_cost + storage_recurring_cost + redundancy_recurring_cost +
       backup_recurring_cost + staff_recurring_cost + switch_recurring_cost + cable_recurring_cost
    )
    
    total_onprem_cost = onprem_initial_cost + onprem_recurring_cost
    
    # Cloud API Inputs
    st.sidebar.header("☁️ Cloud API Deployment")
    num_users = st.sidebar.number_input("🧑 Number of Users", min_value=1, value=20)
    months_cloud = st.sidebar.number_input("📅 Months of API Usage", min_value=1, value=24)
    selected_api = st.sidebar.selectbox("🤖 Select API Model", list(api_costs.keys()))
    
    tokens_per_10user = 176300000  # Assuming each 10 users processes this many tokens per month
    tokens_range = list(range(176300000, 8150000000, 176300000))
    
    # Calculate **single** total cloud cost
    tokens_used = tokens_per_10user * (num_users / 10)
    cloud_cost = months_cloud * (
       (0.921837777 * tokens_used * api_costs[selected_api]["input"]) + (0.078162223 * tokens_used * api_costs[selected_api]["output"])
    )
    
    # Calculate **list** for graph
    cloud_costs_list = [
        ((num_users / 10) * months_cloud * (
            (0.921837777 * api_costs[selected_api]["input"]) + (0.078162223 * api_costs[selected_api]["output"])
        ) * tokens) for tokens in tokens_range
    ]

    # Display Cost Summary
    st.write("### 💰 Cost Summary")
    st.write("**On-Premise Initial Cost:** $", f"{onprem_initial_cost:,.2f}")
    st.write("**On-Premise Recurring Cost:** $", f"{onprem_recurring_cost:,.2f}")
    st.write("**🏢 Total On-Premise Cost:** $", f"{total_onprem_cost:,.2f}")
    st.write("**☁️ Total Cloud API Cost:** $", f"{cloud_cost:,.2f}")  # ✅ Fixed
    
    # Line Chart: Cost vs Number of Tokens with On-Prem cost as a horizontal line
    st.write("### 📈 Cost vs Number of Tokens")
   # Create separate DataFrames for Cloud API and On-Prem
cloud_api_df = pd.DataFrame({
    "Number of Tokens": tokens_range,
    "Cost (USD)": cloud_costs_list,
    "Type": ["Cloud API Cost"] * len(tokens_range),
})

on_prem_df = pd.DataFrame({
    "Number of Tokens": tokens_range,  # Repeat same x-values for consistency
    "Cost (USD)": [total_onprem_cost] * len(tokens_range),  # Constant cost
    "Type": ["On-Prem Cost"] * len(tokens_range),
})

# Combine both DataFrames
chart_data = pd.concat([cloud_api_df, on_prem_df], ignore_index=True)

# Create the chart
chart = alt.Chart(chart_data).mark_line().encode(
    x="Number of Tokens",
    y="Cost (USD)",
    color="Type"
).properties(title="Cloud API Cost Scaling vs On-Prem Cost")
st.write("This chart shows the cost comparison between On-Premise (independent of token usage) and Cloud API deployment for 8 billion+ tokens, which corresponds to roughly 450 users of Cloud API.")
st.altair_chart(chart, use_container_width=True)

# Compare this snippet from AllAPILInes.py:

 # Create separate DataFrames for Cloud API costs of all models
cloud_api_dfs = []

for model, rates in api_costs.items():
    cloud_costs_list = [
        ((num_users / 10) * months_cloud * (
            (0.921837777 * rates["input"]) + (0.078162223 * rates["output"])
        ) * tokens) for tokens in tokens_range
    ]
    df = pd.DataFrame({
        "Number of Tokens": tokens_range,
        "Cost (USD)": cloud_costs_list,
        "Type": model,
    })
    cloud_api_dfs.append(df)

# Combine all Cloud API data
cloud_api_df2 = pd.concat(cloud_api_dfs, ignore_index=True)

# On-Premise cost as a constant line
on_prem_df = pd.DataFrame({
    "Number of Tokens": tokens_range,  # Repeat same x-values for consistency
    "Cost (USD)": [total_onprem_cost] * len(tokens_range),  # Constant cost
    "Type": "On-Prem Cost",
})

# Combine both DataFrames
chart_data = pd.concat([cloud_api_df2, on_prem_df], ignore_index=True)

# Create the chart
chart = alt.Chart(chart_data).mark_line().encode(
    x=alt.X("Number of Tokens", scale=alt.Scale(type="log")),  # Log scale for readability
    y="Cost (USD)",
    color="Type"
).properties(title="Cloud API Cost Scaling vs On-Prem Cost")

st.write("This chart shows the cost comparison between On-Premise (independent of token usage) and Cloud API deployment for various models.")
st.altair_chart(chart, use_container_width=True) 
