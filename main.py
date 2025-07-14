import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import urllib

# Page Config
st.set_page_config(page_title="Dynamic SQL Dashboard", layout="centered")

# === UI for DB Connection ===
st.title("🗄️ SQL Server Connection")

with st.form("db_connection_form"):
    host = st.text_input("SQL Server Hostname or IP", value="localhost")
    port = st.text_input("Port", value="1433")
    db_name = st.text_input("Database Name")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    driver = st.selectbox("ODBC Driver", options=[
        "ODBC Driver 18 for SQL Server",
        "ODBC Driver 17 for SQL Server"
    ])
    connect_btn = st.form_submit_button("Connect")

# Session state to persist connection
if "connected" not in st.session_state:
    st.session_state.connected = False
    st.session_state.engine = None

# === Try Connecting ===
if connect_btn:
    try:
        params = urllib.parse.quote_plus(
            f"DRIVER={driver};SERVER={host},{port};DATABASE={db_name};UID={username};PWD={password};TrustServerCertificate=yes"
        )
        db_url = f"mssql+pyodbc:///?odbc_connect={params}"
        engine = create_engine(db_url)

        with engine.connect() as conn:
            conn.execute("SELECT 1")  # Test connection

        st.session_state.connected = True
        st.session_state.engine = engine
        st.success("✅ Connected to SQL Server database successfully.")

    except Exception as e:
        st.session_state.connected = False
        st.session_state.engine = None
        st.error(f"❌ Database connection failed: {e}")

# === Query Form ===
if st.session_state.connected and st.session_state.engine:
    st.title("🔍 Product Report Dashboard")
    st.header("Query Product Data")

    with st.form("query_form"):
        location = st.text_input("Location")
        gf_number = st.text_input("GF Number")
        order_id = st.text_input("Order ID")
        query_submitted = st.form_submit_button("Run Query")

        if query_submitted:
            if not all([location, gf_number, order_id]):
                st.warning("⚠️ All fields are required.")
            else:
                query = """
                    SELECT *
                    FROM product_orders
                    WHERE location = ? AND gf_number = ? AND order_id = ?
                """
                try:
                    with st.session_state.engine.connect() as conn:
                        df = pd.read_sql_query(query, conn, params=(location, gf_number, order_id))

                    if df.empty:
                        st.info("No records found.")
                    else:
                        st.success(f"✅ Found {len(df)} records.")
                        st.dataframe(df)

                        # CSV Download
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button("📥 Download CSV", data=csv, file_name="product_report.csv", mime="text/csv")

                except Exception as e:
                    st.error(f"❌ Error running query: {e}")
