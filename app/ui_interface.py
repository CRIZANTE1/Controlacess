import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from app.excel_operations import create_excel, load_excel, save_to_excel
from app.data_operations import add_record, update_exit_time, delete_record, check_entry, check_blocked_records, get_block_info

def generate_time_options():
    times = []
    start_time = datetime.strptime("00:00", "%H:%M")
    end_time = datetime.strptime("23:59", "%H:%M")

    current_time = start_time
    while current_time <= end_time:
        times.append(current_time.strftime("%H:%M"))
        current_time += timedelta(minutes=1)
    
    return times

def round_to_nearest_interval(time_value, interval=1):
    """Arredonda o horário para o intervalo mais próximo"""
    if pd.isna(time_value) or time_value == "":
        return "00:00"  # Valor padrão para NaN ou string vazia
    
    if isinstance(time_value, (int, float)):
        hours = int(time_value // 60)
        minutes = int(time_value % 60)
        time_str = f"{hours:02d}:{minutes:02d}"
    else:
        time_str = str(time_value)
    
    # Verificar se o valor está no formato esperado
    try:
        time = datetime.strptime(time_str, "%H:%M")
    except ValueError:
        return "00:00"  # Valor padrão se o formato estiver incorreto
    
    minutes = (time.hour * 60 + time.minute) // interval * interval
    rounded_time = datetime.strptime(f"{minutes // 60:02d}:{minutes % 60:02d}", "%H:%M")
    return rounded_time.strftime("%H:%M")

def vehicle_access_interface():
    # Caminho para o arquivo da planilha
    file_path = "data/controle_acesso_veiculos.xlsx"

    # Cria a planilha se não existir
    create_excel(file_path)

    # Carrega os dados no estado da sessão se ainda não estiverem carregados
    if 'df_acesso_veiculos' not in st.session_state:
        st.session_state.df_acesso_veiculos = load_excel(file_path)

    st.title("Controle de Acesso de Veículos")
    
    # BRIEFING DE SEGURANGA
    with st.expander('Briefing de segurança', expanded=True):
        st.write("**ATENÇÃO:**\n\n"
                 "1. O acesso de veículos deve ser controlado rigorosamente para garantir a segurança do local.\n"
                 "2. Apenas pessoas autorizadas podem liberar o acesso.\n"
                 "3. Em caso de dúvidas, entre em contato com o responsável pela segurança.\n"
                 "4. Mantenha sempre os dados atualizados e verifique as informações antes de liberar o acesso."
                 "\n5. Sempre que for a primeira vez do visitante ou um ano do acesso repassar o video.\n")
        # Adicionar vídeo
        try:
            st.video("data/exemplo.mp4") # Caminho relativo para o vídeo
        except Exception as e:
            st.warning(f"Erro ao carregar o vídeo: {e}")
            st.write("Insira o vídeo manualmente no diretório correto.")
        
    blocks()
    
    # Adicionar ou editar registro
    with st.expander("Adicionar ou Editar Registro", expanded=True):
        unique_names = st.session_state.df_acesso_veiculos["Nome"].unique()
        name_to_add_or_edit = st.selectbox("Selecionar Nome para Adicionar ou Editar:", options=["Novo Registro"] + list(unique_names))
        
        horario_options = generate_time_options()
        default_horario = round_to_nearest_interval(datetime.now().strftime("%H:%M"))

        if name_to_add_or_edit == "Novo Registro":
            # Campos para adicionar novo registro
            name = st.text_input("Nome:")
            rg = st.text_input("RG:")
            placa = st.text_input("Placa do Carro (opcional):")
            marca_carro = st.text_input("Marca do Carro (opcional):")
            data = st.date_input("Data:")
            horario_entrada = st.selectbox("Horário de Entrada:", options=horario_options, index=horario_options.index(default_horario))
            empresa = st.text_input("Empresa:")
            status = st.selectbox("Status de Entrada", ["Liberada", "Bloqueada"], index=0)  # "Liberada" como padrão
            motivo = st.text_input("Motivo do Bloqueio") if status == "Bloqueada" else ""
            aprovador = st.text_input("Aprovador") if status == "Liberada" else ""

            # Exibe a mensagem de alerta se o status for "Bloqueada"
            if status == "Bloqueada":
                st.warning("A liberação só pode ser feita pelo responsável pela segurança ou gerente.")

            # Carregar os dados antes de adicionar o novo registro para verificar a existência do nome
            df_before_add = st.session_state.df_acesso_veiculos.copy()

            if st.button("Adicionar Registro"):
                if name and rg and horario_entrada and data and empresa:
                    # Converter a data para o formato correto
                    data_obj = datetime.strptime(data.strftime("%Y-%m-%d"), "%Y-%m-%d")
                    data_formatada = data_obj.strftime("%d/%m/%Y")

                    try:
                        st.session_state.df_acesso_veiculos = add_record(
                            name, rg, placa, marca_carro, 
                            horario_entrada, 
                            data_formatada,  # Usando a data formatada
                            empresa, 
                            status, 
                            motivo, 
                            aprovador,
                            st.session_state.df_acesso_veiculos, 
                            file_path
                        )
                        st.success("Registro adicionado com sucesso!")

                        # Obter o registro recém-adicionado/atualizado para acessar a Data do Primeiro Registro
                        added_record = st.session_state.df_acesso_veiculos[
                            (st.session_state.df_acesso_veiculos["Nome"] == name) & 
                            (st.session_state.df_acesso_veiculos["Data"] == data_formatada)
                        ].iloc[0]
                    except Exception as e:
                        st.error(f"Erro ao adicionar registro: {e}")
                        added_record = None # Definir como None para evitar erro no próximo bloco

                    first_registration_date_str = added_record["Data do Primeiro Registro"]
                    current_record_date_str = added_record["Data"]

                    needs_briefing = False
                    try:
                        first_registration_date = datetime.strptime(first_registration_date_str, "%d/%m/%Y").date()
                        current_record_date = datetime.strptime(current_record_date_str, "%d/%m/%Y").date()
                        
                        # Verificar se é o primeiro registro ou se passou mais de um ano
                        days_difference = (current_record_date - first_registration_date).days
                        if first_registration_date == current_record_date or days_difference >= 365:
                            needs_briefing = True
                            
                        if needs_briefing:
                            st.warning(f"ATENÇÃO! {name} precisa fazer o briefing de segurança pois {'é seu primeiro acesso' if first_registration_date == current_record_date else 'já se passou mais de 1 ano desde seu último briefing'}.")

                    except ValueError:
                        st.warning(f"Não foi possível verificar a data do primeiro registro para {name}. Por favor, verifique o formato da data.")

                else:
                    st.warning("Por favor, preencha todos os campos obrigatórios: Nome, RG, Horário de Entrada, Data e Empresa.")
        else:
            # Campos para editar registro existente
            existing_record = st.session_state.df_acesso_veiculos[st.session_state.df_acesso_veiculos["Nome"] == name_to_add_or_edit].iloc[0]
            
            rg = st.text_input("RG:", value=existing_record["RG"])
            placa = st.text_input("Placa do Carro (opcional):", value=existing_record["Placa"])
            marca_carro = st.text_input("Marca do Carro (opcional):", value=existing_record["Marca do Carro"])
            data = st.date_input("Data:", value=datetime.strptime(existing_record["Data"], "%d/%m/%Y"))
            horario_entrada = st.selectbox(
                "Horário de Entrada:",
                options=horario_options,
                index=horario_options.index(round_to_nearest_interval(existing_record["Horário de Entrada"]))
                if existing_record["Horário de Entrada"] not in [None, ""] else 0  # Fallback para o primeiro índice se o valor for vazio
            )
            empresa = st.text_input("Empresa:", value=existing_record["Empresa"])

            # Verifica se o valor de Status da Entrada não é NaN e ajusta o índice do selectbox
            status_options = ["Liberada", "Bloqueada"]
            status_value = existing_record["Status da Entrada"]
            if pd.isna(status_value) or status_value not in status_options:
                status_value = status_options[0]  # Valor padrão se não estiver na lista

            status = st.selectbox(
                "Status de Entrada",
                status_options,
                index=status_options.index(status_value)
            )
            motivo = st.text_input("Motivo do Bloqueio", value=existing_record["Motivo do Bloqueio"]) if status == "Bloqueada" else ""
            aprovador = st.text_input("Aprovador", value=existing_record["Aprovador"]) if status == "Liberada" else ""

            # Depuração: Exibir valores de datas para comparação
            #st.write(f"Data existente no registro: {existing_record['Data']}")
            #st.write(f"Data selecionada: {data.strftime('%d/%m/%Y')}")

            # Verifica se a data é igual à data existente no registro
            if existing_record["Data"] == data.strftime('%d/%m/%Y'):
                st.warning("Editando o registro existente")

            # Exibe a mensagem de alerta se o status for "Bloqueada"
            if status == "Bloqueada":
                st.warning("A liberação só pode ser feita pelo responsável por profissional dá área responsável ou Gestor da UO.")

            if st.button("Atualizar Registro"):
                if rg and horario_entrada and data and empresa:
                    # Converter a data para o formato correto
                    data_obj = datetime.strptime(data.strftime("%Y-%m-%d"), "%Y-%m-%d")
                    data_formatada = data_obj.strftime("%d/%m/%Y")

                    st.session_state.df_acesso_veiculos = add_record(
                        name_to_add_or_edit, 
                        rg, 
                        placa, 
                        marca_carro, 
                        horario_entrada, 
                        data_formatada,  # Usando a data formatada
                        empresa, 
                        status, 
                        motivo, 
                        aprovador,
                        st.session_state.df_acesso_veiculos, 
                        file_path
                    )
                    st.success("Registro atualizado com sucesso!")

                    # Verificar necessidade de briefing após atualização
                    updated_record = st.session_state.df_acesso_veiculos[
                        (st.session_state.df_acesso_veiculos["Nome"] == name_to_add_or_edit) & 
                        (st.session_state.df_acesso_veiculos["Data"] == data_formatada)
                    ].iloc[0]

                    first_registration_date_str = updated_record["Data do Primeiro Registro"]
                    current_record_date_str = updated_record["Data"]

                    needs_briefing = False
                    try:
                        first_registration_date = datetime.strptime(first_registration_date_str, "%d/%m/%Y").date()
                        current_record_date = datetime.strptime(current_record_date_str, "%d/%m/%Y").date()
                        
                        # Verificar se passou mais de um ano
                        days_difference = (current_record_date - first_registration_date).days
                        if days_difference >= 365:
                            needs_briefing = True
                            
                        if needs_briefing:
                            st.warning(f"ATENÇÃO! {name_to_add_or_edit} precisa fazer o briefing de segurança pois já se passou mais de 1 ano desde seu último briefing.")

                    except ValueError:
                        st.warning(f"Não foi possível verificar a data do primeiro registro para {name_to_add_or_edit}. Por favor, verifique o formato da data.")

                else:
                    st.warning("Por favor, preencha todos os campos obrigatórios: RG, Horário de Entrada, Data e Empresa.")
                
                

    # Atualizar horário de saída
    with st.expander("Atualizar Horário de Saída", expanded=False):
        unique_names = st.session_state.df_acesso_veiculos["Nome"].unique()
        name_to_update = st.selectbox("Nome do registro para atualizar horário de saída:", options=unique_names)
        data_to_update = st.date_input("Data do registro para atualizar horário de saída:", key="data_saida")
        horario_saida_options = generate_time_options()
        default_horario_saida = round_to_nearest_interval(datetime.now().strftime("%H:%M"))
        horario_saida = st.selectbox("Novo Horário de Saída (HH:MM):", options=horario_saida_options, index=horario_saida_options.index(default_horario_saida), key="horario_saida")

        if st.button("Atualizar Horário de Saída"):
            if name_to_update and data_to_update and horario_saida:
                try:
                    data_to_update = datetime.strptime(data_to_update.strftime("%Y-%m-%d"), "%Y-%m-%d")
                    st.session_state.df_acesso_veiculos, status = update_exit_time(
                        name_to_update, 
                        data_to_update.strftime("%d/%m/%Y"), 
                        horario_saida, 
                        st.session_state.df_acesso_veiculos, 
                        file_path
                    )
                    st.success(status)
                except Exception as e:
                    st.error(f"Erro ao atualizar horário de saída: {e}")
            else:
                st.warning("Por favor, selecione o nome, a data e o novo horário de saída.")
                

    # Deletar registro
    with st.expander("Deletar Registro", expanded=False):
        unique_names = st.session_state.df_acesso_veiculos["Nome"].unique()
        name_to_delete = st.selectbox("Nome do registro a ser deletado:", options=unique_names)
        data_to_delete = st.date_input("Data do registro a ser deletado:", key="data_delete")

        if st.button("Deletar Registro"):
            if name_to_delete and data_to_delete:
                try:
                    data_to_delete = datetime.strptime(data_to_delete.strftime("%Y-%m-%d"), "%Y-%m-%d")
                    st.session_state.df_acesso_veiculos = delete_record(
                        name_to_delete, 
                        data_to_delete.strftime("%d/%m/%Y"), 
                        st.session_state.df_acesso_veiculos, 
                        file_path
                    )
                    st.success("Registro deletado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao deletar registro: {e}")
            else:
                st.warning("Por favor, selecione o nome e a data do registro a ser deletado.")
    

    
# Consultar por Nome
    with st.expander("Consultar Registro por Nome", expanded=False):
        unique_names = st.session_state.df_acesso_veiculos["Nome"].unique()
        name_to_check = st.selectbox("Nome para consulta:", options=unique_names)

        if st.button("Verificar Registro"):
            if name_to_check:
                try:
                    # Chama a função de verificação com apenas o nome
                    person, status = check_entry(
                        st.session_state.df_acesso_veiculos, 
                        name_to_check, 
                        None  # Não é mais necessário passar a data
                    )
                    if person is not None:
                        # Exibe as informações básicas do registro
                        st.write(f"Nome: {person['Nome']}")
                        st.write(f"Placa: {person['Placa']}")
                        st.write(f"Marca do Carro: {person['Marca do Carro']}")
                        st.write(f"Horário de Entrada: {person['Horário de Entrada']}")
                        st.write(f"Horário de Saída: {person['Horário de Saída']}")
                        st.write(f"Empresa: {person['Empresa']}")
                        st.write(f"Status de Entrada: {person['Status da Entrada']}")

                        # Exibe o motivo do bloqueio e o aprovador somente se o status for "Bloqueada"
                        if person['Status da Entrada'] == 'Bloqueada':
                            st.write(f"Motivo do Bloqueio: {person['Motivo do Bloqueio']}")
                            st.write(f"Aprovador do Bloqueio: {person['Aprovador']}")
                        else:
                            st.write(f"Aprovador da Entrada: {person['Aprovador']}")
                    else:
                        st.warning(status)
                except Exception as e:
                    st.error(f"Erro ao verificar registro: {e}")
            else:
                st.warning("Por favor, insira o nome.")
    
    # Consulta Geral de Pessoas Liberadas e Bloqueadas
    with st.expander("Consulta Geral de Pessoas Liberadas e Bloqueadas", expanded=False):
        status_filter = st.selectbox("Selecione o Status para Consulta:", ["Todos", "Liberada", "Bloqueada"])
        empresa_filter = st.selectbox("Selecione a Empresa para Consulta:", ["Todas"] + list(st.session_state.df_acesso_veiculos["Empresa"].unique()))

        if st.button("Consultar"):
            try:
                if status_filter == "Todos":
                    df_filtered = st.session_state.df_acesso_veiculos
                else:
                    df_filtered = st.session_state.df_acesso_veiculos[st.session_state.df_acesso_veiculos["Status da Entrada"] == status_filter]
                
                if empresa_filter != "Todas":
                    df_filtered = df_filtered[df_filtered["Empresa"] == empresa_filter]
                
                # Remove as colunas de horário e data
                columns_to_display = ["Nome", "Placa", "Marca do Carro", "Empresa", "Status da Entrada", "Motivo do Bloqueio", "Aprovador"]
                
                # Verifica se as colunas existem antes de selecioná-las
                existing_columns_to_display = [col for col in columns_to_display if col in df_filtered.columns]
                df_filtered = df_filtered[existing_columns_to_display]
                
                if not df_filtered.empty:
                    st.write(f"Registros de Pessoas {status_filter}as na empresa {empresa_filter}:")
                    st.dataframe(df_filtered)
                else:
                    st.warning(f"Não há registros encontrados para o status {status_filter} e empresa {empresa_filter}.")
            except Exception as e:
                st.error(f"Erro ao realizar consulta geral: {e}")
         

    # Exibir tabela editável
    try:
        df = st.data_editor(st.session_state.df_acesso_veiculos.fillna(""), num_rows="dynamic")

        #st.dataframe(st.session_state.df_acesso_veiculos.fillna(""))
        st.session_state.df_acesso_veiculos = df
        save_to_excel(st.session_state.df_acesso_veiculos, file_path)
    except Exception as e:
        st.error(f"Erro ao exibir ou salvar a tabela: {e}")

    # Verificar e exibir informações de bloqueio
def blocks():
    blocked_info = check_blocked_records(st.session_state.df_acesso_veiculos)
    
    if blocked_info:
        st.error("Registros Bloqueados:\n" + blocked_info)
    else:
        st.empty()

