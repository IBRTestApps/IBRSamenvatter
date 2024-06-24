import streamlit as st
import streamlit_authenticator as st_auth

authenticator = st_auth.Authenticate(
    dict(st.secrets['credentials'].to_dict()),
    st.secrets['cookie']['name'],
    st.secrets['cookie']['key'],
    st.secrets['cookie']['expiry_days'],
    st.secrets['preauthorized']
)
authenticator.login(location='main')
if st.session_state["authentication_status"]:
    st.switch_page('pages/Samenvatter.py')
elif st.session_state["authentication_status"] is False:
    st.error('Gebruikersnaam/wachtwoord is incorrect')
elif st.session_state["authentication_status"] is False:
    st.warning('Voer uw gebruikersnaam en wachtwoord in')