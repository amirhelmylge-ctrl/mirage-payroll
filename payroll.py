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

# 3. CRITICAL: Initialize ALL Session State variables safely at the very top
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "employee" not in st.session_state:
    st.session_state.employee = None
if "df" not in st.session_state:
    st.session_state.df = None

# Admin Secret Passcode
ADMIN_SECRET_KEY = "miragehr2026"

# 4. Sidebar: HR Admin Login Section
with st.sidebar:
    st.header("🔒 بوابة الإدارة (HR Admin)")
    admin_pass_input = st.text_input("أدخل كلمة مرور المسؤول", type="password")
    
    if admin_pass_input.strip() == ADMIN_SECRET_KEY:
        st.session_state.is_admin = True
        st.success("✅ تم تفعيل صلاحيات المسؤول")
    else:
        if admin_pass_input.strip() != "":
            st.error("❌ كلمة المرور غير صحيحة")

# Function to process Excel securely in memory
@st.cache_data
def process_excel(file):
    try:
        xls = pd.ExcelFile(file)
        sheet_names = xls.sheet_names
        
        df1 = pd.read_excel(file, sheet_name=sheet_names[0])
        
        if 'الراتب الاساسي' in df1.columns:
            df1['Base Salary'] = pd.to_numeric(df1['الراتب الاساسي'], errors='coerce').fillna(5000)
        else:
            df1['Base Salary'] = 5000
            
        df1_clean = df1[['الاسم', 'الرقم القومي', 'Base Salary']].copy()
        
        if len(sheet_names) > 1:
            df2 = pd.read_excel(file, sheet_name=sheet_names[1])
            df2_clean = df2[['الاسم', 'الرقم القومي']].copy()
            df2_clean['Base Salary'] = 5000
            combined = pd.concat([df1_clean, df2_clean], ignore_index=True)
        else:
            combined = df1_clean
            
        combined = combined.dropna(subset=['الرقم القومي', 'الاسم'])
        combined['Employee ID'] = combined['الرقم القومي'].astype(str).str.strip()
        combined['Full Name'] = combined['الاسم'].astype(str).str.strip()
        combined['Password'] = combined['Employee ID'].apply(lambda x: x[-4:] if len(x) >= 4 else x)
        
        return combined
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None

# --- SCENARIO A: HR ADMIN VIEW ---
if st.session_state.is_admin:
    st.markdown("---")
    st.subheader("🛠️ لوحة تحكم الموارد البشرية (HR Management Dashboard)")
    st.write("قم برفع ملف الرواتب المحدث أو تعديل البيانات سرا:")
    
    uploaded_file = st.file_uploader("رفع ملف الرواتب الجديد (Upload Excel)", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        st.session_state.df = process_excel(uploaded_file)
        st.success("✅ تم تحديث بيانات الرواتب في النظام بنجاح!")

    if st.session_state.df is not None:
        st.write("### قائمة الموظفين المسجلين الحاليين")
        edited_df = st.data_editor(
            st.session_state.df[['Full Name', 'Employee ID', 'Base Salary']], 
            num_rows="dynamic", 
            use_container_width=True,
            key="admin_editor"
        )
        if st.button("حفظ التعديلات"):
            for idx, row in edited_df.iterrows():
                emp_id = row['Employee ID']
                new_base = row['Base Salary']
                st.session_state.df.loc[st.session_state.df['Employee ID'] == emp_id, 'Base Salary'] = new_base
            st.success("✅ تم الحفظ بنجاح!")
            
    if st.button("تسجيل الخروج من لوحة الإدارة"):
        st.session_state.is_admin = False
        st.rerun()

# --- SCENARIO B: REGULAR EMPLOYEE LOGIN & VIEW ---
else:
    if st.session_state.df is None:
        st.info("👋 مرحباً بك في بوابة موظفي ميراج. النظام قيد التحديث من قبل الإدارة، يرجى العودة لاحقاً أو انتظار رفع ملف الرواتب من المسؤول.")
        st.stop()

    # Employee Login Screen
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
                
                df_system = st.session_state.df
                matching_rows = df_system[df_system['Employee ID'] == clean_id]
                
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

    # Authenticated Employee Payslip View
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

        current_emp_row = st.session_state.df[st.session_state.df['Employee ID'] == emp['Employee ID']]
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
