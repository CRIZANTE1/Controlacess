import os
import pandas as pd

def create_excel(file_path):
    if not os.path.exists(file_path):
        df = pd.DataFrame(columns=["Nome", "RG", "Placa", "Marca do Carro", "Horário de Entrada", "Horário de Saída", "Data", "Empresa"])
        df.to_excel(file_path, index=False)

import streamlit as st # Importar streamlit para exibir mensagens de erro

def load_excel(file_path):
    if os.path.exists(file_path):
        try:
            df = pd.read_excel(file_path)
        except Exception as e:
            st.error(f"Erro ao carregar a planilha: {e}")
            # Retorna um DataFrame vazio com as colunas esperadas em caso de erro
            df = pd.DataFrame(columns=["Nome", "RG", "Placa", "Marca do Carro", "Horário de Entrada", "Horário de Saída", "Data", "Empresa"])
    else:
        # Se o arquivo não existir, cria um novo DataFrame e um novo arquivo Excel
        df = pd.DataFrame(columns=["Nome", "RG", "Placa", "Marca do Carro", "Horário de Entrada", "Horário de Saída", "Data", "Empresa"])
        try:
            df.to_excel(file_path, index=False)
        except Exception as e:
            st.error(f"Erro ao criar a planilha: {e}")
    return df


def save_to_excel(df, file_path):
    df.to_excel(file_path, index=False)
