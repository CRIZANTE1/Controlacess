# Sistema de Controle de Acesso e Briefing

Este sistema gerencia o controle de acesso de visitantes e veículos, incluindo verificação de briefing obrigatório para visitantes que não acessaram o local há mais de um ano.

## Requisitos do Sistema

- Python 3.8 ou superior
- Windows 10/11
- Conexão com internet para acesso ao banco de dados

## Instalação e Uso

1. Instale o Python 3.8 ou superior do site oficial: https://www.python.org/downloads/
   - Durante a instalação, marque a opção "Add Python to PATH"

2. Baixe ou clone este repositório para seu computador

3. Execute o sistema:
   - Dê duplo clique no arquivo `iniciar_sistema.bat`
   - O sistema será iniciado automaticamente no seu navegador padrão
   - Se for a primeira vez, as dependências serão instaladas automaticamente

## Funcionalidades

- Controle de acesso de visitantes
- Controle de acesso de veículos
- Verificação automática de briefing
- Geração de relatórios
- Interface administrativa

## Estrutura de Arquivos

```
.
├── app/
│   ├── data_operations.py    # Operações com banco de dados
│   ├── ui_interface.py       # Interface do usuário
│   ├── excel_operations.py   # Operações com Excel
│   ├── adm_interface.py      # Interface administrativa
│   ├── bcrypt.py            # Funções de criptografia
│   └── login.py             # Sistema de login
├── data/
│   ├── controle_acesso_veiculos.xlsx
│   ├── login_attempts.json
│   ├── users_db.json
│   └── NOVO BRIEFING BAERI 2023.mp4
├── main.py
├── requirements.txt
├── iniciar_sistema.bat
└── README.md
```

## Suporte

Para suporte técnico ou dúvidas, entre em contato com a equipe de TI.

## Notas de Segurança

- Mantenha suas credenciais de acesso em segurança
- Não compartilhe os arquivos do sistema com pessoas não autorizadas
- Faça backup regular dos dados 