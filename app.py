from datetime import datetime
import os
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

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
    page_title="AMTC Attendance", page_icon="📐", layout="centered"
)
st.title("📐 AMTC Attendance System")

menu = [
    "1. अटेंडेंस स्कैन करें (Live Scan)",
    "2. अनुपस्थित लगाएं (Mark Absentees)",
    "3. मार्क्स एवं फीस अपडेट",
    "4. छात्र रिकॉर्ड्स देखें",
]
choice = st.sidebar.selectbox("मेन्यू चुनें:", menu)

# --- 1. LIVE AUTOMATIC SCANNER WITH BEEP SOUND ---
if choice == "1. अटेंडेंस स्कैन करें (Live Scan)":
    st.subheader("📸 ऑटो-स्कैनर (कैमरे के सामने QR लाएं)")
    week_name = st.text_input("टेस्ट का हफ्ता:", value="Week 1")
    fee_default = st.selectbox("डिफ़ॉल्ट फीस स्टेटस:", ["Unpaid", "Paid"])

    # Processing QR scanned from JS
    query_params = st.query_params
    scanned_qr = query_params.get("qr_data", None)

    if scanned_qr:
        sid = scanned_qr.strip().upper()
        if sid in STUDENT_DATABASE:
            today_date = datetime.now().strftime("%d-%m-%Y")
            student_name = STUDENT_DATABASE[sid]

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
                st.warning(f"⚠️ {student_name} ({sid}) की अटेंडेंस आज पहले से दर्ज है!")
            else:
                record = {
                    "Date": [today_date],
                    "Student_ID": [sid],
                    "Name": [student_name],
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
                    f"🎉 ATTENDANCE SUCCESSFUL!\n\n**नाम:** {student_name}\n**ID:** {sid}"
                )
        else:
            st.error(f"❌ अमान्य QR कोड: '{scanned_qr}'")

        # Clear query params after processing
        st.query_params.clear()

    # JS Code for Continuous Auto Camera Scanning and Audio Feedback
    scanner_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js"></script>
        <style>
            #reader { width: 100%; max-width: 450px; margin: 0 auto; border: 2px solid #0D47A1; border-radius: 10px; overflow: hidden; }
            #status-box { text-align: center; font-size: 18px; font-weight: bold; color: green; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div id="reader"></div>
        <div id="status-box">🎥 कैमरा चालू है, QR सामने लाएं...</div>

        <script>
            // Classic Audio Beep Generator using Web Audio API
            function playClassicBeep() {
                try {
                    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                    const osc = audioCtx.createOscillator();
                    const gain = audioCtx.createGain();
                    
                    osc.type = 'sine';
                    osc.frequency.setValueAtTime(880, audioCtx.currentTime); // 880Hz Pitch
                    gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
                    
                    osc.connect(gain);
                    gain.connect(audioCtx.destination);
                    
                    osc.start();
                    osc.stop(audioCtx.currentTime + 0.25); // 0.25 second duration
                } catch(e) {
                    console.log("Audio Error:", e);
                }
            }

            function onScanSuccess(decodedText, decodedResult) {
                // Play audio beep immediately
                playClassicBeep();
                
                document.getElementById('status-box').innerText = "✅ SCANNED: " + decodedText;
                
                // Stop scanner briefly to prevent multiple duplicate hits
                html5QrcodeScanner.clear().then(_ => {
                    // Send scanned value back to Streamlit URL
                    const currentUrl = new URL(window.top.location.href);
                    currentUrl.searchParams.set("qr_data", decodedText);
                    window.top.location.href = currentUrl.toString();
                }).catch(err => {
                    console.error("Failed to clear scanner", err);
                });
            }

            let html5QrcodeScanner = new Html5QrcodeScanner(
                "reader", 
                { 
                    fps: 10, 
                    qrbox: {width: 250, height: 250},
                    rememberLastUsedCamera: true,
                    facingMode: "environment" // Use back camera on phone
                },
                /* verbose= */ false
            );
            html5QrcodeScanner.render(onScanSuccess);
        </script>
    </body>
    </html>
    """
    components.html(scanner_html, height=450)

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
        else:
            st.error("अभी तक कोई रिकॉर्ड नहीं है!")

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
                st.error("छात्र की अटेंडेंस नहीं मिली!")

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
