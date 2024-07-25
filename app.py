import pytesseract
import io
import webbrowser
from io import BytesIO
import base64
import streamlit as st
from textblob import TextBlob
from langchain_groq import ChatGroq
import streamlit_scrollable_textbox as stx
import PyPDF2
from gtts import gTTS
from PIL import Image


st.set_page_config(page_title="LangVault", layout="wide")
st.title("LangVault 📑")

st.sidebar.title("LangVault By OpenRAG")
st.sidebar.markdown(
    """
    🌟 **Introducing LangVault by OpenRAG: Your translator Companion!** 📚

Get ready to experience a different world of books and documents with making and reading your own pdfs and books more accessible to everyone in different languages and make it available worldwide.
    """
)

def text_speech(text):
    tts = gTTS(text=text, lang='hi')
    speech_bytes = io.BytesIO()
    tts.write_to_fp(speech_bytes)
    speech_bytes.seek(0)
    return speech_bytes.read()

new_txt=""

def apply_spell_check(extracted_text):
    try:
        text = TextBlob(extracted_text)
        corrected_text = str(text.correct())
        return corrected_text
    except Exception as e:
        print("Error during spell check:", e)
        return None

def convert_pdf_to_images(pdf_bytes):
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
    for page in pdf_reader.pages:
        # Extract text from the page
        text = page.extract_text()
        yield text

def create_download_link(text, filename):
    text_bytes = text.encode()
    b64 = base64.b64encode(text_bytes).decode()
    download_link = f'<a href="data:text/plain;base64,{b64}" download="{filename}">Download text file</a>'
    return download_link

file = st.file_uploader("Choose a PDF file", type="pdf")
Lang = st.text_input("Enter The Language You want to translate your document into ")
butt = st.button("Submit")

# Hardcoded ChatGroq API key
chatgroq_api_key = "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"

tx = ""
original_txt = ""

if file is not None and butt and Lang:
    llm = ChatGroq(
        temperature=0,
        model="llama3-70b-8192",
        api_key=chatgroq_api_key
    )
    
    i = 0
    for text in convert_pdf_to_images(file.read()):
        i += 1
        st.write(f"Processing page {i}")
        result = llm.predict(f"Translate this text separated by triple backticks delimiter(```) \n Text: \n ```\n {text} \n ``` \n in {Lang} without changing its meaning")
        if result:
            stx.scrollableTextbox(result, height=400)
            b = result.replace("```", " ")
            st.audio(text_speech(str(b)))
        tx += "\n ----- \n" + result + "\n ----- \n"
    
    st.session_state.extracted_txt = tx

if "extracted_txt" in st.session_state:
    tx = st.session_state.extracted_txt  
    b = st.button("Download in txt format")
    if b:
        lnk2 = create_download_link(tx, "output_chatgroq.txt") 
        st.markdown(lnk2, unsafe_allow_html=True)
