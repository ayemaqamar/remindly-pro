import streamlit as st
import pandas as pd
import requests
import time
import joblib
from datetime import datetime
from streamlit_lottie import st_lottie

# ========== CONFIG ==========
PUSHBULLET_TOKEN = "o.tRFNrj1kkwYhpNZKuqcf7cPIRk0lfKv9"
LOTTIE_HERO = "https://assets1.lottiefiles.com/packages/lf20_49rdyysj.json"
LOTTIE_BACKGROUND_FLOATS = "https://assets2.lottiefiles.com/packages/lf20_vf1pbr3s.json"
LOTTIE_CHECKLIST = "https://assets2.lottiefiles.com/packages/lf20_touohxv0.json"
LOTTIE_CLOCK = "https://assets10.lottiefiles.com/packages/lf20_qp1q7mct.json"
LOTTIE_TASK_SUCCESS = "https://assets5.lottiefiles.com/private_files/lf30_m6j5igxb.json"

# ========== LOAD LOTTIE ==========
def load_lottie_url(url):
    try:
        res = requests.get(url)
        if res.status_code == 200:
            return res.json()
    except:
        return None

# ========== PUSHBULLET ==========
def send_push_notification(task, deadline, score):
    try:
        headers = {
            "Access-Token": PUSHBULLET_TOKEN,
            "Content-Type": "application/json"
        }
        data = {
            "type": "note",
            "title": "⏰ Task Reminder",
            "body": f"📝 Task: {task}\nDue: {deadline.strftime('%Y-%m-%d %I:%M %p')}\n🔍 Predicted Priority: {score}"
        }
        res = requests.post("https://api.pushbullet.com/v2/pushes", headers=headers, json=data)
        return res.status_code == 200
    except:
        return False

# ========== AI MODEL ==========
@st.cache_resource
def load_model():
    model, label_map = joblib.load("priority_model.pkl")
    inv_label_map = {v: k for k, v in label_map.items()}
    return model, inv_label_map

model, inv_label_map = load_model()

# ========== PAGE CONFIG ==========
st.set_page_config(page_title="Remindly Pro", page_icon="💼", layout="wide")

st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
        background: linear-gradient(to right top, #f5f7fa, #c3cfe2);
        color: #222;
    }
    .title {
        font-size: 64px;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 10px;
    }
    .subtitle {
        text-align: center;
        font-size: 20px;
        color: #444;
        margin-bottom: 30px;
    }
    .card {
        background: rgba(255, 255, 255, 0.8);
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# ========== HOME PAGE ==========
def show_home():
    with st.container():
        cols = st.columns([1, 2, 1])
        with cols[1]:
            hero = load_lottie_url(LOTTIE_HERO)
            if hero:
                st_lottie(hero, height=240)
            st.markdown('<div class="title">Remindly Pro</div>', unsafe_allow_html=True)
            st.markdown('<div class="subtitle">Smarter productivity. AI-powered scheduling and timely reminders.</div>', unsafe_allow_html=True)
    bg = load_lottie_url(LOTTIE_BACKGROUND_FLOATS)
    if bg:
        st_lottie(bg, speed=0.3, height=150, loop=True)
    st.markdown("""
        <div style='text-align:center;'>
            <a href='?page=reminder' style='text-decoration: none;'>
                <button style='margin-top: 30px;'>Launch Reminder Assistant</button>
            </a>
        </div>
    """, unsafe_allow_html=True)

# ========== REMINDER PAGE ==========
def show_reminder():
    st.markdown('<div class="title">Task Reminder Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Organize, prioritize, and never miss what matters.</div>', unsafe_allow_html=True)

    cols = st.columns(2)
    with cols[0]:
        checklist = load_lottie_url(LOTTIE_CHECKLIST)
        if checklist:
            st_lottie(checklist, height=180)
    with cols[1]:
        clock = load_lottie_url(LOTTIE_CLOCK)
        if clock:
            st_lottie(clock, height=180)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📅 Task Scheduler")
    num_tasks = st.slider("Number of tasks", 1, 5, 2)
    tasks = []

    with st.form("task_form"):
        for i in range(num_tasks):
            st.markdown(f"### Task {i+1}")
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Task Title", key=f"name_{i}")
                urgency = st.selectbox("Urgency", ["Low", "Medium", "High"], key=f"urg_{i}")
                urgency_score = {"Low": 1, "Medium": 2, "High": 3}[urgency]
                date = st.date_input("Deadline", key=f"date_{i}")
                task_time = st.time_input("Time", key=f"time_{i}")
            with col2:
                delay = st.radio("Was this delayed before?", ["No", "Yes"], key=f"del_{i}", horizontal=True)
            tasks.append({
                "Task": name,
                "Deadline": datetime.combine(date, task_time),
                "Urgency_Level": urgency_score,
                "User_History_Delay": 1 if delay == "Yes" else 0
            })
        submitted = st.form_submit_button("Prioritize & Notify")
    st.markdown('</div>', unsafe_allow_html=True)

    if submitted:
        with st.spinner("Predicting task priorities..."):
            time.sleep(1)
        df = pd.DataFrame(tasks)
        df["Today"] = datetime.now()
        df["Days_Left"] = (df["Deadline"] - df["Today"]).dt.total_seconds() / 86400
        features = df[["Urgency_Level", "Days_Left", "User_History_Delay"]]
        df["Priority"] = model.predict(features)
        df["Priority"] = df["Priority"].map(inv_label_map)

        st_lottie(load_lottie_url(LOTTIE_TASK_SUCCESS), height=180)

        display_df = df.rename(columns={
            "Urgency_Level": "Urgency",
            "User_History_Delay": "Delay History",
            "Days_Left": "Days Remaining"
        })

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📋 Task Overview")
        st.dataframe(display_df[["Task", "Deadline", "Urgency", "Days Remaining", "Delay History", "Priority"]], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📬 Notifications")
        for _, row in df.iterrows():
            if row["Priority"] == "Urgent":
                if send_push_notification(row["Task"], row["Deadline"], row["Priority"]):
                    st.success(f"🔔 Notification sent: {row['Task']}")
                else:
                    st.error(f"❌ Failed to notify: {row['Task']}")
        st.markdown('</div>', unsafe_allow_html=True)

# ========== ROUTING ==========
if "page" in st.query_params and st.query_params["page"] == "reminder":
    show_reminder()
else:
    show_home()
