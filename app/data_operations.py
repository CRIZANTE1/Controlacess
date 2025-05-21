import pandas as pd
from app.excel_operations import save_to_excel
from datetime import datetime, timedelta
import streamlit as st
import time
import locale

def show_progress_bar(progress_placeholder):
    progress_text = "Aguarde o carregamento da página..."
    with st.spinner(progress_text):
        for _ in range(100):
            time.sleep(0.010)
    

def initialize_columns(df):
    """Certifica-se de que todas as colunas necessárias estão presentes no DataFrame"""
    required_columns = [
        "Nome", "RG", "Placa", "Marca do Carro", "Horário de Entrada", 
        "Data", "Empresa", "Status da Entrada", "Motivo do Bloqueio", "Aprovador", "Data do Primeiro Registro"
    ]
    for column in required_columns:
        if column not in df.columns:
            df[column] = ""
    return df

def check_briefing_needed(df, name, current_date):
    """
    Verifica se um visitante precisa fazer o briefing baseado em seu histórico completo.
    
    Args:
        df (pd.DataFrame): DataFrame com todos os registros
        name (str): Nome do visitante
        current_date (str): Data atual no formato dd/mm/yyyy
    
    Returns:
        tuple: (precisa_briefing, motivo)
            precisa_briefing: True se precisar fazer briefing
            motivo: String explicando o motivo
    """
    # Pegar todos os registros do visitante
    visitor_records = df[df["Nome"] == name].copy()
    
    if visitor_records.empty:
        return True, "primeiro_acesso"
        
    try:
        # Converter a data atual para datetime
        current_date = datetime.strptime(current_date, "%d/%m/%Y")
        
        # Converter todas as datas para datetime
        visitor_records["Data"] = pd.to_datetime(visitor_records["Data"], format="%d/%m/%Y")
        
        # Encontrar a data do acesso mais recente
        last_access = visitor_records["Data"].max()
        
        # Calcular a diferença em dias
        days_since_last_access = (current_date - last_access).days
        
        if days_since_last_access >= 365:
            return True, "mais_de_um_ano"
        
        return False, None
        
    except ValueError as e:
        st.error(f"Erro ao processar datas: {str(e)}")
        return False, None

def add_record(name, rg, placa, marca_carro, horario_entrada, data, empresa, status, motivo=None, aprovador=None, df=None, file_path=None):
    df = initialize_columns(df)  # Certifique-se de que todas as colunas necessárias estão presentes
    
    # Função auxiliar para formatar data
    def format_date(date_str):
        try:
            # Tenta primeiro o formato dd/mm/yyyy
            return datetime.strptime(date_str, "%d/%m/%Y").strftime("%d/%m/%Y")
        except ValueError:
            try:
                # Tenta o formato yyyy-mm-dd
                return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
            except ValueError:
                try:
                    # Tenta converter de timestamp se for um objeto datetime
                    return date_str.strftime("%d/%m/%Y")
                except AttributeError:
                    return None

    # Formatar a data do novo registro
    data_formatada = format_date(data)
    if not data_formatada:
        st.error(f"Erro: Data '{data}' está em um formato inválido.")
        return df

    # Verificar necessidade de briefing
    needs_briefing, motivo = check_briefing_needed(df, name, data_formatada)
    if needs_briefing:
        mensagem = "ATENÇÃO! {} precisa fazer o briefing de segurança pois {}.".format(
            name,
            "é seu primeiro acesso" if motivo == "primeiro_acesso" else "já se passou mais de 1 ano desde seu último acesso"
        )
        st.warning(mensagem)

    # Verifica se já existe um registro com o mesmo nome e data
    existing_record = df[(df["Nome"] == name) & (df["Data"] == data_formatada)]

    if not existing_record.empty:
        # Atualiza o registro existente
        df.loc[(df["Nome"] == name) & (df["Data"] == data_formatada), [
            "RG", "Placa", "Marca do Carro", "Horário de Entrada", "Empresa", 
            "Status da Entrada", "Motivo do Bloqueio", "Aprovador"
        ]] = [rg, placa, marca_carro, horario_entrada, empresa, status, motivo if motivo else "", aprovador if aprovador else ""]
        
        # Mantém a Data do Primeiro Registro existente
        first_reg_date = df.loc[(df["Nome"] == name) & (df["Data"] == data_formatada), "Data do Primeiro Registro"].iloc[0]
        if not first_reg_date or pd.isna(first_reg_date):
            first_reg_date = data_formatada
        df.loc[(df["Nome"] == name) & (df["Data"] == data_formatada), "Data do Primeiro Registro"] = first_reg_date

    else:
        # Adiciona um novo registro
        # Verifica se já existe algum registro para este visitante
        existing_visitor_records = df[df["Nome"] == name]

        if existing_visitor_records.empty:
            # É o primeiro registro para este visitante
            first_registration_date = data_formatada
        else:
            # Pega a data mais antiga entre todos os registros existentes
            existing_dates = existing_visitor_records["Data"].dropna()
            if existing_dates.empty:
                first_registration_date = data_formatada
            else:
                try:
                    # Converte todas as datas para datetime para comparação
                    dates = pd.to_datetime(existing_dates, format="%d/%m/%Y")
                    first_registration_date = min(dates).strftime("%d/%m/%Y")
                except ValueError:
                    first_registration_date = data_formatada

        new_record = {
            "Nome": name,
            "RG": rg,
            "Placa": placa,
            "Marca do Carro": marca_carro,
            "Horário de Entrada": horario_entrada,
            "Data": data_formatada,
            "Empresa": empresa,
            "Status da Entrada": status,
            "Motivo do Bloqueio": motivo if motivo else "",
            "Aprovador": aprovador if aprovador else "",
            "Data do Primeiro Registro": first_registration_date
        }
        new_record_df = pd.DataFrame([new_record])
        df = pd.concat([df, new_record_df], ignore_index=True)

    if file_path:
        df.to_excel(file_path, index=False)
    
    return df


