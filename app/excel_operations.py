import os
import pandas as pd
import streamlit as st

# Flag para ativar o modo de demonstração
DEMO_MODE = True

def create_excel(file_path):
    if not os.path.exists(file_path) and not DEMO_MODE:
        df = pd.DataFrame(columns=["Nome", "RG", "Placa", "Marca do Carro", "Horário de Entrada", "Horário de Saída", "Data", "Empresa", "Status da Entrada", "Motivo do Bloqueio", "Aprovador", "Data do Primeiro Registro"])
        df.to_excel(file_path, index=False)


def load_excel(file_path):
    required_columns = ["Nome", "RG", "Placa", "Marca do Carro", "Horário de Entrada", "Horário de Saída", "Data", "Empresa", "Status da Entrada", "Motivo do Bloqueio", "Aprovador", "Data do Primeiro Registro"]

    if DEMO_MODE:
        st.warning("Modo de demonstração ativo. Carregando dados fictícios.")
        data = {
            "Nome": ["João Silva", "Maria Souza", "Pedro Santos"],
            "RG": ["11.111.111-1", "22.222.222-2", "33.333.333-3"],
            "Placa": ["ABC-1234", "DEF-5678", "GHI-9012"],
            "Marca do Carro": ["Fiat Palio", "VW Gol", "Chevrolet Onix"],
            "Horário de Entrada": ["08:00", "09:00", "10:00"],
            "Horário de Saída": ["17:00", "18:00", "19:00"],
            "Data": ["21/05/2025", "21/05/2025", "21/05/2025"],
            "Empresa": ["Empresa A", "Empresa B", "Empresa C"],
            "Status da Entrada": ["Liberado", "Liberado", "Bloqueado"],
            "Motivo do Bloqueio": ["", "", "Documentação pendente"],
            "Aprovador": ["", "", "Ana Costa"],
            "Data do Primeiro Registro": ["20/05/2025", "20/05/2025", "19/05/2025"]
        }
        df = pd.DataFrame(data)
    else:
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
    if not DEMO_MODE:
        df.to_excel(file_path, index=False)
    else:
        st.info("Modo de demonstração ativo. As alterações não serão salvas no Banco de dados.")
