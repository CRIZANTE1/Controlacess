import streamlit as st
from app.ui_interface import vehicle_access_interface
from app.data_operations import mouth_consult

st.set_page_config(page_title="Controle de Integração", layout="wide")

st.warning('Esta é uma versão de teste. Para mais informações, entre em contato com o desenvolvedor: Cristian Ferreira Carlos, CE9X, +55 11 3103-8708, cristiancarlos@vibraenergia.com.br')

def main():
    st.sidebar.title("Bem-vindo (Versão de Teste)")
    page = st.sidebar.selectbox("Escolha a página:", ["Controle de Acesso"])

    if page == "Controle de Acesso":
        vehicle_access_interface()
        mouth_consult()
   

    st.caption('Desenvolvido por Cristian Ferreira Carlos, CE9X, +551131038708, cristiancarlos@vibraenergia.com.br')

if __name__ == "__main__":
    main()
