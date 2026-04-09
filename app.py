import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO

st.set_page_config(page_title="Day to Day Smart Catalog", layout="wide")

st.title("🛒 Retail Image Fetcher & Catalog Maker")
st.write("Upload your Price Change Excel and verify product images.")

# --- SIDEBAR: Upload Excel ---
st.sidebar.header("Upload Data")
uploaded_file = st.sidebar.file_uploader("Choose Excel File", type=["xlsx", "xls", "csv"])

if uploaded_file:
    # Load Data
    df = pd.read_excel(uploaded_file)
    st.success(f"Loaded {len(df)} items.")

    # --- MAIN UI ---
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📋 Price List Preview")
        st.dataframe(df, use_container_width=True)

    with col2:
        st.subheader("🖼️ Image Verification")
        selected_index = st.selectbox("Select Item to Check", df.index, format_func=lambda x: df.iloc[x]['DESCRIPTION'])
        
        item = df.iloc[selected_index]
        search_query = item['DESCRIPTION']
        
        st.info(f"Searching for: **{search_query}**")
        
        # Placeholder for auto-fetched image (Logic for real-time API would go here)
        st.write("---")
        
        # --- Drag & Drop / Copy Paste Section ---
        st.markdown("#### 📸 Manual Image Upload")
        st.caption("Drag and drop an image here if the search is wrong.")
        manual_image = st.file_uploader(f"Upload Image for {item['BARCODE']}", type=["jpg", "png", "jpeg"], key=item['BARCODE'])

        if manual_image:
            img = Image.open(manual_image)
            st.image(img, caption="Manual Upload Success", width=200)

# --- INSTRUCTIONS FOR GITHUB ---
with st.expander("🚀 How to host on GitHub"):
    st.markdown("""
    1. Create a new repository on GitHub.
    2. Upload this `app.py` file.
    3. Create a `requirements.txt` file and add:
       ```
       streamlit
       pandas
       openpyxl
       Pillow
       requests
       ```
    4. Go to [share.streamlit.io](https://share.streamlit.io) and connect your GitHub repo.
    """)
