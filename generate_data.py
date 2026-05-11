"""
Helper script untuk generate/regenerate data synthetic.

Usage:
    python generate_data.py                  # Generate default 2000 records
    python generate_data.py 5000            # Generate 5000 records
    python generate_data.py 500 --replace   # Generate 500 records (replace existing)
"""

import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from churn_intel.synthetic_data import create_synthetic_churn_data
from churn_intel.settings import CUSTOMERS_CSV, DATA_RAW_DIR


def main():
    """Generate synthetic data with CLI arguments."""
    
    # Parse arguments
    n_samples = 2000
    replace = False
    
    if len(sys.argv) > 1:
        try:
            n_samples = int(sys.argv[1])
        except ValueError:
            print(f"❌ Error: '{sys.argv[1]}' bukan angka valid")
            sys.exit(1)
    
    if "--replace" in sys.argv or "-r" in sys.argv:
        replace = True
    
    # Check if file exists
    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    
    if CUSTOMERS_CSV.exists() and not replace:
        print(f"⚠️  File sudah ada: {CUSTOMERS_CSV}")
        print(f"   Records saat ini: {len(__import__('pandas').read_csv(CUSTOMERS_CSV))}")
        print(f"\n   Untuk membuat ulang, gunakan: python generate_data.py {n_samples} --replace")
        return
    
    # Generate data
    print(f"🔄 Generating {n_samples:,} synthetic customer records...")
    df = create_synthetic_churn_data(n_samples=n_samples)
    
    # Save
    df.to_csv(CUSTOMERS_CSV, index=False)
    
    # Statistics
    print(f"✅ Data generated successfully!")
    print(f"\n📊 Dataset Statistics:")
    print(f"   • Lokasi: {CUSTOMERS_CSV}")
    print(f"   • Total records: {len(df):,}")
    print(f"   • Churn rate: {df['churn'].mean():.1%}")
    print(f"   • Kolom: {', '.join(df.columns)}")
    print(f"\n   Kolom detail:")
    for col in df.columns:
        if df[col].dtype == 'object':
            print(f"   • {col:20} (string): {df[col].nunique()} unique values")
        else:
            print(f"   • {col:20} (numeric): min={df[col].min():.2f}, max={df[col].max():.2f}")
    
    print(f"\n✨ Data siap digunakan untuk Streamlit app!")
    print(f"   Jalankan: streamlit run app/streamlit_app.py")


if __name__ == "__main__":
    main()
