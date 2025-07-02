import streamlit as st
import pandas as pd
import requests
import time
import joblib
from datetime import datetime
from streamlit_lottie import st_lottie

# ========== CONFIG ==========
PUSHBULLET_TOKEN = "o.tRFNrj1kkwYhpNZKuqcf7cPIRk0lfKv9"

# ========== LOTTIE ==========
LOTTIE_ROBOT = "https://lottie.host/f69965f3-e0b0-4bec-9440-10fafec47996/iexeV7I1I6.json"
LOTTIE_BACKGROUND_FLOATS = "https://assets2.lottiefiles.com/packages/lf20_vf1pbr3s.json"
LOTTIE_TASK_SUCCESS = "https://assets5.lottiefiles.com/private_files/lf30_m6j5igxb.json"
LOTTIE_CUSTOM_1 = "https://lottie.host/a96ffd1a-aef3-4063-abc2-15323eb1481a/RfAp91ZpIv.json"
LOTTIE_CUSTOM_2 = "https://lottie.host/b723aeed-6918-4133-940e-6b6fd9eeeec3/8TltsefBYg.json"

# ========== INITIALIZE ==========
task_history = []

@st.cache_resource
def load_model():
    model, label_map = joblib.load("priority_model.pkl")
    inv_label_map = {v: k for k, v in label_map.items()}
    return model, inv_label_map

model, inv_label_map = load_model()

# ========== HELPERS ==========
def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except:
        return None

def send_push_notification(task, deadline, score):
    try:
        headers = {
            "Access-Token": PUSHBULLET_TOKEN,
            "Content-Type": "application/json"
        }
        data = {
            "type": "note",
            "title": "⏰ Task Reminder",
            "body": f"Task: {task}\nDue: {deadline.strftime('%Y-%m-%d %I:%M %p')}\nPredicted Priority: {score}"
        }
        res = requests.post("https://api.pushbullet.com/v2/pushes", headers=headers, json=data)
        return res.status_code == 200
    except:
        return False

def should_notify(row):
    priority = row["Priority"]
    deadline = row["Deadline"]
    now = datetime.now()
    hours_left = (deadline - now).total_seconds() / 3600
    return (priority == "Urgent") or \
           (priority == "Medium" and hours_left <= 24) or \
           (priority == "Low" and hours_left <= 6)

def suggest_task():
    return task_history[-1] if task_history else ""

# ========== PAGE CONFIG ==========
st.set_page_config(page_title="Remindly Pro", page_icon="💼", layout="wide")

