"""
============================================================
 AfriShield AI
 African Offline Cybersecurity Intelligence Assistant

 Main Streamlit Application

 Version: 3.1
 Author: Midian
============================================================
"""


import streamlit as st
import json
import os


from retriever import search_documents
from generate_answer import generate_answer

from threat_detector import analyze_threat
from incident_response import get_incident_response

from incident_logger import save_incident
from scam_detector import detect_scam



# ============================================================
# PAGE CONFIGURATION
# ============================================================


st.set_page_config(

    page_title="AfriShield AI",

    page_icon="🛡️",

    layout="wide",

    initial_sidebar_state="expanded"

)



# Remove Streamlit Branding

st.markdown(
"""
<style>

#MainMenu {
    visibility:hidden;
}

footer {
    visibility:hidden;
}

header {
    visibility:hidden;
}

</style>
""",
unsafe_allow_html=True
)



# ============================================================
# SESSION STATE
# ============================================================


if "messages" not in st.session_state:

    st.session_state.messages = []



# ============================================================
# SIDEBAR
# ============================================================


with st.sidebar:


    st.title(
        "🛡️ AfriShield AI"
    )


    st.caption(
        "African AI Cybersecurity Intelligence Platform"
    )


    st.divider()



    # Incident Counter

    try:

        if os.path.exists(
            "incident_logs.json"
        ):


            with open(
                "incident_logs.json",
                "r"
            ) as f:

                logs = json.load(f)


            st.metric(

                "🚨 Incidents Logged",

                len(logs)

            )


        else:


            st.metric(

                "🚨 Incidents Logged",

                0

            )


    except:


        st.metric(

            "🚨 Incidents Logged",

            0

        )



    st.divider()



    st.success(
        "🟢 Threat Engine Ready"
    )


    st.success(
        "🟢 Scam Engine Ready"
    )


    st.success(
        "🟢 RAG Knowledge Base Ready"
    )


    st.success(
        "🟢 Llama 3.2 Offline AI Ready"
    )



    st.divider()



    st.subheader(
        "📊 Session Statistics"
    )


    st.metric(

        "Messages",

        len(
            st.session_state.messages
        )

    )


    threats = len(
        [
            m for m in st.session_state.messages
            if m.get("threat")
        ]
    )


    st.metric(

        "Threats Detected",

        threats

    )



    st.divider()



    if st.button(
        "🗑️ Clear Chat"
    ):

        st.session_state.messages = []

        st.rerun()



    st.divider()



    # Export Chat

    if st.session_state.messages:


        chat_data = json.dumps(

            st.session_state.messages,

            indent=4

        )


        st.download_button(

            label="⬇️ Export Chat",

            data=chat_data,

            file_name="afrishield_chat.json",

            mime="application/json"

        )



    st.divider()


    st.caption(
        "AfriShield AI v3.1"
    )

    st.caption(
        "Africa Deep Tech Challenge 2026"
    )





# ============================================================
# MAIN HEADER
# ============================================================


st.title(
    "🛡️ AfriShield AI Cybersecurity Assistant"
)


st.caption(
    "Offline African Cybersecurity Intelligence Platform powered by RAG + Llama 3.2"
)



st.divider()




# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================


for msg in st.session_state.messages:


    with st.chat_message(
        msg["role"]
    ):


        if msg["role"] == "assistant":



            if msg.get("threat"):


                st.warning(

f"""
🛡️ Threat Type:

{msg['threat']}


⚠️ Severity:

{msg['severity']}


📊 Confidence:

{msg['confidence']}%

"""
                )


                st.progress(

                    min(
                        int(msg["confidence"]),
                        100
                    )

                )



            if msg.get("scam"):


                st.error(

                    f"🚨 Scam Detected: {msg['scam']}"

                )



            st.markdown(

                msg["content"]

            )



            if msg.get(
                "recommendations"
            ):


                st.subheader(
                    "🛠 Recommended Actions"
                )


                for item in msg["recommendations"]:


                    st.success(
                        item
                    )



        else:


            st.write(
                msg["content"]
            )






# ============================================================
# USER INPUT
# ============================================================


question = st.chat_input(

    "Describe a cyber incident or ask a security question..."

)




if question:



    # Save User Message

    st.session_state.messages.append(

        {

            "role":"user",

            "content":question

        }

    )



    with st.chat_message(
        "user"
    ):

        st.write(
            question
        )



    with st.spinner(

        "🛡️ AfriShield AI analyzing..."

    ):



        # ----------------------------------------------------
        # Scam Detection
        # ----------------------------------------------------


        scam_result = detect_scam(
            question
        )



        # ----------------------------------------------------
        # Threat Analysis
        # ----------------------------------------------------


        analysis = analyze_threat(
            question
        )



        threat_type = None

        severity = None

        confidence = 0

        recommendations = []




        if analysis.category != "General Security Question":



            threat_type = analysis.category


            severity = analysis.severity.value


            confidence = analysis.confidence



            recommendations = get_incident_response(

                threat_type

            )



            save_incident(

                question,

                threat_type,

                severity,

                confidence

            )




        # ----------------------------------------------------
        # RAG Retrieval
        # ----------------------------------------------------


        documents = search_documents(

            question

        )


        context = "\n\n".join(

            documents

        )



        if threat_type:


            context += f"""

Threat Analysis:

Category:
{threat_type}

Severity:
{severity}

Confidence:
{confidence}%


Recommended Response:

{recommendations}

"""



        # ----------------------------------------------------
        # Generate Answer
        # ----------------------------------------------------


        answer = generate_answer(

            question,

            context

        )



        # ----------------------------------------------------
        # Scam Warning
        # ----------------------------------------------------


        if scam_result:


            answer = f"""

🚨 SCAM ALERT DETECTED


Scam Type:

{scam_result}



{answer}



Never share:


❌ Passwords

❌ OTP Codes

❌ BVN

❌ NIN

❌ ATM PIN

❌ Bank Details

"""





    # ========================================================
    # SAVE ASSISTANT MESSAGE
    # ========================================================


    st.session_state.messages.append(

        {


            "role":"assistant",


            "content":answer,


            "threat":threat_type,


            "severity":severity,


            "confidence":confidence,


            "recommendations":recommendations,


            "scam":scam_result


        }

    )




    # ========================================================
    # DISPLAY RESPONSE
    # ========================================================


    with st.chat_message(
        "assistant"
    ):



        if threat_type:


            st.warning(

f"""
🛡️ Threat:

{threat_type}


⚠️ Severity:

{severity}


"""

            )



            st.progress(

                min(
                    int(confidence),
                    100
                )

            )


            st.caption(

                f"📊 Confidence Score: {confidence}%"

            )



            with st.expander(

                "🔍 Threat Analysis Details"

            ):


                st.write(

                    "Intent:",

                    analysis.incident_type.value

                )


                st.write(

                    "Matched Signals:",

                    analysis.matched_keywords

                )





        if scam_result:


            st.error(

                f"🚨 Scam Alert: {scam_result}"

            )



        st.markdown(

            answer

        )



        if recommendations:


            st.subheader(

                "🛠 Recommended Actions"

            )


            for item in recommendations:


                st.success(

                    item

                )