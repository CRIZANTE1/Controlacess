import os
import pandas as pd
import streamlit as st 

def create_excel(file_path):
    if not os.path.exists(file_path):
        df = pd.DataFrame(columns=["Nome", "RG", "Placa", "Marca do Carro", "Horário de Entrada", "Horário de Saída", "Data", "Empresa", "Status da Entrada", "Motivo do Bloqueio", "Aprovador", "Data do Primeiro Registro"])
        df.to_excel(file_path, index=False)



def load_excel(file_path):
    required_columns = ["Nome", "RG", "Placa", "Marca do Carro", "Horário de Entrada", "Horário de Saída", "Data", "Empresa", "Status da Entrada", "Motivo do Bloqueio", "Aprovador", "Data do Primeiro Registro"]
    
    if os.path.exists(file_path):
        try:
            df = pd.read_excel(file_path)
            # Adiciona colunas que podem estar faltando em arquivos antigos
            for col in required_columns:
                if col not in df.columns:
                    df[col] = ""
        except Exception as e:
            st.error(f"Erro ao carregar a planilha: {e}")
            # Retorna um DataFrame vazio com todas as colunas necessárias em caso de erro
            df = pd.DataFrame(columns=required_columns)
    else:
        # Se o arquivo não existir, cria um novo DataFrame com todas as colunas necessárias e um novo arquivo Excel
        df = pd.DataFrame(columns=required_columns)
        try:
            df.to_excel(file_path, index=False)
        except Exception as e:
            st.error(f"Erro ao criar a planilha: {e}")
    return df


def save_to_excel(df, file_path):
    df.to_excel(file_path, index=False)
