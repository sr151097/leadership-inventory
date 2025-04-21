import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import matplotlib.pyplot as plt
from fpdf import FPDF
from PyPDF2 import PdfMerger
import os
import unicodedata

pio.kaleido.scope.default_format = "png"

def clean_pdf_text(text):
    replacements = {
        "—": "-",    # em dash
        "–": "-",    # en dash
        "“": "\"",   # left double quote
        "”": "\"",   # right double quote
        "‘": "'",    # left single quote
        "’": "'",    # right single quote
        "\u00A0": " "  # non-breaking space
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return unicodedata.normalize("NFKD", text)

#  Page navigation state 
if 'page' not in st.session_state:
    st.session_state.page = 'welcome'

# --- APP CONFIG ---
st.set_page_config(page_title="Leadership Inventory", layout="centered")

# Apply background image
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("Leadership.jpg");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Load Excel from the same directory
@st.cache_data
def load_questions():
    xls = pd.ExcelFile("Dynamic leadership.xlsm")
    all_parts = []
    for i in range(1, 7):
        part_df = pd.read_excel(xls, sheet_name=f"PART {i}")
        part_df = part_df.dropna(subset=[part_df.columns[0], part_df.columns[1]])
        part_df = part_df[[part_df.columns[0], part_df.columns[1]]]
        part_df.columns = ['Q_No', 'Question']
        part_df['Part'] = f'PART {i}'
        all_parts.append(part_df)
    questions_df = pd.concat(all_parts, ignore_index=True)
    return questions_df

# Leadership styles dictionary
def get_leadership_styles():
    return {
        "Visionary/Authoritative": """Within the 6 leadership styles, you lead with a Visionary style.

You lead by painting a clear and inspiring vision of the future. You naturally say, “Come with me” — inviting others to follow your lead with confidence.
You thrive in situations where a new direction or big-picture clarity is needed. You are high in self-confidence and empathy, helping people feel connected to the bigger purpose.
You act as a change catalyst, bringing energy and inspiration to transformation. You’re skilled at drawing others into your ideas and aligning them with shared goals.
Your presence creates strong positivity and long-term motivation in teams. Great job,— this is one of the most powerful and uplifting leadership styles!

Aspects to reflect upon is do you invest time in coaching/ guiding your team members & building deep connections. Do you listen to all the voices in the room while making decisions.
How much of balance do you have between vision & tasks at hand. And how much of tasks are you able to complete or do you need more support here.

**Ask your team these questions / do a 360 degree report on Workday to understand your blind spots.**""",

        "Coaching": """Within the 6 leadership styles, you lead with a Coaching style.

You focus on developing people and helping them grow over the long term. You encourage others with a mindset of “Try it” — creating a safe space to experiment and learn.
You believe in open exploration when it comes to solving problems and reaching goals. You demonstrate strong empathy, self-awareness, and a genuine interest in others’ growth.
You’re skilled at asking questions, offering guidance, and unlocking potential in your team. You see mistakes as learning opportunities, not failures. Your leadership is especially impactful in environments that value long-term development and individual growth. Well done, Coach — your strength lies in growing future leaders!

Aspects to reflect upon is do you invest time in creating the big picture/ vision for your team. While you focus on developing people, how are you with stakeholder alignment at all levels?
Does collaboration come easily for you. How are you with compliance related matters and those aspects that require multiple tasks and people.

**Ask your team these questions / do a 360 degree report on Workday to understand your blind spots.**""",

        "Affiliative": """Within the 6 leadership styles, you lead with an Affiliative Leadership style.

You prioritize emotional bonds, team harmony, and well-being above all. You lead with the belief that “People come first”, and it shows in your relationships.
You demonstrate strong empathy and communication skills, making people feel seen and heard. You excel at rebuilding trust, especially after conflicts or tough transitions.
You create a safe, supportive environment where individuals feel valued and included. Your leadership is especially powerful when the team needs to heal, reconnect, or reignite motivation.
While not highly goal-focused, you bring people together with emotional intelligence and care. To stay effective long-term, you ensure that team harmony supports progress, not replaces it.
Great work — your warmth and connection-building are at the heart of strong, resilient teams.

Aspects to reflect upon is do you invest time in creating the big picture/ vision for your team. While you bring so much depth in bonds and relationships at work, are you able to look at the tasks at hand and command a performance culture in the team? Are you able to have a difficult conversation with the team or does that drain you. Are you able to recognize the talent within team members easily or do you focus on how they keep the peace of the team culture.

**Ask your team these questions / do a 360 degree report on Workday to understand your blind spots.**""",

        "Democratic": """Within the 6 leadership styles, you lead with a Democratic Leadership style.

You lead by building consensus through participation and collaboration. You often ask “What do you think?”, inviting ideas and encouraging open dialogue.
You demonstrate strong team leadership, communication, and a spirit of inclusion. You create a culture where people feel heard, valued, and involved in decision-making.
Your approach helps build deep ownership and commitment to shared goals. You’re especially effective in environments where trust, transparency, and team input are valued.
While your style may slow things down early on, it pays off once team momentum builds. You ensure that key stakeholders — especially senior leaders — are aligned and supportive of the process.
Keep going , a collaborative leader like you creates empowered, engaged teams over time!

Aspects to reflect upon is whether consensus is always needed or do you want to bring your judgement when matters are high urgency/ criticality. Does big decisions which are dependent on multiple stakeholders set you off guard. What is the team vision while we arrive at consensus? In the attempt to build a democratic environment, are you losing out on any creativity within team.

**Ask your team these questions / do a 360 degree report on Workday to understand your blind spots.**""",

        "Pace-setting": """Within the 6 leadership styles, you lead with a Pace-Setting Leadership style.

You lead by setting high standards and expecting excellence in performance. Your message is clear: “Do as I do, now” — and you lead by example every step of the way.
You demonstrate strong self-direction, initiative, and a deep drive to succeed. You perform at a high level and expect others to match your energy and standards.
Your style works best with highly skilled and self-motivated team members who thrive under pressure. You bring conscientiousness and a laser focus to the task at hand.
Like the Coercive leader, you’re highly results-driven — but your strength lies in modeling excellence, not control. While effective in fast-paced environments, this style can lead to burnout if overused.
Keep it balanced — your power comes from your ability to inspire through your own performance.

Aspects to reflect upon is do you invest time in creating the big picture/ vision for your team. While you are results focused, how much do you invest time in understanding various skill levels of the team and how you can support each of them. While you want to model excellence, how empathetic are you with your team or even yourself about expectations.
Does having to collaborate with multiple stakeholders stress you. Are your relationships with the team – surface level and not deep enough to engage and inspire them.

**Ask your team these questions / do a 360 degree report on Workday to understand your blind spots.**""",

        "Commanding/Coercive": """Within the 6 leadership styles, you lead with a Commanding Leadership style.

You lead with clear authority and expect immediate action and compliance. Your leadership voice says: “Do what I tell you” — direct, decisive, and firm.
You demonstrate strong initiative, self-control, and an intense drive to succeed. You thrive in crisis situations where quick, commanding leadership is essential.
You bring clarity and structure in moments of uncertainty, helping others feel grounded. Your style works best when time is limited, risks are high, or direction is urgently needed.
While powerful in high-stakes moments, it can limit team creativity and ownership if used too often. You're aware that balance is key — and you aim to combine authority with empathy when possible. Well done — your ability to step up and lead under pressure is a real strength.

Aspects to reflect upon is how do you engage with a team and inspire them to perform in your absence. How do you delegate work in your team. Do you allow team members to lead aspects in areas of work and therefore take ownership of their own tasks. Do you tend to micro manage or give very quick feedback. How much do you focus on inspiring the team to perform beyond their capabilities.

**Ask your team these questions / do a 360 degree report on Workday to understand your blind spots.**"""
    }

# --- TOP LEFT LOGO ---
st.markdown("""
<div style='position: absolute; top: 10px; left: 10px;'>
    <img src='https://raw.githubusercontent.com/your-repo-path/download.png' width='60'>
</div>
""", unsafe_allow_html=True)

# --- WELCOME MESSAGE ---
st.image("download.png", width=150)
st.markdown("<h1 style='text-align: center;'>🧭 Dynamic Leadership Inventory</h1>", unsafe_allow_html=True)
st.markdown("""
    Welcome! This tool helps you discover your dominant leadership style.  
    Please answer the following questions honestly. Once submitted, you'll receive a personalized leadership profile and a downloadable report with insights.
""")
st.markdown("<br><br>", unsafe_allow_html=True)

# --- USER DETAILS ---
st.markdown("### 👤 Participant Information")
name = st.text_input("Your Name")
email = st.text_input("Your Email")
password = st.text_input("Enter Access Password", type="password")

if password != "leader2024":
    st.warning("Please enter a valid password to begin.")
    st.stop()

st.markdown("---")

questions_df = load_questions()
styles = get_leadership_styles()

st.header("📋 Rate the Following Statements (1 = Strongly Disagree, 5 = Strongly Agree)")
responses = []
for index, row in questions_df.iterrows():
    score = st.slider(f"{int(row['Q_No'])}. {row['Question']}", 1, 5, 3)
    responses.append((row['Part'], score))

# --- ON SUBMIT ---
if st.button("✅ Submit Exam"):
    part_scores = {}
    for part, score in responses:
        part_scores[part] = part_scores.get(part, 0) + score

    style_map = {
        "PART 1": "Visionary/Authoritative",
        "PART 2": "Coaching",
        "PART 3": "Affiliative",
        "PART 4": "Democratic",
        "PART 5": "Pace-setting",
        "PART 6": "Commanding/Coercive"
    }

    style_totals = {style_map[k]: v for k, v in part_scores.items()}
    top_styles = sorted(style_totals.items(), key=lambda x: x[1], reverse=True)[:1]
    final_style = top_styles[0][0]

    st.markdown("---")
    st.subheader("🎯 Your Leadership Style")
    for style, _ in top_styles:
        st.markdown(f"<h4 style='color:#2e7d32;'>{style}</h4>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='background-color:#e6ffe6; padding:15px; border-left: 6px solid green;'>
            {styles[style]}
        </div>
        """, unsafe_allow_html=True)

    radar_df = pd.DataFrame(list(style_totals.items()), columns=["Leadership Style", "Total Score"])
    radar_df["Style"] = radar_df["Leadership Style"]
    fig = px.line_polar(radar_df, r="Total Score", theta="Style", line_close=True,
                        title="Your Leadership Profile", markers=True)
    fig.update_traces(fill='toself', line_color='green')
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 60])),
        showlegend=False,
        paper_bgcolor="#fff0f0"
    )
    st.plotly_chart(fig)
    fig.write_image("radar_chart.png")

    # --- PDF Generation ---
    pdf = FPDF()
    pdf.add_page()
    pdf.image("download.png", x=10, y=8, w=40)
    pdf.ln(25)
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(135, 206, 235)
    pdf.cell(0, 10, "Leadership Inventory Report", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"Name: {name}", ln=True)
    pdf.cell(0, 10, f"Email: {email}", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Top Leadership Style:", ln=True)
    pdf.ln(6)

    for style, _ in top_styles:
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(0, 51, 102)
        pdf.multi_cell(0, 8, clean_pdf_text(f"{style}"))
        pdf.ln(2)
        pdf.set_font("Arial", size=12)
        pdf.set_text_color(0, 0, 0)
        clean_desc = clean_pdf_text(styles[style])
        pdf.multi_cell(0, 8, clean_desc)
        pdf.ln(4)

    if os.path.exists("radar_chart.png"):
        pdf.image("radar_chart.png", w=150)

    pdf.output("appendix.pdf")

    def merge_pdfs(main_path, extra_path, output_path):
        merger = PdfMerger()
        merger.append(extra_path)
        merger.append(main_path)
        merger.write(output_path)
        merger.close()

    merge_pdfs("Leadership Style.pdf", "appendix.pdf", "Leadership Report.pdf")

    with open("Leadership Report.pdf", "rb") as f:
        st.download_button(
            label="📥 Download Full Report (with Appendix)",
            data=f,
            file_name="Leadership Report.pdf",
            mime="application/pdf"
        )

    st.success("🎉 Your leadership style report is ready for download!")
    st.markdown("<p style='font-size: 6px; color: #999999; text-align: right;'> ©http://www.skillsyouneed.com/lead/leadership-styles.html .</p>", unsafe_allow_html=True)
