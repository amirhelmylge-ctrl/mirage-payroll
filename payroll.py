import pandas as pd
import streamlit as st

# Page configuration
st.set_page_config(page_title="Employee Login Portal", page_icon="🔐")

# --- Language Translations Dictionary ---
translations = {
    "English": {
        "title": "🔐 Employee Login Portal",
        "subtitle": "Please enter your National ID to proceed.",
        "admin_header": "Admin Control Panel",
        "upload_label": "Upload Employees Excel File",
        "upload_success": "Employee data successfully loaded and saved!",
        "upload_warning": (
            "⚠️ Employee database not uploaded yet. Please ask the admin to"
            " upload the Excel file from the sidebar."
        ),
        "input_label": "National ID (الرقم القومي):",
        "login_btn": "Login",
        "logout_btn": "Logout",
        "empty_input": "Please enter your National ID.",
        "error_id": "Incorrect National ID. Please check and try again.",
        "error_read": "Error reading file: {error}",
        "dashboard_title": "Payroll Breakdown & Salary Details",
        "welcome_banner": "Welcome, {name}!",
        "id_display": "National ID:",
        "details_header": "Detailed Salary Breakdown (Bonuses, Deductions, etc.)",
    },
    "العربية": {
        "title": "🔐 بوابة تسجيل دخول الموظفين",
        "subtitle": "الرجاء إدخال الرقم القومي الخاص بك للمتابعة.",
        "admin_header": "لوحة تحكم المسؤول (Admin)",
        "upload_label": "رفع ملف الـ Excel للموظفين",
        "upload_success": "تم تحديث وحفظ بيانات الموظفين بنجاح!",
        "upload_warning": (
            "⚠️ لم يتم رفع قاعدة بيانات الموظفين بعد. يرجى من المسؤول رفع ملف الـ"
            " Excel من القائمة الجانبية."
        ),
        "input_label": "الرقم القومي (National ID):",
        "login_btn": "تسجيل الدخول",
        "logout_btn": "تسجيل الخروج",
        "empty_input": "الرجاء إدخال الرقم القومي.",
        "error_id": "الرقم القومي غير صحيح. يرجى التحقق والمحاولة مرة أخرى.",
        "error_read": "خطأ في قراءة الملف: {error}",
        "dashboard_title": "تفاصيل الراتب والخصومات والمكافآت",
        "welcome_banner": "أهلاً بك يا {name}!",
        "id_display": "الرقم القومي:",
        "details_header": "تفاصيل مفردات الراتب (المكافآت، الخصومات، وغيرها)",
    },
}

# --- Language Switcher in Sidebar ---
st.sidebar.title("🌐 Language / اللغة")
selected_lang = st.sidebar.selectbox("Choose Language", ["العربية", "English"])
t = translations[selected_lang]

# Initialize session state variables
if "employee_df" not in st.session_state:
  st.session_state.employee_df = None
if "logged_in_user" not in st.session_state:
  st.session_state.logged_in_user = None
if "logged_in_id" not in st.session_state:
  st.session_state.logged_in_id = None
if "employee_row_data" not in st.session_state:
  st.session_state.employee_row_data = None

# --- Admin Section (Sidebar) ---
st.sidebar.markdown("---")
st.sidebar.header(t["admin_header"])
uploaded_file = st.sidebar.file_uploader(t["upload_label"], type=["xlsx", "xls"])

if uploaded_file is not None:
  try:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    st.session_state.employee_df = df
    st.sidebar.success(t["upload_success"])
  except Exception as e:
    st.sidebar.error(t["error_read"].format(error=e))

# --- Main Page Layout ---
st.title(t["title"])

# Check if an employee is currently logged in -> Show Employee Dashboard
if st.session_state.logged_in_user:
  st.success(t["welcome_banner"].format(name=st.session_state.logged_in_user))

  st.markdown(f"### 📋 {t['dashboard_title']}")
  st.info(
      f"**{t['id_display']}**"
      f" `{str(st.session_state.logged_in_id).strip()}`"
  )

  st.markdown(f"#### {t['details_header']}")

  if st.session_state.employee_row_data is not None:
    row_data = st.session_state.employee_row_data

    # Display columns in clean organized columns layout (e.g., 2 columns side-by-side)
    cols = st.columns(2)
    idx = 0
    for col_name, val in row_data.items():
      # Skip showing name and national ID inside the metrics since they are already at the top banner
      if col_name in ["الاسم", "الرقم القومي", "Name", "National ID"]:
        continue

      with cols[idx % 2]:
        st.metric(label=str(col_name), value=str(val))
      idx += 1

  st.markdown("---")
  if st.button(t["logout_btn"]):
    st.session_state.logged_in_user = None
    st.session_state.logged_in_id = None
    st.session_state.employee_row_data = None
    st.rerun()

else:
  st.write(t["subtitle"])

  if st.session_state.employee_df is None:
    st.warning(t["upload_warning"])
  else:
    df = st.session_state.employee_df

    # Input field for National ID
    national_id_input = st.text_input(t["input_label"], type="password")

    if st.button(t["login_btn"]):
      if not national_id_input:
        st.warning(t["empty_input"])
      else:
        matched = df[
            df["الرقم القومي"].astype(str).str.strip()
            == national_id_input.strip()
        ]

        if not matched.empty:
          employee_name = matched.iloc[0]["الاسم"]
          st.session_state.logged_in_user = employee_name
          st.session_state.logged_in_id = national_id_input.strip()
          st.session_state.employee_row_data = matched.iloc[0].to_dict()
          st.rerun()
        else:
          st.error(t["error_id"])
