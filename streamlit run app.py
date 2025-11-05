{\rtf1\ansi\ansicpg949\cocoartf2865
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
import pandas as pd\
import io\
import uuid\
from google import genai\
from google.genai.errors import APIError\
\
# --- 1. \uc0\u54872 \u44221  \u49444 \u51221  \u48143  \u52488 \u44592 \u54868  ---\
\
# Gemini \uc0\u53364 \u46972 \u51060 \u50616 \u53944  \u48143  \u49464 \u49496  \u49345 \u53468  \u52488 \u44592 \u54868  \u54632 \u49688 \
def initialize_session():\
    """Streamlit \uc0\u49464 \u49496  \u49345 \u53468  \u48143  Gemini \u53364 \u46972 \u51060 \u50616 \u53944 \u47484  \u52488 \u44592 \u54868 \u54633 \u45768 \u45796 ."""\
    # API \uc0\u53412  \u52376 \u47532 \
    api_key = st.secrets.get("GEMINI_API_KEY")\
\
    # API \uc0\u53412 \u44032  secrets\u50640  \u50630 \u51004 \u47732  \u49324 \u51060 \u46300 \u48148 \u50640 \u49436  \u51077 \u47141 \u48155 \u44592 \
    if not api_key:\
        with st.sidebar:\
            st.warning("`st.secrets['GEMINI_API_KEY']`\uc0\u47484  \u52286 \u51012  \u49688  \u50630 \u49845 \u45768 \u45796 . \u53412 \u47484  \u51076 \u49884 \u47196  \u51077 \u47141 \u54644 \u51452 \u49464 \u50836 .")\
            api_key = st.text_input("Gemini API Key", type="password")\
            if not api_key:\
                st.info("\uc0\u44228 \u49549 \u54616 \u47140 \u47732  Gemini API \u53412 \u44032  \u54596 \u50836 \u54633 \u45768 \u45796 .")\
                return None\
    \
    # Gemini \uc0\u53364 \u46972 \u51060 \u50616 \u53944  \u52488 \u44592 \u54868 \
    try:\
        client = genai.Client(api_key=api_key)\
    except Exception as e:\
        st.error(f"Gemini \uc0\u53364 \u46972 \u51060 \u50616 \u53944  \u52488 \u44592 \u54868  \u49892 \u54056 : \{e\}")\
        return None\
\
    # \uc0\u49464 \u49496  \u49345 \u53468  \u52488 \u44592 \u54868 \
    if "session_id" not in st.session_state:\
        st.session_state.session_id = str(uuid.uuid4())\
    if "messages" not in st.session_state:\
        st.session_state.messages = []\
    if "log_history" not in st.session_state:\
        st.session_state.log_history = []\
    if "is_csv_logging_enabled" not in st.session_state:\
        st.session_state.is_csv_logging_enabled = True\
    if "model_name" not in st.session_state:\
        st.session_state.model_name = "gemini-2.0-flash"\
\
    return client\
\
client = initialize_session()\
\
# --- 2. \uc0\u49884 \u49828 \u53596  \u54532 \u47212 \u54532 \u53944  \u48143  \u47784 \u45944  \u49444 \u51221  ---\
\
# \uc0\u49324 \u50857 \u51088  \u50836 \u52397 \u50640  \u46384 \u47480  \u49884 \u49828 \u53596  \u54532 \u47212 \u54532 \u53944  \u51221 \u51032  (\u52828 \u51208 \u54620  \u51025 \u45824 , \u51221 \u48372  \u49688 \u51665 , \u51060 \u47700 \u51068  \u50836 \u52397 /\u44144 \u51208  \u50504 \u45236 )\
SYSTEM_PROMPT = """\
\uc0\u45817 \u49888 \u51008  \u49660 \u54609 \u47792  \u44256 \u44061  \u51025 \u45824  \u52311 \u48391 \u51077 \u45768 \u45796 . \u49324 \u50857 \u51088 \u45716  \u44396 \u47588  \u44284 \u51221 \u50640 \u49436  \u44202 \u51008  \u48520 \u54200 \u49324 \u54637 \u51060 \u45208  \u48520 \u47564 \u51012  \u51060 \u50556 \u44592 \u54616 \u44256  \u51080 \u49845 \u45768 \u45796 .\
\
1. \uc0\u47784 \u46304  \u51025 \u45813 \u51008  \u47588 \u50864  \u51221 \u51473 \u54616 \u44256  \u44277 \u44048  \u50612 \u47536  \u47568 \u53804 \u47484  \u49324 \u50857 \u54644 \u50556  \u54633 \u45768 \u45796 . \u49324 \u50857 \u51088 \u51032  \u44048 \u51221 \u51012  \u47676 \u51200  \u51064 \u51221 \u54616 \u44256  \u49324 \u44284 \u54616 \u49901 \u49884 \u50724 .\
2. \uc0\u49324 \u50857 \u51088 \u51032  \u48520 \u54200  \u49324 \u54637 \u51012  \u44396 \u52404 \u51201 \u51004 \u47196  (\u47924 \u50631 \u51060 /\u50616 \u51228 /\u50612 \u46356 \u49436 /\u50612 \u46523 \u44172 ) \u51221 \u47532 \u54616 \u50668  \u45812 \u45817 \u51088 \u50640 \u44172  \u51204 \u45804 \u54616 \u44592  \u50948 \u54620  \u54596 \u49688  \u51221 \u48372 \u47484  \u49688 \u51665 \u54644 \u50556  \u54633 \u45768 \u45796 .\
3. \uc0\u47784 \u46304  \u51221 \u48372  \u49688 \u51665 \u51060  \u50756 \u47308 \u46104 \u47732 , \u47560 \u51648 \u47561  \u51025 \u45813 \u50640 \u49436  "\u45812 \u45817 \u51088  \u54869 \u51064  \u54980  \u54924 \u49888 \u51012  \u50948 \u54644  \u51060 \u47700 \u51068  \u51452 \u49548 \u47484  \u50836 \u52397 \u46300 \u47549 \u45768 \u45796 . \u54924 \u49888  \u48155 \u51004 \u49892  \u51060 \u47700 \u51068  \u51452 \u49548 \u47484  \u50508 \u47140 \u51452 \u49884 \u44192 \u50612 \u50836 ?"\u46972 \u44256  \u50504 \u45236 \u54616 \u47728  \u51060 \u47700 \u51068  \u51452 \u49548 \u47484  \u50836 \u52397 \u54644 \u50556  \u54633 \u45768 \u45796 .\
4. \uc0\u47564 \u51068  \u49324 \u50857 \u51088 \u44032  \u50672 \u46973  \u51228 \u44277 \u51012  \u50896 \u52824  \u50506 \u45716 \u45796 \u44256  \u47749 \u49884 \u54616 \u47732 , \u47560 \u51648 \u47561  \u51025 \u45813 \u51004 \u47196  "\u51396 \u49569 \u54616 \u51648 \u47564 , \u50672 \u46973 \u52376  \u51221 \u48372 \u47484  \u48155 \u51648  \u47803 \u54616 \u50668  \u45812 \u45817 \u51088 \u51032  \u44160 \u53664  \u45236 \u50857 \u51012  \u48155 \u51004 \u49892  \u49688  \u50630 \u50612 \u50836 ."\u46972 \u44256  \u51221 \u51473 \u55176  \u50504 \u45236 \u54616 \u44256  \u45824 \u54868 \u47484  \u51333 \u47308 \u54616 \u49901 \u49884 \u50724 .\
"""\
\
# \uc0\u49440 \u53469  \u44032 \u45733 \u54620  \u47784 \u45944  \u47785 \u47197  (gemini-2.0-flash\u47484  \u44592 \u48376 \u44050 \u51004 \u47196 , -exp \u51228 \u50808 )\
AVAILABLE_MODELS = [\
    "gemini-2.0-flash",\
    "gemini-2.0-pro",\
    "gemini-2.5-flash",\
    "gemini-2.5-pro",\
    # \uc0\u45796 \u47480  \u47784 \u45944 \u51060  \u51080 \u45796 \u47732  \u50668 \u44592 \u50640  \u52628 \u44032 \
]\
\
# --- 3. Streamlit UI \uc0\u48143  \u44592 \u45733  \u54632 \u49688  ---\
\
def reset_chat():\
    """\uc0\u45824 \u54868  \u45236 \u50857  \u48143  \u47196 \u44536 \u47484  \u52488 \u44592 \u54868 \u54633 \u45768 \u45796 ."""\
    st.session_state.messages = []\
    st.session_state.log_history = []\
    st.session_state.session_id = str(uuid.uuid4())\
    st.toast("\uc0\u45824 \u54868 \u44032  \u52488 \u44592 \u54868 \u46104 \u50632 \u49845 \u45768 \u45796 . \u49352 \u47196 \u50868  \u44256 \u44061  \u51025 \u45824 \u47484  \u49884 \u51089 \u54633 \u45768 \u45796 .")\
\
def download_log():\
    """\uc0\u54788 \u51116  \u45824 \u54868  \u44592 \u47197 \u51012  CSV \u54028 \u51068 \u47196  \u45796 \u50868 \u47196 \u46300 \u54633 \u45768 \u45796 ."""\
    if not st.session_state.log_history:\
        st.warning("\uc0\u45796 \u50868 \u47196 \u46300 \u54624  \u45824 \u54868  \u44592 \u47197 \u51060  \u50630 \u49845 \u45768 \u45796 .")\
        return\
\
    df = pd.DataFrame(st.session_state.log_history)\
    csv = df.to_csv(index=False).encode('utf-8')\
    \
    st.download_button(\
        label="\uc0\u47196 \u44536  \u45796 \u50868 \u47196 \u46300  (.csv)",\
        data=csv,\
        file_name=f"chatbot_log_\{st.session_state.session_id\}.csv",\
        mime="text/csv",\
        key="download_csv"\
    )\
\
def log_message(role, content):\
    """\uc0\u45824 \u54868  \u45236 \u50857 \u51012  \u47196 \u44613  \u55176 \u49828 \u53664 \u47532 \u50640  \u44592 \u47197 \u54633 \u45768 \u45796 ."""\
    if st.session_state.is_csv_logging_enabled:\
        st.session_state.log_history.append(\{\
            "session_id": st.session_state.session_id,\
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),\
            "role": role,\
            "content": content\
        \})\
