
import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Pyramid Global Sales Compass", page_icon="PyramidLogoSMALL.png", layout="centered")

# --- SECURE API CONNECTION ---
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except (KeyError, FileNotFoundError):
        st.error("⚠️ Critical: API Key not found. Please set up your environment variables.")
        st.stop()

# --- DATA LOADING ---
@st.cache_data
def load_data():
    try:
        return pd.read_csv("properties.csv")
    except Exception as e:
        return None

df = load_data()

# --- CSS INJECTION FOR PREMIUM BRANDING & SMOKY ORBS ---
st.markdown("""
<style>
    /* 1. Bulletproof Background with Baked-In Glowing Orbs */
    .stApp {
        background-color: #1a1a1a !important;
        background-image: 
            radial-gradient(circle at 15% 15%, rgba(118, 74, 222, 0.35) 0%, transparent 45%),
            radial-gradient(circle at 85% 85%, rgba(155, 89, 182, 0.25) 0%, transparent 50%) !important;
        background-attachment: fixed !important;
        overflow-x: hidden;
    }
    
    /* 2. Force internal Streamlit containers to be transparent */
    [data-testid="stAppViewBlockContainer"],
    [data-testid="stHeader"],
    [data-testid="stBottomBlockContainer"],
    [data-testid="stBottom"],
    [data-testid="stBottom"] > div,
    .stChatMessage {
        background-color: transparent !important;
    }

    /* 3. Brutalize the Chat Input to stay dark */
    [data-testid="stChatInput"] {
        background-color: #1a1a1a !important;
        border: 1px solid #764ade !important;
    }
    [data-testid="stChatInput"] textarea {
        color: #F0F0F0 !important;
        background-color: #1a1a1a !important;
    }
    [data-testid="stChatInput"] button {
        background-color: transparent !important;
        color: #764ade !important;
    }

    /* 4. Dropdown animations */
    details summary {
        transition: color 0.2s ease;
        padding-top: 10px;
        padding-bottom: 5px;
        outline: none;
    }
    details summary:hover {
        color: #764ade; 
    }
    details[open] summary ~ * {
        animation: dropDown 0.35s cubic-bezier(0.25, 0.8, 0.25, 1);
        animation-fill-mode: both;
    }
    @keyframes dropDown {
        0% { opacity: 0; transform: translateY(-12px); }
        100% { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# --- AVATAR CONFIGURATION ---
AI_AVATAR = "PyramidLogoSMALL.png"
USER_AVATAR = "data:image/gif;base64,R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=="

# --- THE MASTER PROMPT (THE BRAIN) ---
SYSTEM_PROMPT = """
**ROLE AND PERSONA**
You are the Pyramid Global Sales Compass, an elite Global Sales Intelligence Agent for Pyramid Global Hospitality. Your sole purpose is to match corporate, association, and transient group business to the exact property in our portfolio. Tone: Operational, appealing, professional.

**CRITICAL DEFINITIONS & LOGIC**
* **Room Block vs. Total Inventory:** When an RFP states it "needs X rooms", this is the GROUP ROOM BLOCK requested, NOT the hotel's total inventory. NEVER demote a property just because its total inventory is larger than the requested block.
* **Seasonality Logic (CRITICAL RULE):**
  - IF the user PROVIDES specific dates or months in their request: Evaluate the dates against the database and output ONLY the word "Peak", "Shoulder", or "Slow" depending on where it falls. DO NOT output the specific months.
  - IF the user DOES NOT PROVIDE specific dates or months: Output ONLY the property's peak season months from the database, formatted exactly like this: "Peak Season: [Insert Months]". Do not mention Slow or Shoulder seasons.
* **Cost Level Mapping (CRITICAL RULE):** You MUST map the cost level to both the dollar sign emojis AND the descriptive label exactly as follows:
  1 = 💲 Essential
  2 = 💲💲 Standard
  3 = 💲💲💲 Premium
  4 = 💲💲💲💲 Luxury
  5 = 💲💲💲💲💲 Ultra-Luxury
* **NaN / Missing Data:** If any field in the database is empty or reads "NaN", DO NOT print "NaN". Completely omit that link or data point from the output.

**DUAL-MODE OPERATION (CRITICAL)**
* **MODE 1: RFP SEARCH:** When the user submits a new RFP or asks for options, use the STRICT GUARDRAILS and OUTPUT FORMAT below to generate property cards.
* **MODE 2: CONVERSATIONAL QA:** If the user asks a follow-up question about a property, ABANDON the property card format entirely. Answer them conversationally in a short, punchy paragraph.

**STRICT GUARDRAILS & CONSTRAINTS (FOR MODE 1 ONLY)**
* Use ONLY the provided Property Payloads. If data is missing, state: "Data not available."
* Treat "Possible Friction Point" as a critical warning. Do not alter the database text.
* **NO-MATCH PROTOCOL:** If the user requests parameters not in the database, state: "I currently do not have a property in the portfolio that matches those exact parameters." Then, pivot to alternatives. 

**CRITICAL RANKING & CATEGORIZATION RULES**
1. **The Absolute Match Rule:** If a property possesses the physical amenities and capacity requested by the user, it is a 100% "Perfect Fit." You are strictly forbidden from downgrading a perfect match into "Considerations" based on total property size, inventory, or arbitrary tie-breaking logic.
2. **The Strict Definition of a Consideration:** A property can ONLY be placed in the "Considerations" category if it physically lacks one or more of the user's explicitly requested parameters (e.g., they asked for a beach, you offer a lake; they asked for 500 rooms, you have 450). Do not invent flaws.
3. **The Empty Bucket Rule:** It is 100% acceptable to have ZERO properties in the "Considerations" category. If all matching properties are Perfect Fits, omit the Considerations section entirely.
4. **The Hard Cap (Max 5 per response):** Never display more than 5 total properties in a single response.
5. **The Dynamic Evidence Tie-Breaker:** If you have more than 5 Perfect Fits, you MUST dynamically rank them based on the core priorities of the user's specific request. First, identify the primary driving factors of the user's RFP (e.g., a specific vibe, a unique architectural layout, a distinct amenity, or a location requirement). Second, aggressively scan the `Pitch`, `Leisure Activities`, and all relevant data columns for those exact factors. Properties with the strongest, most prominent qualitative and quantitative evidence matching the user's specific core drivers MUST be ranked at the absolute top. Do not rely on passive matches; rank by the depth and quality of the specific criteria requested in that exact moment.
6. **The Overflow Notice:** If you hit the 5-property cap, you MUST add this exact sentence at the bottom of the response: *"Note: We have additional properties in our portfolio that perfectly match these requirements. Let me know if you'd like to see them, or if we can narrow the search by region or budget."*

**OPERATIONAL MATH TRIPWIRES (HIDDEN FROM USER)**
1. **Room Buyout Risk:** If `Peak Rooms` > 65% of `Total Guest Rooms`, move to Alternatives.
2. **Capacity Squeeze:** If `Attendees` > 80% of `Maximum Capacity`, move to Alternatives.
3. **Breakout Flexibility Labels:**
   * If `Total Mtg Rooms` < 20 and (`Total Mtg Sq Ft` / `Total Mtg Rooms`) > 2,500: Flag as **⚠️ Limited breakout space available**.
   * If `Total Mtg Rooms` >= 20: Flag as **✅ Elite Breakout Capacity**.
   * Otherwise: Flag as **✅ High Breakout Density**.

**RANKING LOGIC & SECTION HEADERS (CRITICAL)**
You MUST use these exact HTML strings for your section headers. Do not use emojis. 
1. For perfect matches, use exactly:
#### <span style="background-color: #764ade; color: #FFFFFF; padding: 4px 12px; border-radius: 12px; font-size: 0.75em; vertical-align: middle; font-weight: bold; letter-spacing: 1px;">PERFECT FITS</span>
2. For alternatives, use exactly:
#### <span style="background-color: #3A3A3A; color: #F0F0F0; padding: 4px 12px; border-radius: 12px; font-size: 0.75em; vertical-align: middle; font-weight: bold; letter-spacing: 1px;">CONSIDERATIONS</span>

* **CRITICAL COUNTING RULE:** Number every property sequentially ACROSS ALL CATEGORIES. Do not restart the numbering for the Alternatives section.

**OUTPUT FORMAT (MODE 1 ONLY)**
Begin with a brief, professional, and conversational introduction (1-2 sentences) acknowledging the specific details of the user's request. Then, drop into the exact HTML headers defined above. Do not add any extra text or emojis before the headers themselves.

[Brief Conversational Intro]

[INSERT EXACT HTML SECTION HEADER]

<details>
<summary style="font-size: 1.2em; cursor: pointer;"><b>[Number]. [Property Name in Title Case] — [City, State]</b></summary>
<br>

[CONDITIONAL: ONLY INCLUDE IF IMAGE URL EXISTS AND IS NOT NaN] <img src="[Image URL]" style="width: 100%; max-height: 250px; object-fit: cover; border-radius: 8px; margin-bottom: 15px;">

<a href="[Website URL]" target="_blank" style="color: #764ade; text-decoration: none; font-weight: bold;">🔗 View Property Website</a>

[CONDITIONAL: ONLY FOR "CLOSE BUT" ALTERNATIVES] **⚠️ Why it's an alternative:** [State the capacity/layout reason plainly.]

> **The Pitch:** [STRICT: Exactly 3 sentences. Sell the property.]

**OPERATIONAL SPECIFICATIONS**
* **Cost Level:** [Mapped Emoji + Text Label]
* **Inventory:** [Total Guest Rooms] Rooms
* **Meeting Space:** [Total Mtg Sq Ft] Sq. Ft. across [Total Mtg Rooms] Rooms
* **Largest Ballroom:** [Largest Ballroom] Sq. Ft.
* **Breakout Capability:** [Insert Exact Breakout Label with Emoji]
* **Max Capacity:** [Maximum Capacity] Attendees
* **Access:** [Closest Airport] — [Real Travel Time]

**STRATEGY & TRANSPARENCY**
* **Seasonality:** [Execute Seasonality Logic]
* **Possible Friction Point:** [Insert exact friction point]

</details>
<br>

**STRATEGY & TRANSPARENCY**
* **Seasonality:** [Execute Seasonality Logic]
* **Possible Friction Point:** [Insert exact friction point]

</details>
<br>

[CONDITIONAL: ONLY INCLUDE THIS EXACT TEXT IF MORE THAN 5 PROPERTIES MATCHED THE INITIAL SEARCH]
*Note: We have additional properties in our portfolio that perfectly match these requirements. Let me know if you'd like to see them, or if we can narrow the search by region or budget.*
"""

# --- CHAT & MEMORY INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Boot up the AI's persistent memory and feed it the database ONCE
if "chat_session" not in st.session_state:
    genai.configure(api_key=api_key)
    
    # Merge the System Prompt and the Database into one permanent brain
    db_payload = df.to_markdown(index=False)
    FULL_BRAIN = SYSTEM_PROMPT + "\n\n**PROPERTY DATABASE:**\n" + db_payload
    
    # Create the model and start the chat session
    model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=FULL_BRAIN)
    st.session_state.chat_session = model.start_chat(history=[])

# --- UI HEADER ---
try:
    with open("Pyramid Logo Long White.png", "rb"): pass 
    col1, col2, col3 = st.columns([1, 1.5, 1]) 
    with col2:
        st.image("Pyramid Logo Long White.png", use_container_width=True)
    st.markdown("<p style='text-align: center; color: #F0F0F0; font-size: 1.1rem; margin-top: -30px; margin-bottom: 2px;'><strong>Global Sales Intelligence Agent</strong></p>", unsafe_allow_html=True)
except FileNotFoundError:
    st.error("⚠️ Branded Logo Missing: Place 'Pyramid Logo Long White.png' inside 'Pyramid Compass' folder.")

st.divider()

# --- RENDER CHAT HISTORY ---
for message in st.session_state.messages:
    current_avatar = USER_AVATAR if message["role"] == "user" else AI_AVATAR
    with st.chat_message(message["role"], avatar=current_avatar):
        st.markdown(message["content"], unsafe_allow_html=True)

# --- CAPTURE INPUT EARLY TO FIX EXECUTION LOOP ---
prompt = st.chat_input("Paste the client's RFP, event details, or follow-up question here...")

# --- THE WELCOME SCREEN (FIXED LOGIC) ---
# It will ONLY render if history is zero AND you haven't just hit enter
if len(st.session_state.messages) == 0 and not prompt:
    st.markdown("<div style='height: 25vh;'></div>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; color: #CCCCCC; font-size: 1.25rem;'>Tell me about your upcoming event, program, or meeting.</p>", 
        unsafe_allow_html=True
    )

# --- CHAT INTAKE ENGINE ---
if prompt:
    # 1. Print user message to UI
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt, unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Send message to the persistent AI Brain
    with st.chat_message("assistant", avatar=AI_AVATAR):
        with st.spinner("Analyzing Pyramid Global Portfolio..."):
            try:
                # Send ONLY the user's prompt. The AI already knows the database and the history.
                response = st.session_state.chat_session.send_message(prompt)
                
                st.markdown(response.text, unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"⚠️ An error occurred: {e}")







