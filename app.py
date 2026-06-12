# ============================================
# IMPORT LIBRARIES
# ============================================

import streamlit as st
import pandas as pd
import numpy as np

# ============================================
# PAGE CONFIG
# ============================================

st.set_page_config(
    page_title="Insurance Premium Calculator",
    page_icon="💰",
    layout="wide"
)

# ============================================
# TITLE
# ============================================

st.title("💰 ICICI GTL Calculator")

st.markdown(
    "Upload any insurance Excel file for premium calculation"
)

# ============================================
# SETTINGS
# ============================================

GST_RATE = 0.18

rate_option = st.selectbox(
    "Select Premium Rate Per Lakh (GST Included)",
    [1125.00, 1012.15]
)

RATE_PER_LAKH_INCL_GST = rate_option
RATE_PER_LAKH_EXCL_GST = RATE_PER_LAKH_INCL_GST / (1 + GST_RATE)

# ============================================
# FILE UPLOAD
# ============================================

uploaded_file = st.file_uploader(
    "Upload Excel File",
    type=["xlsx"]
)

# ============================================
# PROCESS FILE
# ============================================

if uploaded_file is not None:

    try:

        # ============================================
        # READ FILE
        # ============================================

        df = pd.read_excel(uploaded_file)

        # ============================================
        # CLEAN COLUMN NAMES
        # ============================================

        df.columns = df.columns.str.strip()

        # ============================================
        # SHOW ORIGINAL DATA
        # ============================================

        st.subheader("Uploaded Data")
        st.dataframe(df.head())

        # ============================================
        # HANDLE MISSING COLUMNS
        # ============================================

        required_columns = [
            'Loan Account No.',
            'Name of Primary Loan borrower',
            'Mobile No',
            'Sum Assured'
        ]

        for col in required_columns:
            if col not in df.columns:
                df[col] = ""

        # ============================================
        # CLEAN SUM ASSURED
        # ============================================

        df['Sum Assured'] = pd.to_numeric(
            df['Sum Assured'],
            errors='coerce'
        ).fillna(0)

        # ============================================
        # OPTIONAL COLUMNS
        # ============================================

        if 'MAIN MEMBER AGE' not in df.columns:
            df['MAIN MEMBER AGE'] = 0

        if 'Loan Outstanding Amount' not in df.columns:
            df['Loan Outstanding Amount'] = 0

        # ============================================
        # PREMIUM CALCULATION
        # ============================================

        df['Premium Excl GST'] = (
            (df['Sum Assured'] / 100000)
            * RATE_PER_LAKH_EXCL_GST
        )

        # ============================================
        # GST CALCULATION
        # ============================================

        df['GST Amount'] = (
            df['Premium Excl GST'] * GST_RATE
        )

        df['Premium + GST'] = (
            df['Premium Excl GST'] + df['GST Amount']
        )

        # Round values
        df['Premium Excl GST'] = df['Premium Excl GST'].round(2)
        df['GST Amount'] = df['GST Amount'].round(2)
        df['Premium + GST'] = df['Premium + GST'].round(2)

        # ============================================
        # FINAL OUTPUT
        # ============================================

        output_columns = [
            'Loan Account No.',
            'Name of Primary Loan borrower',
            'Mobile No',
            'MAIN MEMBER AGE',
            'Sum Assured',
            'Premium Excl GST',
            'GST Amount',
            'Premium + GST'
        ]

        final_df = df[output_columns]

        # ============================================
        # DASHBOARD
        # ============================================

        st.subheader("Portfolio Summary")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Members", len(final_df))

        with col2:
            st.metric(
                "Total Sum Assured",
                f"₹ {final_df['Sum Assured'].sum():,.0f}"
            )

        with col3:
            st.metric(
                "Total Premium (Incl GST)",
                f"₹ {final_df['Premium + GST'].sum():,.2f}"
            )

        # ============================================
        # RATE INFO
        # ============================================

        st.info(
            f"Selected Rate: ₹{RATE_PER_LAKH_INCL_GST:,.2f} per lakh (GST Included)"
        )

        # ============================================
        # OUTPUT TABLE
        # ============================================

        st.subheader("Premium Calculation Output")
        st.dataframe(final_df, use_container_width=True)

        # ============================================
        # DOWNLOAD FILE
        # ============================================

        output_file = "ICICI_GTL_Output.xlsx"
        final_df.to_excel(output_file, index=False)

        with open(output_file, "rb") as file:
            st.download_button(
                label="⬇ Download Output Excel",
                data=file,
                file_name=output_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"Error: {e}")
