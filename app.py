import io
from pathlib import Path

import pandas as pd
import streamlit as st

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="ICICI GTL Calculator",
    layout="wide"
)

st.title("ICICI GTL Calculator")

st.write(
    "Upload an Excel file. The calculator will keep all original columns and add "
    "Net Premium, GST Amount, and Gross Premium."
)

# --------------------------------------------------
# Constants
# --------------------------------------------------
GST_RATE = 0.18

RATE_OPTIONS = ["1125", "1012.50"]

RATE_MAP = {
    "1125": 1125.0,
    "1012.50": 1012.50,
}

# --------------------------------------------------
# Helper Functions
# --------------------------------------------------
def find_sum_assured_column(df: pd.DataFrame):
    normalized_map = {
        str(col).strip().lower().replace(" ", "").replace("_", ""): col
        for col in df.columns
    }

    possible_names = [
        "sumassured",
        "suminsured",
        "si",
    ]

    for name in possible_names:
        if name in normalized_map:
            return normalized_map[name]

    return None


def build_output(df: pd.DataFrame, selected_rate: str) -> pd.DataFrame:
    output_df = df.copy()

    sum_assured_col = find_sum_assured_column(output_df)

    if sum_assured_col is None:
        raise ValueError(
            "Sum Assured column not found. Expected one of: "
            "Sum Assured, Sum_Assured, Sum Insured, SI"
        )

    sum_assured = pd.to_numeric(
        output_df[sum_assured_col],
        errors="coerce"
    ).fillna(0)

    rate = RATE_MAP[selected_rate]

    # Gross Premium
    gross_premium = (sum_assured * rate) / 100000

    # Net Premium
    net_premium = gross_premium / (1 + GST_RATE)

    # GST Amount
    gst_amount = gross_premium - net_premium

    output_df["Net Premium"] = net_premium.round(2)
    output_df["GST Amount"] = gst_amount.round(2)
    output_df["Gross Premium"] = gross_premium.round(2)

    return output_df


def convert_to_excel(df: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(
            writer,
            index=False,
            sheet_name="Output"
        )

    buffer.seek(0)
    return buffer.getvalue()


# --------------------------------------------------
# UI
# --------------------------------------------------
selected_rate = st.selectbox(
    "Select Premium Rate",
    RATE_OPTIONS
)

uploaded_file = st.file_uploader(
    "Upload Excel File",
    type=["xlsx", "xls"]
)

# --------------------------------------------------
# Processing
# --------------------------------------------------
if uploaded_file is not None:
    try:
        input_df = pd.read_excel(uploaded_file)

        output_df = build_output(
            input_df,
            selected_rate
        )

        st.success("File processed successfully.")

        st.subheader("Preview")

        st.dataframe(
            output_df,
            use_container_width=True,
            height=500
        )

        output_file_name = (
            f"{Path(uploaded_file.name).stem}_output.xlsx"
        )

        st.download_button(
            label="Download Output Excel",
            data=convert_to_excel(output_df),
            file_name=output_file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Error: {e}")