def update_exit_time(name, date, new_exit_time, df, file_path):
    # Atualiza o horário de saída para o registro especificado
    df.loc[(df["Nome"] == name) & (df["Data"] == date), "Horário de Saída"] = new_exit_time
    
    # Salva o DataFrame atualizado no arquivo Excel
    df.to_excel(file_path, index=False)
    
    return df, "Horário de saída atualizado com sucesso!"


def delete_record(name, data, df, file_path):
    name_lower = name.lower()
    df['Nome_lower'] = df['Nome'].str.lower()  # Adiciona uma coluna temporária para facilitar a comparação

    df = df[~((df['Nome_lower'] == name_lower) & (df['Data'] == data))]
    df.drop(columns=['Nome_lower'], inplace=True)  # Remove a coluna temporária
    if file_path:
        df.to_excel(file_path, index=False)
    return df

from datetime import datetime

def check_entry(df, name, data):
    # Converte o nome para minúsculas
    name_lower = name.lower()
    
    # Adiciona uma coluna temporária com o nome em minúsculas para facilitar a comparação
    df['Nome_lower'] = df['Nome'].str.lower()

    # Exibe o dataframe temporário para depuração (descomente para verificar)
    # st.write(df[['Nome', 'Nome_lower', 'Data']])

    # Verifica se a data foi fornecida ou não
    if data:
        person = df[(df['Nome_lower'] == name_lower) & (df['Data'] == data)]
    else:
        person = df[df['Nome_lower'] == name_lower]
    
    # Remove a coluna temporária após a comparação
    df.drop(columns=['Nome_lower'], inplace=True)
    
    # Verifica se algum registro foi encontrado
    if not person.empty:
        return person.iloc[0], "Registro encontrado."
    else:
        return None, "Nome e/ou data não encontrados."


    

def check_blocked_records(df):
    """
    Verifica se há registros bloqueados e aplica a lógica de liberação recente.
    """
    # Filtra os registros bloqueados
    blocked_records = df[df['Status da Entrada'] == 'Bloqueada']

    # Obtém a data mais recente de liberação para cada nome
    recent_release_dates = df[df['Status da Entrada'] == 'Liberada'].groupby('Nome')['Data'].max()

    def should_show_block(record):
        name = record['Nome']
        block_date = datetime.strptime(record['Data'], '%d/%m/%Y')
        recent_release_date = recent_release_dates.get(name)
        
        if recent_release_date:
            recent_release_date = datetime.strptime(recent_release_date, '%d/%m/%Y')
            return block_date > recent_release_date
        return True

    # Gera a informação de bloqueios que devem ser mostrados
    blocked_info = "\n".join([
        f"Nome: {row['Nome']}, Data: {row['Data']}, Placa: {row['Placa']}, Motivo: {row['Motivo do Bloqueio']}"
        for _, row in blocked_records.iterrows()
        if should_show_block(row)
    ])

    return blocked_info if blocked_info else None


def get_block_info(df, name):
    """
    Obtém o número de bloqueios e os motivos de bloqueio para uma pessoa específica.

    Args:
        df (pd.DataFrame): DataFrame contendo os dados dos registros.
        name (str): Nome da pessoa para consultar.

    Returns:
        tuple: Contém o número de bloqueios e uma lista de motivos.
    """
    person_records = df[df["Nome"] == name]
    blocked_records = person_records[person_records["Status da Entrada"] == "Bloqueada"]
    num_blocks = len(blocked_records)
    reasons = blocked_records["Motivo do Bloqueio"].dropna().unique()
    
    return num_blocks, reasons


#-------------------------------------- Fase de teste ---------------------


def mouth_consult(): # Consulta por mês as entradas de uma pessoa especifica
    with st.expander("Consultar Registro por Nome e Mês", expanded=False):
        unique_names = st.session_state.df_acesso_veiculos["Nome"].unique()
        name_to_check_month = st.selectbox("Nome para consulta por mês:", options=unique_names)
        month_to_check = st.date_input("Mês e ano para consulta:", value=datetime.now())

        if st.button("Verificar Registros do Mês"):
            if name_to_check_month and month_to_check:
                start_date = pd.Timestamp(month_to_check.replace(day=1))
                end_date = (start_date + pd.DateOffset(months=1)) - pd.DateOffset(days=1)
                
                mask = (
                    (st.session_state.df_acesso_veiculos["Nome"] == name_to_check_month) &
                    (pd.to_datetime(st.session_state.df_acesso_veiculos["Data"], format="%d/%m/%Y") >= start_date) &
                    (pd.to_datetime(st.session_state.df_acesso_veiculos["Data"], format="%d/%m/%Y") <= end_date)
                )
                filtered_df = st.session_state.df_acesso_veiculos[mask]
                
                if not filtered_df.empty:
                    # Set the locale to pt_BR
                    locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')
                    st.write(f"Registros de {name_to_check_month} para o mês de {month_to_check.strftime('%B %Y')}:")
                    st.dataframe(filtered_df)
                else:
                    st.warning(f"Nenhum registro encontrado para {name_to_check_month} no mês de {month_to_check.strftime('%B %Y')}.")
            else:
                st.warning("Por favor, selecione o nome e o mês para consulta.")