\
def generate_response(prompt):\
    """Gemini API\uc0\u47484  \u54840 \u52636 \u54616 \u50668  \u51025 \u45813 \u51012  \u49373 \u49457 \u54616 \u44256  \u45824 \u54868  \u55176 \u49828 \u53664 \u47532 \u47484  \u44288 \u47532 \u54633 \u45768 \u45796 ."""\
    \
    # 1. API\uc0\u50640  \u48372 \u45244  \u55176 \u49828 \u53664 \u47532  \u44396 \u49457  \u48143  \u44288 \u47532 \
    # \uc0\u49884 \u49828 \u53596  \u54532 \u47212 \u54532 \u53944 \u45716  messages\u50640  \u51200 \u51109 \u54616 \u51648  \u50506 \u44256  API \u54840 \u52636  \u49884 \u50640 \u47564  \u52628 \u44032 \
    history = []\
    for message in st.session_state.messages:\
        # role mapping: 'user' -> 'user', 'assistant' -> 'model'\
        history.append(\{"role": "user" if message["role"] == "user" else "model", "parts": [\{"text": message["content"]\}]\})\
    \
    # \uc0\u52572 \u44540  6\u53556 \u47564  \u50976 \u51648  (System prompt \u51228 \u50808 \u54620  5\u49933 : User/Model)\
    # \uc0\u52509  10\u44060 \u51032  \u47700 \u49884 \u51648  (5 User, 5 Model) + \u47560 \u51648 \u47561  \u49324 \u50857 \u51088  \u47700 \u49884 \u51648 \
    MAX_HISTORY_SIZE = 10 # 5\uc0\u53556  (User + Model)\
    if len(history) > MAX_HISTORY_SIZE:\
        history = history[-MAX_HISTORY_SIZE:]\
        st.info("\uc0\u45824 \u54868  \u44600 \u51060 \u44032  \u44600 \u50612 \u51256  API \u50836 \u52397  \u49884 \u50640 \u45716  \u52572 \u44540  5\u53556 \u47564  \u50976 \u51648 \u46121 \u45768 \u45796 .")\
