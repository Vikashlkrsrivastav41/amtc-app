from datetime import datetime
import os
import cv2
import numpy as np
import pandas as pd
import streamlit as st

FILE_NAME = "Sunday_Test_Records.csv"
TEACHER_QR = "TEACHER-AMTC"

STUDENT_DATABASE = {
    "AMTC-101": "Ayush Kumar",
    "AMTC-102": "Monika Kumari",
    "AMTC-103": "Nishu kumari",
    "AMTC-104": "Rohan kumar",
    "AMTC-105": "Sebi kumari",
    "AMTC-106": "Deepak kumar",
    "AMTC-107": "Anjli kumari",
    "AMTC-108": "Mushkan kumari",
    "AMTC-109": "Shonakshi kumari",
    "AMTC-110": "Ladu kumar",
    "AMTC-111": "shroj kumar",
    "AMTC-112": "Ravi ranjan kumar",
    "AMTC-113": "Aaditya kumar",
    "AMTC-114": "Rishu kumar",
    "AMTC-115": "Monika Kumari",
}

st.set_page_config(
    page_title="AMTC Teaching Center", page_icon="📐", layout="centered"
)
st.title("📐 AMTC Teaching Center System")

menu = [
    "1. अटेंडेंस स्कैन करें (Scan QR)",
    "2. अनुपस्थित लगाएं (Mark Absentees)",
    "3. मार्क्स एवं फीस अपडेट",
    "4. छात्र रिकॉर्ड्स देखें",
]
choice = st.sidebar.selectbox("मेन्यू चुनें:", menu)

# --- 1. SCAN ATTENDANCE ---
if choice == "1. अटेंडेंस स्कैन करें (Scan QR)":
    st.subheader("📸 फोन कैमरे से QR स्कैन करें")
    week_name = st.text_input("टेस्ट का हफ्ता:", value="Week 1")
    fee_default = st.selectbox("डिफ़ॉल्ट फीस स्टेटस:", ["Unpaid", "Paid"])

    img_file = st.camera_input("बच्चे का QR कार्ड कैमरे के सामने लाएं")

    if img_file:
        bytes_data = img_file.getvalue()
        cv2_img = cv2.imdecode(
            np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR
        )

        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(cv2_img)

        if data:
            sid = data.strip().upper()
            if sid in STUDENT_DATABASE:
                today_date = datetime.now().strftime("%d-%m-%Y")

                already_marked = False
                if os.path.exists(FILE_NAME):
                    df_ex = pd.read_csv(FILE_NAME)
                    chk = df_ex[
                        (df_ex["Student_ID"] == sid)
                        & (df_ex["Test_Week"] == week_name)
                        & (df_ex["Attendance"] == "Present")
                    ]
                    if not chk.empty:
                        already_marked = True

                if already_marked:
                    st.warning(
                        f"⚠️ {STUDENT_DATABASE[sid]} की अटेंडेंस आज पहले से दर्ज है!"
                    )
                else:
                    record = {
                        "Date": [today_date],
                        "Student_ID": [sid],
                        "Name": [STUDENT_DATABASE[sid]],
                        "Test_Week": [week_name],
                        "Attendance": ["Present"],
                        "Marks_Obtained": ["Pending"],
                        "Total_Marks": ["--"],
                        "Test_Fee": [fee_default],
                    }
                    df_new = pd.DataFrame(record)
                    if os.path.exists(FILE_NAME):
                        pd.concat(
                            [pd.read_csv(FILE_NAME), df_new], ignore_index=True
                        ).to_csv(FILE_NAME, index=False)
                    else:
                        df_new.to_csv(FILE_NAME, index=False)

                    st.success(
                        f"🎉 ATTENDANCE SUCCESS: {STUDENT_DATABASE[sid]} ({sid})"
                    )
            else:
                st.error("❌ अमान्य QR कोड!")

# --- 2. MARK ABSENTEES ---
elif choice == "2. अनुपस्थित लगाएं (Mark Absentees)":
    st.subheader("🚫 अनुपस्थित बच्चे दर्ज करें")
    week_name = st.text_input("टेस्ट का हफ्ता:", value="Week 1")

    if st.button("ऑटो-मार्क Absent"):
        if os.path.exists(FILE_NAME):
            df = pd.read_csv(FILE_NAME)
            presents = df[df["Test_Week"] == week_name]["Student_ID"].tolist()
            today_date = datetime.now().strftime("%d-%m-%Y")

            absent_records = []
            for sid, name in STUDENT_DATABASE.items():
                if sid not in presents:
                    absent_records.append(
                        {
                            "Date": today_date,
                            "Student_ID": sid,
                            "Name": name,
                            "Test_Week": week_name,
                            "Attendance": "Absent",
                            "Marks_Obtained": "0",
                            "Total_Marks": "--",
                            "Test_Fee": "Unpaid",
                        }
                    )

            if absent_records:
                pd.concat(
                    [df, pd.DataFrame(absent_records)], ignore_index=True
                ).to_csv(FILE_NAME, index=False)
                st.success(
                    f"✅ {len(absent_records)} बच्चों की Absent मार्क हो गई!"
                )
            else:
                st.info("सभी बच्चे उपस्थित हैं!")

# --- 3. MARKS & FEE UPDATE ---
elif choice == "3. मार्क्स एवं फीस अपडेट":
    st.subheader("🔒 मार्क्स और फीस अपडेट")
    sid = st.selectbox(
        "छात्र चुनें:",
        [k for k in STUDENT_DATABASE.keys()],
        format_func=lambda x: f"{STUDENT_DATABASE[x]} ({x})",
    )

    m_obt = st.number_input("प्राप्त अंक (Obtained):", min_value=0, value=0)
    m_tot = st.number_input("कुल अंक (Total):", min_value=1, value=30)
    fee_st = st.selectbox("फीस स्टेटस:", ["Paid", "Unpaid"])

    st.write("---")
    st.info("सुरक्षा: टीचर QR स्कैन करें")
    t_cam = st.camera_input("Teacher QR")

    if t_cam:
        bytes_data = t_cam.getvalue()
        cv2_img = cv2.imdecode(
            np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR
        )
        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(cv2_img)

        if data and data.strip().upper() == TEACHER_QR:
            if st.button("सेव करें"):
                if os.path.exists(FILE_NAME):
                    df = pd.read_csv(FILE_NAME)
                    mask = df["Student_ID"] == sid
                    if mask.any():
                        df.loc[mask, "Marks_Obtained"] = str(m_obt)
                        df.loc[mask, "Total_Marks"] = str(m_tot)
                        df.loc[mask, "Test_Fee"] = fee_st
                        df.to_csv(FILE_NAME, index=False)
                        st.success(f"✅ {STUDENT_DATABASE[sid]} का डेटा सेव हो गया!")
        else:
            st.error("❌ Security Check Failed!")

# --- 4. VIEW DATABASE ---
elif choice == "4. छात्र रिकॉर्ड्स देखें":
    st.subheader("📊 पूरा रिकॉर्ड्स डेटाबेस")
    if os.path.exists(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        st.dataframe(df)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Excel/CSV फ़ाइल डाउनलोड करें",
            data=csv,
            file_name="AMTC_Records.csv",
            mime="text/csv",
        )