import streamlit as st
import streamlit_authenticator as st_auth
from docx import Document
from langchain_openai.chat_models.base import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
# import pypdf

authenticator = st_auth.Authenticate(
    dict(st.secrets['credentials'].to_dict()),
    st.secrets['cookie']['name'],
    st.secrets['cookie']['key'],
    st.secrets['cookie']['expiry_days'],
    st.secrets['preauthorized']
)
# Redirect naar loginpagina als gebruiker niet is geauthenticeerd.
if st.session_state["authentication_status"] is None:
    st.switch_page('Login.py')
authenticator.logout(location='sidebar')

# Instantiate chat history in session state. This will hold the generated summary.

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "response" not in st.session_state:
    st.session_state.response = ""

template = """
Je bent een juridisch assistent die juristen helpt bij het maken van samenvattingen van jurisprudentie.
Werk zo accuraat mogelijk en volg de instructies van de gebruiker bij het produceren van je samenvatting.

instructies gebruiker: {instructies}
--------------------------------------------

tekst samenvatting: {brontekst}
"""
prompt = PromptTemplate.from_template(template)


@st.cache_data
def get_docx_text(path):
    """Gebruikt Python-Docx om alle text uit geüpload .docx bestand te halen.
     gebruikt st.cache_data om respons te cachen tussen streamlit script reruns"""
    document = Document(path)
    text = []
    for paragraph in document.paragraphs:
        text.append(paragraph.text)
    return '\n\n'.join(text)


def response_func():
    """Bouwt langchain LCEL chain uit componenten en geeft stream respons terug."""
    output_parser = StrOutputParser
    chain = prompt | model | output_parser()
    response = chain.stream({"instructies": st.session_state['gebruikersprompt'],
                             "brontekst": uploaded_file_text})
    return response


st.title('IBR AI Samenvatter voor Jurisprudentie')
st.header('Welkom, Rick')
st.divider()
uploaded_file = st.file_uploader(label='upload een bestand', type=['docx'], key='uploaded file',
                                 help='upload een .docx bestand')
# Settings menu
with st.expander(label='Instellingen', expanded=True):
    st.slider(label='lengte samenvatting in tokens', min_value=1, max_value=4096, key='max tokens',
              help='Éen token vertegenwoordigd ong. 3/4de van een woord')
    st.slider(label='toon samenvatting', min_value=0.0, max_value=1.0, key='temperature',
              help='de toon van de geproduceerde tekst. lager=zakelijker, hoger=vrijelijker')

# OpenAI model initialisatie
model = ChatOpenAI(model='gpt-4o', temperature=st.session_state['temperature'],
                   max_tokens=st.session_state['max tokens'],
                   api_key=st.secrets['OPENAI_API_KEY'],
                   organization=st.secrets['OPENAI_ORG_ID'])

# Geüpload bestand
uploaded_file_text = get_docx_text(uploaded_file)

# Weergave brontekst
with st.expander(label='Te samenvatten tekst', expanded=False):
    st.write(uploaded_file_text)
st.text_area(label='prompt', placeholder='Voer hier uw instructies voor de samenvatting in', key='gebruikersprompt')

# Samenvatten brontekst, weergeven respons LLM
if st.button(label='Start samenvatting', type='primary', use_container_width=True):
    with st.chat_message('AI'):
        response_text = st.write_stream(response_func())
    st.session_state['response'] = response_text

# Downloaden geproduceerd bestand
st.download_button(label='Download uw samenvatting', data=st.session_state['response'], file_name='samenvatting.docx',
                   mime='docx')