\
    # 2. API \uc0\u54840 \u52636 \
    try:\
        response = client.models.generate_content(\
            model=st.session_state.model_name,\
            contents=history + [\{"role": "user", "parts": [\{"text": prompt\}]\}],\
            config=\{\
                "system_instruction": SYSTEM_PROMPT,\
            \}\
        )\
        return response.text\
\
    except APIError as e:\
        # API 429 \uc0\u50640 \u47084  \u46608 \u45716  \u45796 \u47480  API \u50640 \u47084  \u52376 \u47532 \
        st.error(f"API \uc0\u54840 \u52636  \u51473  \u50724 \u47448  \u48156 \u49373 : \{e\}")\
        st.warning("API \uc0\u54840 \u52636 \u50640  \u49892 \u54056 \u54664 \u49845 \u45768 \u45796 . \u51104 \u49884  \u54980  \u51116 \u49884 \u46020 \u54616 \u44144 \u45208 , \u45824 \u54868 \u47484  \u52488 \u44592 \u54868 \u54616 \u49901 \u49884 \u50724 .")\
        return "\uc0\u51396 \u49569 \u54633 \u45768 \u45796 . \u54788 \u51116  \u49884 \u49828 \u53596  \u50724 \u47448 \u47196  \u51064 \u54644  \u51025 \u45813 \u54624  \u49688  \u50630 \u49845 \u45768 \u45796 . \u51104 \u49884  \u54980  \u45796 \u49884  \u49884 \u46020 \u54644  \u51452 \u49884 \u44144 \u45208  '\u45824 \u54868  \u52488 \u44592 \u54868 ' \u48260 \u53948 \u51012  \u45580 \u47084 \u51452 \u49901 \u49884 \u50724 ."\
    except Exception as e:\
        # \uc0\u44592 \u53440  \u50696 \u50808  \u52376 \u47532 \
        st.error(f"\uc0\u50696 \u44592 \u52824  \u50506 \u51008  \u50724 \u47448  \u48156 \u49373 : \{e\}")\
        return "\uc0\u51396 \u49569 \u54633 \u45768 \u45796 . \u52376 \u47532  \u51473  \u50696 \u49345 \u52824  \u47803 \u54620  \u50724 \u47448 \u44032  \u48156 \u49373 \u54664 \u49845 \u45768 \u45796 ."\
