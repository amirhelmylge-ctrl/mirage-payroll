import streamlit as st
import pandas as pd

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

st.title("💼 Mirage Employee Portal")

# 3. Sidebar: File Uploader & HR Admin Toggle
st.sidebar.header("📁 لوحة تحكم الإدارة (HR Panel)")
uploaded_file = st.sidebar.file_uploader("قم بتحديث ملف الاكسل (Upload Excel)", type=["xlsx", "xls"])

# HR Admin Authentication Section in Sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("🔒 وضع المسؤول (HR Admin)")
admin_password_input = st.sidebar.text_input("Admin Passcode", type="password")
# Change this secret admin pass to whatever you prefer!
ADMIN_SECRET_KEY = "miragehr2026" 

is_hr_admin = (admin_password_input.strip() == ADMIN_SECRET_KEY)

if is_hr_admin:
    st.sidebar.success("✅ HR Admin Mode Active")

# Function to load and process data
@st.cache_data
def process_excel(file):
    try:
        xls = pd.ExcelFile(file)
        sheet_names = xls.sheet_names
        
        df1 = pd.read_excel(file, sheet_name=sheet_names[0])
        
        # Clean Sheet 1 (contains salary)
        if 'الراتب الاساسي' in df1.columns:
            df1['Base Salary'] = pd.to_numeric(df1['الراتب الاساسي'], errors='coerce').fillna(5000)
        else:
            df1['Base Salary'] = 5000
            
        df1_clean = df1[['الاسم', 'الرقم القومي', 'Base Salary']].copy()
        
        # Optional: Check if second sheet exists
        if len(sheet_names) > 1:
            df2 = pd.read_excel(file, sheet_name=sheet_names[1])
            df2_clean = df2[['الاسم', 'الرقم القومي']].copy()
            df2_clean['Base Salary'] = 5000
            combined = pd.concat([df1_clean, df2_clean], ignore_index=True)
        else:
            combined = df1_clean
            
        # Clean and filter data
        combined = combined.dropna(subset=['الرقم القومي', 'الاسم'])
        combined['Employee ID'] = combined['الرقم القومي'].astype(str).str.strip()
        combined['Full Name'] = combined['الاسم'].astype(str).str.strip()
        combined['Password'] = combined['Employee ID'].apply(lambda x: x[-4:] if len(x) >= 4 else x)
        
        return combined
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None

# Manage data state
if uploaded_file is not None:
    df = process_excel(uploaded_file)
    st.session_state['df'] = df
else:
    if 'df' in st.session_state:
        df = st.session_state['df']
    else:
        df = None

if df is None:
    st.info("👈 Please upload your company Excel file using the sidebar to start the portal.")
    st.stop()

# Session State Management for Employee Login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.employee = None

# If HR Admin mode is active, show the HR Management Dashboard
if is_hr_admin:
    st.markdown("---")
    st.subheader("🛠️ لوحة تحكم الموارد البشرية (HR Management Dashboard)")
    st.write("يمكنك مراجعة وتعديل بيانات الرواتب للموظفين مباشرة أدناه:")
    
    # Editable DataFrame for HR
    edited_df = st.data_editor(st.session_state['df'][['Full Name', 'Employee ID', 'Base Salary']], num_rows="dynamic", use_container_width=True)
    
    if st.button("حفظ التعديلات (Save Salary Changes)"):
        # Update the session state dataframe with the newly edited base salaries
        for idx, row in edited_df.iterrows():
            emp_id = row['Employee ID']
            new_base = row['Base Salary']
            st.session_state['df'].loc[st.session_state['df']['Employee ID'] == emp_id, 'Base Salary'] = new_base
        st.success("✅ تم تحديث الرواتب بنجاح!")
    
    st.markdown("---")

# Regular Employee Login View
if not st.session_state.logged_in:
    st.subheader("تسجيل الدخول للموظفين (Employee Login)")
    st.write("الرجاء إدخال الرقم القومي (اسم المستخدم) وكلمة المرور الخاصة بك.")

    with st.form("login_form"):
        emp_id_input = st.text_input("Employee ID (الرقم القومي)")
        password_input = st.text_input("Password (كلمة المرور)", type="password")
        submit_btn = st.form_submit_button("تسجيل الدخول / Login")

        if submit_btn:
            clean_id = emp_id_input.strip()
            clean_pass = password_input.strip()
            
            matching_rows = st.session_state['df'][st.session_state['df']['Employee ID'] == clean_id]
            
            if not matching_rows.empty:
                stored_pass = str(matching_rows.iloc[0]['Password'])
                if clean_pass == stored_pass:
                    st.session_state.logged_in = True
                    st.session_state.employee = matching_rows.iloc[0].to_dict()
                    st.rerun()
                else:
                    st.error("❌ كلمة المرور غير صحيحة.")
            else:
                st.error("❌ رقم الموظف (الرقم القومي) غير موجود.")

# Authenticated Employee Dashboard View
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

    # Fetch latest base salary from session state in case HR updated it
    current_emp_row = st.session_state['df'][st.session_state['df']['Employee ID'] == emp['Employee ID']]
    base_salary = float(current_emp_row.iloc[0]['Base Salary'])
    
    col1, col2 = st.columns(2)
    with col1:
        days_off = st.number_input("Days Off (أيام الراحة / الغياب)", min_value=0, value=0, step=1)
        days_late = st.number_input("Days Late (أيام التأخير)", min_value=0, value=0, step=1)
    with col2:
        bonuses = st.number_input("Bonuses (المكافآت)", min_value=0.0, value=0.0, step=50.0)
        salary_cuts = st.number_input("Salary Cuts (الخصومات)", min_value=0.0, value=0.0, step=50.0)

    final_salary = base_salary + bonuses - salary_cuts

    st.markdown("---")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("الراتب الأساسي (Base Salary)", f"${base_salary:,.2f}")
    m2.metric("المكافآت والخصومات", f"+${bonuses:,.2f} / -${salary_cuts:,.2f}")
    m3.metric("صافي الراتب النهائي (Final Net Salary)", f"${final_salary:,.2f}")
