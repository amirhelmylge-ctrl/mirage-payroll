import pandas as pd
import streamlit as st

# Page configuration
st.set_page_config(page_title="Employee Login Portal", page_icon="🔐")

st.title("🔐 بوابة تسجيل دخول الموظفين")

# Initialize session state for uploaded data if it doesn't exist
if "employee_df" not in st.session_state:
  st.session_state.employee_df = None

# --- Admin Section (Sidebar) ---
st.sidebar.header("لوحة تحكم المسؤول (Admin)")
uploaded_file = st.sidebar.file_uploader(
    "رفع ملف الـ Excel للموظفين", type=["xlsx", "xls"]
)

if uploaded_file is not None:
  try:
    # Read the uploaded Excel file
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    # Save into session state so it stays active
    st.session_state.employee_df = df
    st.sidebar.success("تم تحديث وحفظ بيانات الموظفين بنجاح!")
  except Exception as e:
    st.sidebar.error(f"خطأ في قراءة الملف: {e}")

# --- Employee Login Section ---
st.write("الرجاء إدخال الرقم القومي الخاص بك للمتابعة.")

if st.session_state.employee_df is None:
  st.warning(
      "⚠️ لم يتم رفع قاعدة بيانات الموظفين بعد. يرجى من المسؤول رفع ملف الـ Excel"
      " من القائمة الجانبية."
  )
else:
  df = st.session_state.employee_df

  # Input field for National ID
  national_id_input = st.text_input(
      "الرقم القومي (National ID):", type="password"
  )

  if st.button("تسجيل الدخول"):
    if not national_id_input:
      st.warning("الرجاء إدخال الرقم القومي.")
    else:
      # Match input against the 'الرقم القومي' column
      matched = df[
          df["الرقم القومي"].astype(str).str.strip()
          == national_id_input.strip()
      ]

      if not matched.empty:
        employee_name = matched.iloc[0]["الاسم"]
        st.success(f"مرحباً، {employee_name}! تم تسجيل الدخول بنجاح.")
      else:
        st.error("الرقم القومي غير صحيح. يرجى التحقق والمحاولة مرة أخرى.")
