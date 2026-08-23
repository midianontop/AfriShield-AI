import re

import streamlit as st

st.set_page_config(
    page_title="AfriShield AI Test",
    page_icon="🛡️"
)


def render_html(html: str) -> None:
    """
    Render a block of HTML via st.markdown, collapsing it to a single
    line first.

    Why this is necessary: Streamlit's markdown renderer (react-markdown
    + remark under the hood) has a long-standing, maintainer-confirmed
    class of bugs where multi-line HTML — especially HTML containing a
    newline inside an attribute, like a nicely-indented multi-line
    style="..." block — fails to render past the first line and prints
    the rest as literal escaped text instead of parsing it as tags. See
    streamlit/streamlit#859 and #1800 on GitHub for two confirmed reports
    of exactly this symptom.

    Collapsing every run of whitespace (including newlines) down to a
    single space sidesteps the underlying parser's newline-handling edge
    cases entirely, since a one-line HTML block has no line-break
    ambiguity left for it to misparse. This is the standard community
    workaround for this whole bug category.
    """
    single_line = re.sub(r"\s+", " ", html).strip()
    st.markdown(single_line, unsafe_allow_html=True)


st.title("🛡️ AfriShield AI")

st.write("Streamlit is working correctly.")

render_html(
    """
    <div style="
        padding: 20px;
        border-radius: 10px;
        background-color: #171A24;
        color: white;
    ">
        <h2>AfriShield AI</h2>
        <p>HTML rendering test successful.</p>
    </div>
    """
)

question = st.chat_input("Ask a cybersecurity question...")

if question:
    st.write("You asked:", question)