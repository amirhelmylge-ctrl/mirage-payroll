import streamlit as st
import pandas as pd
import os

# 1. Page Configuration
st.set_page_config(
    page_title="Mirage Payroll Portal",
    page_icon="💼",
    layout="centered"
)

# 2. Custom UI Styling
st.markdown("""
    <style>
    .main { background-color: #F3F4F6; }
    .stButton>button { 
        width: 100%; 
        background-color: #2563EB; 
        color: white; 
        font-weight: bold; 
        border-radius: 8px; 
        padding: 10px; 
    }
    .stButton>button:hover { 
        background-color: #1D4ED8; 
        color: white; 
    }
    </style>
""", unsafe_allow_html=True)

# 3. Load and Process Employee Data from Excel
@st.cache_data
def load_employee_data():
    excel_path = "فنيين ميراج.xlsx"
    if not os.path.exists(excel_path):
        return None
    
    try:
        # Read both sheets
        df1 = pd.read_excel(excel_path, sheet_name='Sheet1')
        df2 = pd.read_excel(excel_path, sheet_name='Sheet2')
        
        # Clean Sheet 1 (contains salary)
        df1['Base Salary'] = pd.to_numeric(df1['الراتب الاساسي'], errors='coerce').fillna(5000)
        df1_clean = df1[['الاسم', 'الرقم القومي', 'Base Salary']].copy()
        
        # Clean Sheet 2 (default base salary to 5000 if not listed)
        df2_clean = df2[['الاسم', 'الرقم القومي']].copy()
        df2_clean['Base Salary'] = 5000
        
        # Combine sheets
        combined = pd.concat([df1_clean, df2_clean], ignore_index=True)
        
        # Drop rows with missing National ID or Name
        combined = combined.dropna(subset=['الرقم القومي', 'الاسم'])
        
        # Format columns as strings and clean whitespace
        combined['Employee ID'] = combined['الرقم القومي'].astype(str).str.strip()
        combined['Full Name'] = combined['الاسم'].astype(str).str.strip()
        
        # Generate default password (last 4 digits of National ID)
        combined['Password'] = combined['Employee ID'].apply(lambda x: x[-4:] if len(x) >= 4 else x)
        
        return combined
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
        return None

df = load_employee_data()

if df is None or df.empty:
    st.error("⚠️ Could not load 'فنيين ميراج.xlsx'. Please ensure the Excel file is uploaded to the root of your GitHub repository.")
    st.stop()

# 4. Session State Management for Login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.employee = None

# 5. Login View
if not st.session_state.logged_in:
    st.title("💼 Mirage Employee Portal")
    st.subheader("بوابة موظفي ميراج - تسجيل الدخول")
    st.write("الرجاء إدخال الرقم القومي (اسم المستخدم) وكلمة المرور.")

    with st.form("login_form"):
        emp_id_input = st.text_input("Employee ID (الرقم القومي)")
        password_input = st.text_input("Password (كلمة المرور)", type="password")
        submit_btn = st.form_submit_button("تسجيل الدخول / Login")

        if submit_btn:
            clean_id = emp_id_input.strip()
            clean_pass = password_input.strip()
            
            matching_rows = df[df['Employee ID'] == clean_id]
            
            if not matching_rows.empty:
                stored_pass = str(matching_rows.iloc[0]['Password'])
                if clean_pass == stored_pass:
                    st.session_state.logged_in = True
                    st.session_state.employee = matching_rows.iloc[0].to_dict()
                    st.rerun()
                else:
                    st.error("❌ كلمة المرور غير صحيحة. (Incorrect Password)")
            else:
                st.error("❌ رقم الموظف (الرقم القومي) غير موجود. (ID Not Found)")

# 6. Authenticated Employee Dashboard View
else:
    emp = st.session_state.employee
    st.title(f"Welcome, {emp['Full Name']} 👋")
    st.write(f"**Employee ID (الرقم القومي):** {emp['Employee ID']}")

    if st.button("تسجيل الخروج / Logout"):
        st.session_state.logged_in = False
        st.session_state.employee = None
        st.rerun()

    st.markdown("---")
    st.subheader("📊 تفاصيل الراتب الشهري (Monthly Salary Details)")

    base_salary = float(emp['Base Salary'])
    
    # Input fields for attendance, bonuses, and cuts
    col1, col2 = st.columns(2)
    with col1:
        days_off = st.number_input("Days Off (أيام الراحة / الغياب)", min_value=0, value=0, step=1)
        days_late = st.number_input("Days Late (أيام التأخير)", min_value=0, value=0, step=1)
    with col2:
        bonuses = st.number_input("Bonuses (المكافآت)", min_value=0.0, value=0.0, step=50.0)
        salary_cuts = st.number_input("Salary Cuts (الخصومات)", min_value=0.0, value=0.0, step=50.0)

    # Net Salary Calculation Formula
    final_salary = base_salary + bonuses - salary_cuts

    st.markdown("---")
    
    # Metric Summary Cards
    m1, m2, m3 = st.columns(3)
    m1.metric("الراتب الأساسي (Base Salary)", f"${base_salary:,.2f}")
    m2.metric("المكافآت والخصومات", f"+${bonuses:,.2f} / -${salary_cuts:,.2f}")
    m3.metric("صافي الراتب النهائي (Final Net Salary)", f"${final_salary:,.2f}")