\
\
# --- 4. Streamlit \uc0\u47700 \u51064  \u47112 \u51060 \u50500 \u50883  ---\
\
st.set_page_config(page_title="Gemini \uc0\u44256 \u44061  \u51025 \u45824  \u52311 \u48391 ", layout="wide")\
st.title("\uc0\u55357 \u57037 \u65039  Gemini \u44256 \u44061  \u51025 \u45824  \u52311 \u48391  (\u48520 \u47564  \u51217 \u49688 )")\
st.caption("\uc0\u51221 \u51473 \u54620  \u51025 \u45824 \u47196  \u48520 \u54200  \u49324 \u54637 \u51012  \u49688 \u51665 \u54616 \u44256  \u45812 \u45817 \u51088 \u50640 \u44172  \u51204 \u45804 \u54633 \u45768 \u45796 .")\
\
# \uc0\u49324 \u51060 \u46300 \u48148  (\u49444 \u51221  \u48143  \u44592 \u45733 )\
with st.sidebar:\
    st.header("\uc0\u49444 \u51221  \u48143  \u44592 \u45733 ")\
\
    # \uc0\u47784 \u45944  \u49440 \u53469 \
    st.session_state.model_name = st.selectbox(\
        "\uc0\u44592 \u48376  \u47784 \u45944  \u49440 \u53469 ",\
        options=AVAILABLE_MODELS,\
        index=AVAILABLE_MODELS.index(st.session_state.model_name)\
    )\
    st.caption(f"\uc0\u54788 \u51116  \u47784 \u45944 : **\{st.session_state.model_name\}**")\
    st.caption(f"\uc0\u49464 \u49496  ID: **\{st.session_state.session_id[:8]\}...**")\
    st.write("---")\
