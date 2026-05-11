"""
.streamlit/config.toml - REFERENCE GUIDE

Lokasi: .streamlit/config.toml
Status: Sudah ada dengan default optimal

Opsi untuk customize:
"""

# ╔════════════════════════════════════════════════════════════════╗
# ║            THEME - Ubah warna/styling aplikasi                ║
# ╚════════════════════════════════════════════════════════════════╝

# ✅ CURRENT (Dark Theme - Recommended)
# [theme]
# primaryColor = "#22d3ee"              # Warna aksen (cyan)
# backgroundColor = "#050816"           # Latar belakang (dark navy)
# secondaryBackgroundColor = "#111928"  # Latar belakang secondary
# textColor = "#eef2ff"                 # Warna teks (light gray)
# font = "sans serif"


# ⚫ ALTERNATIVE: Full Dark Theme (Minimal)
# [theme]
# primaryColor = "#22d3ee"
# backgroundColor = "#0a0e27"
# secondaryBackgroundColor = "#1a1f3a"
# textColor = "#ffffff"
# font = "sans serif"


# 🔵 ALTERNATIVE: Blue Theme
# [theme]
# primaryColor = "#0ea5e9"              # Sky blue
# backgroundColor = "#0f172a"           # Slate dark
# secondaryBackgroundColor = "#1e293b"  # Slate medium
# textColor = "#f1f5f9"                 # Slate light
# font = "sans serif"


# 🟣 ALTERNATIVE: Purple Theme
# [theme]
# primaryColor = "#a78bfa"              # Purple
# backgroundColor = "#1f1535"           # Dark purple
# secondaryBackgroundColor = "#2d1b4e"  # Medium purple
# textColor = "#e9d5ff"                 # Light purple
# font = "sans serif"


# ╔════════════════════════════════════════════════════════════════╗
# ║           BROWSER - Kontrol perilaku browser                   ║
# ╚════════════════════════════════════════════════════════════════╝

# [browser]
# gatherUsageStats = false  # Tidak kirim analytics ke Streamlit


# ╔════════════════════════════════════════════════════════════════╗
# ║          LOGGER - Kontrol logging level                        ║
# ╚════════════════════════════════════════════════════════════════╝

# [logger]
# level = "info"  # Options: debug, info, warning, error


# ╔════════════════════════════════════════════════════════════════╗
# ║          CLIENT - Kontrol maksimal file upload, dll            ║
# ╚════════════════════════════════════════════════════════════════╝

# [client]
# maxUploadSize = 200  # Max upload size dalam MB


# ╔════════════════════════════════════════════════════════════════╗
# ║        SERVER - Port, timeout, dan server settings             ║
# ╚════════════════════════════════════════════════════════════════╝

# [server]
# port = 8501                    # Port default
# address = "localhost"          # Host
# headless = true                # Run without web browser
# runOnSave = true              # Rerun saat file berubah
# maxUploadSize = 200            # Max upload (MB)
# enableXsrfProtection = true   # Security


# ╔════════════════════════════════════════════════════════════════╗
# ║            MAPBOX - Jika menggunakan map features              ║
# ╚════════════════════════════════════════════════════════════════╝

# [mapbox]
# token = "your_mapbox_token"


# ╔════════════════════════════════════════════════════════════════╗
# ║          DEPRECATION - Kontrol warning lama                    ║
# ╚════════════════════════════════════════════════════════════════╝

# [deprecation]
# showPyplotGlobalUse = false


# ╔════════════════════════════════════════════════════════════════╗
# ║          EXAMPLE: Advanced Config (Production)                 ║
# ╚════════════════════════════════════════════════════════════════╝

# [theme]
# primaryColor = "#22d3ee"
# backgroundColor = "#050816"
# secondaryBackgroundColor = "#111928"
# textColor = "#eef2ff"
# font = "sans serif"
#
# [browser]
# gatherUsageStats = false
#
# [server]
# port = 8501
# address = "0.0.0.0"           # Accessible dari network
# headless = true
# runOnSave = true
# maxUploadSize = 500           # 500 MB max upload
#
# [logger]
# level = "info"
#
# [client]
# maxUploadSize = 500


# ╔════════════════════════════════════════════════════════════════╗
# ║                   NOTES UNTUK PRODUCTION                       ║
# ╚════════════════════════════════════════════════════════════════╝

# Untuk deployment production:
#
# 1. Gunakan environment variables untuk sensitive config:
#    $ export STREAMLIT_SERVER_PORT=8501
#    $ export STREAMLIT_SERVER_ADDRESS=0.0.0.0
#
# 2. Settings priority (highest to lowest):
#    - Command line flags: streamlit run app.py --server.port 8080
#    - Environment variables: STREAMLIT_SERVER_PORT=8080
#    - config.toml file
#    - Default values
#
# 3. Security recommendations:
#    - runOnSave = false (production)
#    - enableXsrfProtection = true
#    - gatherUsageStats = false
#    - Validate semua user inputs
#
# 4. Performance:
#    - maxUploadSize tergantung server resources
#    - Gunakan caching: @st.cache_data
#    - Monitor memory usage

"""

print(__doc__)
