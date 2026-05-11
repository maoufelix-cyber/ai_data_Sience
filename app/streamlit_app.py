import streamlit as st
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler

MODEL_PATH = "models/customer_churn_model.joblib"

@st.cache_data
def load_model(path):
    return joblib.load(path)

@st.cache_data
def load_sample_data():
    return pd.DataFrame(
        [
            {
                "customer_age": 35,
                "account_balance": 54000,
                "tenure_months": 24,
                "total_transactions": 12,
                "is_premium": "no",
                "support_tickets": 1,
                "avg_order_value": 185.0,
            }
        ]
    )

st.title("Dashboard Prediksi Churn Pelanggan")
st.markdown(
    "Gunakan antarmuka ini untuk melihat bagaimana fitur pelanggan berdampak pada prediksi churn."
)

model = load_model(MODEL_PATH)
input_data = load_sample_data()

with st.form("input_form"):
    st.subheader("Input Data Pelanggan")
    customer_age = st.number_input("Usia pelanggan", min_value=18, max_value=90, value=35)
    account_balance = st.number_input("Saldo akun", min_value=0, value=54000)
    tenure_months = st.number_input("Lama langganan (bulan)", min_value=0, max_value=120, value=24)
    total_transactions = st.number_input("Total transaksi", min_value=0, max_value=200, value=12)
    is_premium = st.selectbox("Member premium?", ["yes", "no"])
    support_tickets = st.number_input("Jumlah tiket dukungan", min_value=0, max_value=20, value=1)
    avg_order_value = st.number_input("Nilai pesanan rata-rata", min_value=0.0, value=185.0)
    submit = st.form_submit_button("Prediksi Churn")

if submit:
    sample = pd.DataFrame(
        [
            {
                "customer_age": customer_age,
                "account_balance": account_balance,
                "tenure_months": tenure_months,
                "total_transactions": total_transactions,
                "is_premium": is_premium,
                "support_tickets": support_tickets,
                "avg_order_value": avg_order_value,
            }
        ]
    )
    prediction = model.predict(sample)
    probability = model.predict_proba(sample)[:, 1][0]

    st.write("## Hasil Prediksi")
    st.write("- Prediksi churn: **Ya**" if prediction[0] == 1 else "- Prediksi churn: **Tidak**")
    st.write(f"- Probabilitas churn: **{probability:.2%}**")
    st.write(
        "Gunakan hasil ini untuk menentukan pelanggan yang perlu ditangani oleh tim retensi."
    )

st.markdown("---")
st.write("## Contoh Data Pelanggan")
st.dataframe(input_data)
