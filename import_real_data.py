"""
Guide untuk mengimport dataset REAL dari file CSV/Excel.

Langkah-langkah:
1. Persiapkan dataset Anda
2. Taruh di folder data/raw/
3. Rename sesuai kebutuhan atau gunakan script ini untuk map kolom
"""

import pandas as pd
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from churn_intel.settings import CUSTOMERS_CSV, DATA_RAW_DIR


def import_real_data(source_file: str, column_mapping: dict = None):
    """
    Import dataset real dan map kolom ke format yang diharapkan.
    
    Args:
        source_file: Path ke file CSV/Excel Anda
        column_mapping: Dict untuk rename kolom
                       contoh: {"age": "customer_age", "balance": "account_balance"}
    
    Expected columns (minimal):
        - customer_age (int): Umur pelanggan
        - account_balance (float): Saldo akun
        - tenure_months (int): Berapa bulan menjadi pelanggan
        - total_transactions (int): Total transaksi
        - is_premium (str): "yes" atau "no"
        - support_tickets (int): Jumlah tiket support
        - avg_order_value (float): Rata-rata nilai order
        - churn (int): 0 atau 1 (target variable)
    
    Returns:
        bool: True jika berhasil, False jika gagal
    """
    
    try:
        source_path = Path(source_file)
        
        # Baca file
        if source_path.suffix == '.xlsx':
            df = pd.read_excel(source_path)
            print(f"✅ Membaca Excel: {source_path}")
        else:
            df = pd.read_csv(source_path)
            print(f"✅ Membaca CSV: {source_path}")
        
        print(f"   Records: {len(df)}")
        print(f"   Kolom saat ini: {list(df.columns)}")
        
        # Map kolom jika diperlukan
        if column_mapping:
            print(f"\n🔄 Mapping kolom...")
            df = df.rename(columns=column_mapping)
            print(f"   Kolom baru: {list(df.columns)}")
        
        # Validasi kolom required
        required_cols = [
            'customer_age', 'account_balance', 'tenure_months',
            'total_transactions', 'is_premium', 'support_tickets',
            'avg_order_value', 'churn'
        ]
        
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            print(f"\n❌ Error: Kolom yang hilang: {missing}")
            print(f"   Kolom yang ada: {list(df.columns)}")
            print(f"\n   Contoh mapping untuk memperbaiki:")
            print(f"   column_mapping = {{")
            for col in missing:
                print(f"       # '{col}': 'nama_kolom_di_file_anda',")
            print(f"   }}")
            return False
        
        # Clean data
        print(f"\n🧹 Cleaning data...")
        df = df[required_cols]  # Select only required columns
        df['is_premium'] = df['is_premium'].astype(str).str.lower().map({'yes': 'yes', 'no': 'no', '1': 'yes', '0': 'no'})
        df['churn'] = df['churn'].astype(int).clip(0, 1)
        
        # Remove nulls
        initial_count = len(df)
        df = df.dropna()
        removed = initial_count - len(df)
        if removed > 0:
            print(f"   ⚠️  Removed {removed} rows dengan missing values")
        
        print(f"   ✅ Final records: {len(df)}")
        
        # Statistics
        print(f"\n📊 Data Statistics:")
        print(f"   • Churn rate: {df['churn'].mean():.1%}")
        print(f"   • Premium rate: {(df['is_premium'] == 'yes').mean():.1%}")
        print(f"   • Avg tenure: {df['tenure_months'].mean():.1f} months")
        print(f"   • Avg balance: ${df['account_balance'].mean():,.2f}")
        
        # Save
        DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(CUSTOMERS_CSV, index=False)
        
        print(f"\n✅ Data berhasil disimpan ke: {CUSTOMERS_CSV}")
        print(f"   Siap untuk Streamlit app!")
        print(f"\n   Jalankan: streamlit run app/streamlit_app.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {str(e)}")
        return False


def get_column_mapping_example():
    """Print contoh column mapping untuk berbagai format dataset."""
    
    print("""
╔════════════════════════════════════════════════════════════════╗
║           CONTOH COLUMN MAPPING UNTUK FORMAT BERBEDA          ║
╚════════════════════════════════════════════════════════════════╝

Format 1: Kaggle Churn Dataset
─────────────────────────────
column_mapping = {
    'Age': 'customer_age',
    'Balance': 'account_balance',
    'Tenure': 'tenure_months',
    'NumOfProducts': 'total_transactions',
    'IsActiveMember': 'is_premium',  # 1=yes, 0=no
    'NumTickets': 'support_tickets',
    'EstimatedSalary': 'avg_order_value',
    'Exited': 'churn'
}

Format 2: E-Commerce Dataset
──────────────────────────
column_mapping = {
    'customer_age_years': 'customer_age',
    'account_balance_usd': 'account_balance',
    'months_as_customer': 'tenure_months',
    'purchase_count': 'total_transactions',
    'membership_tier': 'is_premium',  # 'premium'/'standard'
    'support_requests': 'support_tickets',
    'avg_purchase_value': 'avg_order_value',
    'customer_churn_binary': 'churn'
}

Format 3: Telecom Dataset
──────────────────────────
column_mapping = {
    'Age': 'customer_age',
    'MonthlyCharges': 'account_balance',
    'tenure': 'tenure_months',
    'TotalCharges': 'total_transactions',
    'Contract': 'is_premium',  # 'Month-to-month'/'Two year'
    'TechSupport': 'support_tickets',  # 'Yes'/'No'
    'MonthlyCharges': 'avg_order_value',
    'Churn': 'churn'  # 'Yes'/'No'
}

Format 4: SaaS/Subscription Dataset
────────────────────────────────
column_mapping = {
    'user_age': 'customer_age',
    'annual_value': 'account_balance',
    'months_active': 'tenure_months',
    'api_calls_count': 'total_transactions',
    'plan_type': 'is_premium',  # 'pro'/'free'
    'support_tickets_opened': 'support_tickets',
    'avg_transaction_value': 'avg_order_value',
    'churned': 'churn'  # True/False atau 1/0
}
    """)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python import_real_data.py /path/to/your/data.csv")
        print("  python import_real_data.py /path/to/your/data.xlsx")
        print("\nContoh:")
        print("  python import_real_data.py data/raw/my_churn_data.csv")
        print("  python import_real_data.py ../external_data/customers.xlsx")
        print("\nUntuk melihat contoh column mapping:")
        print("  python import_real_data.py --show-examples")
        sys.exit(1)
    
    if sys.argv[1] == "--show-examples":
        get_column_mapping_example()
        sys.exit(0)
    
    source = sys.argv[1]
    import_real_data(source)