\
    # CSV \uc0\u47196 \u44613  \u50741 \u49496 \
    st.session_state.is_csv_logging_enabled = st.checkbox(\
        "CSV \uc0\u51088 \u46041  \u47196 \u44613  \u54876 \u49457 \u54868 ",\
        value=st.session_state.is_csv_logging_enabled\
    )\
    st.write("---")\
\
    # \uc0\u47196 \u44536  \u45796 \u50868 \u47196 \u46300  \u48143  \u45824 \u54868  \u52488 \u44592 \u54868 \
    download_log() # \uc0\u45796 \u50868 \u47196 \u46300  \u48260 \u53948  \u49373 \u49457  \u54632 \u49688  \u54840 \u52636 \
    if st.button("\uc0\u45824 \u54868  \u52488 \u44592 \u54868 ", type="primary"):\
        reset_chat()\
    st.write("---")\
    st.markdown("API Key\uc0\u45716  `st.secrets['GEMINI_API_KEY']`\u50640 \u49436  \u51088 \u46041  \u47196 \u46300 \u46121 \u45768 \u45796 . (\u50630 \u51004 \u47732  \u49345 \u45800  \u51077 \u47141 \u46976  \u49324 \u50857 )")\
\
# \uc0\u52488 \u44592  \u54872 \u50689  \u47700 \u49884 \u51648  (\u47700 \u49884 \u51648  \u47785 \u47197 \u51060  \u48708 \u50612  \u51080 \u51012  \u46412 \u47564 )\
if not st.session_state.messages:\
    initial_message = generate_response("\uc0\u50504 \u45397 \u54616 \u49464 \u50836 . \u48520 \u54200  \u49324 \u54637 \u51060  \u51080 \u50612  \u50672 \u46973 \u54616 \u49512 \u44400 \u50836 . \u51228 \u44032  \u46020 \u50752 \u46300 \u47540 \u44172 \u50836 .")\
    st.session_state.messages.append(\{"role": "assistant", "content": initial_message\})\
    log_message("assistant", initial_message)\
\
# \uc0\u45824 \u54868  \u55176 \u49828 \u53664 \u47532  \u52636 \u47141 \
for message in st.session_state.messages:\
    with st.chat_message(message["role"], avatar="\uc0\u55358 \u56598 " if message["role"] == "assistant" else "\u55357 \u56420 "):\
        st.markdown(message["content"])\
\
# \uc0\u49324 \u50857 \u51088  \u51077 \u47141  \u52376 \u47532 \
if user_prompt := st.chat_input("\uc0\u50668 \u44592 \u50640  \u48520 \u54200  \u49324 \u54637 \u51012  \u51077 \u47141 \u54616 \u49464 \u50836 ."):\
    # 1. \uc0\u49324 \u50857 \u51088  \u47700 \u49884 \u51648  \u52628 \u44032  \u48143  \u47196 \u44613 \
    st.session_state.messages.append(\{"role": "user", "content": user_prompt\})\
    log_message("user", user_prompt)\
    \
    # 2. \uc0\u49324 \u50857 \u51088  \u47700 \u49884 \u51648  \u52636 \u47141 \
    with st.chat_message("user", avatar="\uc0\u55357 \u56420 "):\
        st.markdown(user_prompt)\
\
    # 3. \uc0\u47784 \u45944  \u51025 \u45813  \u49373 \u49457  \u48143  \u52636 \u47141 \
    with st.chat_message("assistant", avatar="\uc0\u55358 \u56598 "):\
        with st.spinner("\uc0\u45813 \u48320 \u51012  \u49373 \u49457  \u51473 \u51077 \u45768 \u45796 ..."):\
            full_response = generate_response(user_prompt)\
            st.markdown(full_response)\
    \
    # 4. \uc0\u47784 \u45944  \u51025 \u45813  \u52628 \u44032  \u48143  \u47196 \u44613 \
    st.session_state.messages.append(\{"role": "assistant", "content": full_response\})\
    log_message("assistant", full_response)\
    \
    # 5. UI \uc0\u51088 \u46041  \u50629 \u45936 \u51060 \u53944 \
    st.rerun()\
}