# ========== STYLING ==========
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(145deg, #0f0f1a, #1a1a2e);
    color: #f0f0f0;
}
.title, .title.neon {
    font-family: 'Orbitron', sans-serif;
    font-size: 64px;
    font-weight: 700;
    background: linear-gradient(90deg, #00ffe0, #9d00ff, #00ffe0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 10px;
}
.subtitle, .subtitle.neon {
    font-size: 20px;
    text-align: center;
    color: #a0a0ff;
    font-weight: 600;
    letter-spacing: 1px;
    margin-bottom: 30px;
}
.neo-card {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 20px;
    padding: 20px;
    border: 1px solid rgba(0, 255, 255, 0.1);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    box-shadow: 0 8px 24px rgba(0, 255, 255, 0.08);
    margin-bottom: 30px;
}
.neon-launch {
    background: linear-gradient(90deg, #00ffe0, #9d00ff);
    color: white;
    font-weight: 600;
    border: none;
    border-radius: 30px;
    padding: 0.7rem 1.8rem;
    font-size: 16px;
    box-shadow: 0 4px 20px rgba(0,255,255,0.3);
    transition: all 0.3s ease-in-out;
    cursor: pointer;
}
.neon-launch:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 24px rgba(157, 0, 255, 0.4);
}
</style>
""", unsafe_allow_html=True)

# ========== PAGES ==========
def show_home():
    st.markdown("<div style='padding-top: 80px'></div>", unsafe_allow_html=True)
    with st.container():
        cols = st.columns([1, 2, 1])
        with cols[1]:
            robot = load_lottie_url(LOTTIE_ROBOT)
            if robot:
                st_lottie(robot, height=280)
            st.markdown('<div class="title neon">Remindly Pro</div>', unsafe_allow_html=True)
            st.markdown('<div class="subtitle neon">Plan. Prioritize. Perform.</div>', unsafe_allow_html=True)

    bg = load_lottie_url(LOTTIE_BACKGROUND_FLOATS)
    if bg:
        st_lottie(bg, speed=0.3, height=150, loop=True)

    st.markdown("""
        <div style='text-align:center; margin-top: 30px;'>
            <a href='?page=reminder'>
                <button class='neon-launch'>Launch Reminder Assistant</button>
            </a>
        </div>
    """, unsafe_allow_html=True)

def show_reminder():
    st.markdown('<div class="title neon">🧠 Task Reminder Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle neon">Organize with precision. Prioritize with power.</div>', unsafe_allow_html=True)

    st.markdown('<div class="neo-card">', unsafe_allow_html=True)
    st.subheader("🗓 Task Scheduler")

    num_tasks = st.slider("Number of tasks", 1, 5, 2)
    tasks = []

    with st.form("task_form"):
        for i in range(num_tasks):
            st.markdown(f"<div class='neo-card'>", unsafe_allow_html=True)
            st.markdown(f"### Task {i+1}")
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Task Title", key=f"name_{i}")
                date = st.date_input("Deadline", key=f"date_{i}")
                task_time = st.time_input("Time", key=f"time_{i}")
            with col2:
                delay = st.radio("Was this delayed before?", ["No", "Yes"], key=f"delay_{i}", horizontal=True)
            st.markdown("</div>", unsafe_allow_html=True)

            task_history.append(name)
            tasks.append({
                "Task": name,
                "Deadline": datetime.combine(date, task_time),
                "Urgency_Level": 0,
                "User_History_Delay": 1 if delay == "Yes" else 0
            })

        submitted = st.form_submit_button("Prioritize & Notify")
    st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        with st.spinner("Running the AI hamster wheel..."):
            time.sleep(1)
        df = pd.DataFrame(tasks)
        df["Today"] = datetime.now()
        df["Days_Left"] = (df["Deadline"] - df["Today"]).apply(lambda delta: max(delta.total_seconds() / 86400, 0))
        features = df[["Urgency_Level", "Days_Left", "User_History_Delay"]]
        df["Priority"] = model.predict(features)
        df["Priority"] = df["Priority"].map(inv_label_map)

        st_lottie(load_lottie_url(LOTTIE_TASK_SUCCESS), height=180)

        st.subheader("📋 Task Overview")
        df.rename(columns={"Days_Left": "Days remaining", "User_History_Delay": "Delay History"}, inplace=True)
        st.dataframe(df[["Task", "Deadline", "Days remaining", "Delay History", "Priority"]], use_container_width=True)

        st.subheader("📬 Notifications")
        for _, row in df.iterrows():
            if should_notify(row):
                if send_push_notification(row["Task"], row["Deadline"], row["Priority"]):
                    st.success(f"🔔 Notification sent: {row['Task']}")
                else:
                    st.error(f"❌ Failed to notify: {row['Task']}")
            else:
                st.info(f"⏳ Snoozed: {row['Task']} ({row['Priority']})")

        st.markdown('<div class="title neon" style="font-size: 28px;">📆 Days Left Before Deadline</div>', unsafe_allow_html=True)
        if not df.empty:
            avg_days = df["Days remaining"].mean()
            display_days = 0 if abs(avg_days) < 0.05 else round(avg_days, 1)
            st.metric("", f"{display_days} days")

            st.subheader("💜 Upcoming Tasks")
            st.table(df[["Task", "Deadline", "Priority"]].sort_values("Deadline").head(5))
        else:
            st.info("No task data yet. Go schedule something 😎")

# ========== ROUTING ==========
query_params = st.query_params if hasattr(st, "query_params") else {}

page_param = query_params.get("page", "")
if isinstance(page_param, list):
    page_param = page_param[0]

if page_param == "reminder":
    show_reminder()
else:
    show_home()
