import pandas as pd
import streamlit as st

# Page configuration
st.set_page_config(page_title="Employee Login Portal", page_icon="🔐")

st.title("🔐 بوابة تسجيل دخول الموظفين")
st.write("الرجاء إدخال الرقم القومي الخاص بك للمتابعة.")


# Automatically load the Excel file from the repository directory
@st.cache_data
def load_data():
  # Make sure your Excel file is uploaded to the root folder and named 'employees.xlsx'
  # (Or change 'employees.xlsx' below to match your actual file name)
  return pd.read_excel("employees.xlsx")


try:
  df = load_data()

  # Clean column names to prevent matching errors caused by hidden spaces
  df.columns = df.columns.str.strip()

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

        # Optional: Display additional employee dashboard details here if needed

      else:
        st.error("الرقم القومي غير صحيح. يرجى التحقق والمحاولة مرة أخرى.")

except Exception as e:
  st.error(
      "تعذر تحميل ملف بيانات الموظفين. تأكد من رفع ملف الـ Excel في نفس مجلد"
      f" المشروع. تفاصيل الخطأ: {e}"
  )
