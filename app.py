import streamlit as st
import pandas as pd
from PIL import Image
from fpdf import FPDF
import os

# --- PAGE SETUP & DARK THEME ---
st.set_page_config(page_title="Day to Day Smart Catalog", layout="wide")

st.markdown("""
    <style>
    .stDataFrame { border: 1px solid #444; }
    .main { background-color: #0e1117; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛒 Day to Day: Smart Image Catalog")
st.write("Upload your Price List Excel, link images, and export to PDF.")

# --- SIDEBAR: UPLOAD DATA ---
st.sidebar.header("📁 Data Source")
uploaded_file = st.sidebar.file_uploader("Upload Price Change Excel", type=["xlsx", "xls", "csv"])

if uploaded_file:
    # 1. LOAD AND CLEAN DATA
    df = pd.read_excel(uploaded_file)
    
    # Smart Column Cleaning (Fixes KeyError for misspelled headers)
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    possible_desc = ['DESCRIPTION', 'PRICE CHAGE', 'ITEM', 'PRODUCT', 'NAME']
    desc_col = next((c for c in df.columns if c in possible_desc), df.columns[0])
    
    # Format Barcode
    if 'BARCODE' in df.columns:
        df['BARCODE'] = df['BARCODE'].astype(str).str.replace(".0", "", regex=False)
    else:
        st.error("Error: Could not find a 'BARCODE' column in your Excel.")
        st.stop()

    # Image Storage in Session
    if 'image_store' not in st.session_state:
        st.session_state.image_store = {}

    # 2. MAIN UI LAYOUT
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📋 Product List")
        
        # Search Box
        search = st.text_input("Search Item by Name or Barcode")
        if search:
            display_df = df[df[desc_col].astype(str).str.contains(search, case=False) | df['BARCODE'].str.contains(search)]
        else:
            display_df = df
        
        # Dropdown selection
        selected_index = st.selectbox(
            "Select Item to Edit Image", 
            display_df.index, 
            format_func=lambda x: str(display_df.loc[x, desc_col])
        )
        item_data = display_df.loc[selected_index]

    with col2:
        st.subheader("🖼️ Image Manager")
        barcode = item_data['BARCODE']
        item_name = item_data[desc_col]
        
        st.info(f"**Item:** {item_name}\n\n**Barcode:** {barcode}")

        # Show existing image
        if barcode in st.session_state.image_store:
            st.image(st.session_state.image_store[barcode], caption="Current Image", width=250)
        else:
            st.warning("No image linked yet. Drag & Drop or Copy-Paste below.")

        # Uploader logic
        uploaded_img = st.file_uploader(f"Upload Image", type=["jpg", "png", "jpeg"], key=f"uploader_{barcode}")
        
        if uploaded_img:
            img = Image.open(uploaded_img).convert("RGB")
            st.session_state.image_store[barcode] = img
            st.success("✅ Image Linked to Barcode!")

    # 3. PDF EXPORT SECTION
    st.divider()
    if st.button("📄 Generate PDF Catalog"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "DAY TO DAY PRICE LIST", ln=True, align='C')
        pdf.ln(10)

        # PDF Table Headers
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(30, 10, "IMAGE", border=1, align='C')
        pdf.cell(40, 10, "BARCODE", border=1, align='C')
        pdf.cell(90, 10, "DESCRIPTION", border=1, align='C')
        pdf.cell(30, 10, "PRICE", border=1, align='C', ln=True)

        pdf.set_font("Arial", '', 9)

        for index, row in df.iterrows():
            b_code = str(row['BARCODE'])
            d_name = str(row[desc_col])
            
            # Find price column safely
            price_col = 'NEW PRICE' if 'NEW PRICE' in df.columns else df.columns[-1]
            price = str(row[price_col])

            x = pdf.get_x()
            y = pdf.get_y()
            
            # Draw empty image cell
            pdf.cell(30, 20, "", border=1)
            
            # Insert Image if exists
            if b_code in st.session_state.image_store:
                img_path = f"temp_{b_code}.jpg"
                st.session_state.image_store[b_code].save(img_path)
                pdf.image(img_path, x + 5, y + 2, 20, 16)
                os.remove(img_path)
            
            # Draw text cells
            pdf.set_xy(x + 30, y)
            pdf.cell(40, 20, b_code, border=1, align='C')
            pdf.cell(90, 20, d_name[:50], border=1, align='L') # Cutoff long names
            pdf.cell(30, 20, price, border=1, align='C', ln=True)

        # Save and Download
        pdf_output = pdf.output(dest='S').encode('latin-1')
        st.download_button(
            label="📥 Download Final PDF", 
            data=pdf_output, 
            file_name="DayToDay_Catalog.pdf", 
            mime="application/pdf"
        )
