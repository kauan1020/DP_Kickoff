# Guia de Estudos: Plataforma de Dados para Engenheiro de Dados

Um repositório **didático** para quem quer aprender a montar uma **plataforma de dados** do zero, usando ferramentas **gratuitas e open source**. Aqui você vai simular um **datalake** local, com dados passando por quatro camadas: **Landing → Bronze → Silver → Gold**, tudo orquestrado pelo **Airflow**. O processamento das camadas (Bronze, Silver, Gold) pode ser feito com **Spark** (preferencial) ou com **Pandas** — Spark é mais comum em produção, mas configurar Spark com Airflow local pode ser mais trabalhoso; Pandas é uma alternativa válida e mais simples para começar.

Se você é iniciante ou vem de outras áreas e quer entender na prática como engenheiros de dados organizam pipelines, este guia foi feito para você. Cada seção explica o **porquê** das escolhas e traz um **passo a passo** para você seguir na ordem certa.

---

## Índice

1. [O que é este projeto?](#o-que-é-este-projeto)
2. [Por que este guia?](#por-que-este-guia)
3. [O que você vai aprender](#o-que-você-vai-aprender)
4. [Arquitetura em palavras simples](#arquitetura-em-palavras-simples)
5. [Por que Hooks isolados? Por que Operator usa Hook?](#por-que-hooks-isolados-por-que-operator-usa-hook)
6. [Por que testar? Por que usar POO?](#por-que-testar-por-que-usar-poo)
7. [Passo a passo: como começar (ambiente)](#passo-a-passo-como-começar-ambiente)
8. [Passo a passo: ordem certa para criar os pipelines](#passo-a-passo-ordem-certa-para-criar-os-pipelines)
9. [Estrutura do repositório](#estrutura-do-repositório)
10. [Checklist e próximos passos](#checklist-e-próximos-passos)

---

## O que é este projeto?

Imagine um **fluxo de dados** que começa em uma **fonte externa** (por exemplo, uma API na internet) e termina em **tabelas prontas para análise** (relatórios, dashboards). No meio do caminho, os dados passam por **quatro etapas** em pastas diferentes:

| Etapa   | Nome    | Em uma frase |
|--------|---------|----------------|
| 1ª     | **Landing** | Dados **como chegam** (brutos, sem mudança). |
| 2ª     | **Bronze**  | Dados **organizados e com última versão** (upsert). |
| 3ª     | **Silver**  | Dados **modelados** (Data Vault, 3NF ou Star Schema). |
| 4ª     | **Gold**    | Tabelas de **análise e agregações** (modelo OBT). |

Quem **coordena** esse fluxo é o **Airflow**, que neste projeto **roda obrigatoriamente em Docker** (veja a seção de ambiente). Quem **processa** os dados (leitura, transformação, escrita nas camadas Bronze, Silver e Gold) pode ser **Spark** (preferencial) ou **Pandas** — você escolhe conforme a complexidade que quiser enfrentar. Tudo isso você vai montar passo a passo, seguindo a ordem deste README.

---

## Por que este guia?

- **Didático**: Explica o **porquê** de cada camada e de cada padrão (Hook, Operator, testes, POO).
- **Prático**: Você **implementa** os pipelines na ordem certa, com READMEs em cada pasta dizendo exatamente o que criar.
- **Open source**: Só ferramentas gratuitas (Airflow, Spark, Python). Nada de serviço pago obrigatório.
- **Local primeiro**: Datalake em pastas no seu PC (ou, se quiser avançar, MinIO no Docker).
- **Boas práticas**: Hooks isolados, Operators usando Hooks, testes, POO e documentação (docstrings), para você treinar o que se usa no mercado.

---

## O que você vai aprender

- **Datalake em camadas**: O que é Landing, Bronze, Silver e Gold e por que separar assim.
- **Airflow**: O que são DAGs, Hooks e Operators; como orquestrar pipelines.
- **Processamento (Spark ou Pandas)**: Spark é preferível para ETL (Bronze, Silver, Gold), mas configurar Spark com Airflow (especialmente em Docker) pode ser mais difícil; Pandas é uma alternativa válida e mais simples para começar.
- **Padrões de arquitetura**: Por que separar “conexão com API” (Hook) da “regra de negócio” (Operator).
- **Boas práticas**: Por que testar, por que usar POO, como manter código limpo (DRY, docstrings).
- **Fluxo completo**: Da API até tabelas de análise (OBT), passando por upsert na Bronze e modelagem na Silver.

---

## Arquitetura em palavras simples

```
   FONTES EXTERNAS (API, arquivos…)
            │
            ▼
   ┌─────────────────────────────────────────┐
   │  AIRFLOW (DAGs)                          │
   │  • Operator usa Hook → extrai → Landing  │
   │  • DAG Bronze  → Landing → Bronze       │
   │  • DAG Silver → Bronze  → Silver        │
   │  • DAG Gold   → Silver  → Gold          │
   └─────────────────────────────────────────┘
            │
            ▼
   ┌─────────────────────────────────────────┐
   │  DATALAKE (pastas no PC ou MinIO)        │
   │                                          │
   │  LANDING → BRONZE → SILVER → GOLD        │
   │  (raw)    (última   (modelagem) (análise)│
   │            versão)                      │
   └─────────────────────────────────────────┘
```

- **Landing**: Onde os dados **chegam** da API ou de arquivos. Formato bruto (JSON, CSV, etc.). Ninguém “mexe” no dado aqui; só guardamos.
- **Bronze**: Onde garantimos **uma linha por chave** (ex.: um usuário por ID), com a **última versão** (upsert). Formato estruturado (ex.: Parquet).
- **Silver**: Onde aplicamos **modelagem de dados** (Data Vault, 3NF ou Star Schema). Dados prontos para ser consumidos de forma organizada.
- **Gold**: Onde criamos **tabelas de análise** e agregações (somas, contagens, por período, etc.), de preferência no modelo **OBT** (One Big Table), para relatórios e dashboards.

Cada pasta do repositório tem um README explicando o intuito daquela camada e quais arquivos criar.

---

## Por que Hooks isolados? Por que Operator usa Hook?

### O que é um Hook?

Um **Hook** é o pedaço de código que **só se preocupa em conectar** a uma fonte externa: receber credenciais (senha, API key), autenticar, fazer a requisição (ex.: chamar uma API) e **devolver os dados**. Ele **não** decide o que fazer com os dados nem onde salvar; isso é responsabilidade de outro componente.

### O que é um Operator?

Um **Operator** é o pedaço de código que **orquestra a regra de negócio**: “buscar os dados da API, separar por tabela e gravar na pasta Landing”. Para buscar os dados, ele **usa** o Hook. Ou seja: o Operator **não** fala com a API diretamente; ele **chama** o Hook e depois decide como e onde gravar (por exemplo, na Landing).

### Por que deixar o Hook isolado?

1. **Reuso**: O mesmo Hook (ex.: “API pública”) pode ser usado por vários Operators ou DAGs (extrair para Landing, fazer um backup, etc.) sem repetir código de conexão.
2. **Testes mais fáceis**: Você testa a conexão (Hook) separado da lógica de negócio (Operator). No teste do Operator, você “engana” o código com um Hook falso (mock) que devolve dados fixos, sem chamar a API de verdade.
3. **Manutenção**: Se a API mudar (URL, autenticação), você mexe só no Hook; os Operators continuam iguais.
4. **Responsabilidade única**: Hook = integração; Operator = negócio. Assim o código fica mais claro e alinhado com boas práticas de arquitetura (por exemplo, Clean Architecture).

### Resumo

- **Hook** = “como conectar e trazer dados” (integração).
- **Operator** = “o que fazer com os dados” (negócio); ele **usa** o Hook e grava na Landing (ou dispara o próximo passo).

---

## Por que testar? Por que usar POO?

### Por que testar?

- **Segurança ao mudar código**: Quando você alterar um Hook ou um Operator, os testes avisam se algo quebrou, sem precisar subir o Airflow e rodar a DAG inteira.
- **Documentação viva**: Os testes mostram **como** o código deve se comportar (ex.: “quando a API retorna 200, o Hook devolve o JSON”).
- **Confiança**: Quem for usar ou dar manutenção no projeto sabe que há testes cobrindo os pontos críticos.

Não é obrigatório testar tudo no início, mas criar pelo menos alguns testes para o Hook e para o Operator que grava na Landing já é um ótimo hábito e faz parte do desafio deste guia.

### Por que usar POO (Programação Orientada a Objetos)?

- **Organização**: Hook e Operator são **classes** com métodos bem definidos (`get_endpoint`, `execute`, etc.), o que deixa o papel de cada um claro.
- **Reuso e extensão**: Novos Hooks (outra API, outro banco) seguem o mesmo padrão (herdam de `BaseHook`); novos Operators herdam de `BaseOperator`.
- **Encapsulamento**: Credenciais e detalhes de conexão ficam dentro do Hook; o Operator só chama métodos e não precisa saber *como* a conexão funciona.
- **Alinhado ao Airflow**: O Airflow já é pensado em Hooks e Operators como classes; usar POO deixa seu código natural dentro do ecossistema.

POO, testes, docstrings e evitar repetição (DRY) são boas práticas que você vai exercitar neste projeto.

---

## Passo a passo: como começar (ambiente)

Siga na ordem. Se algo der erro, confira se a versão do Python é compatível (recomendado: 3.10 ou 3.11).

### 1. Pré-requisitos

- **Python** instalado (3.10 ou 3.11). No terminal: `python3 --version`.
- **Git** (para clonar o repositório, se ainda não tiver).
- **Docker e Docker Compose** (obrigatórios para o Airflow): o Airflow **sempre** roda em containers neste guia. Assim o ambiente fica igual para todos e próximo do que se usa em produção.

### 2. Clonar ou baixar o repositório

Se usar Git:

```bash
git clone <url-do-repositorio>
cd data_platform_kickoff
```

Se baixou em ZIP, extraia e entre na pasta do projeto no terminal.

### 3. Criar o ambiente virtual (venv)

O ambiente virtual evita misturar as dependências deste projeto com outros projetos no seu PC.

No terminal, na **pasta raiz do projeto**:

```bash
python3 -m venv venv
```

Isso cria uma pasta `venv` com um Python “isolado” para este projeto.

### 4. Ativar o ambiente virtual

- **Linux / macOS**:
  ```bash
  source venv/bin/activate
  ```
- **Windows (PowerShell)**:
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **Windows (CMD)**:
  ```cmd
  .\venv\Scripts\activate.bat
  ```

Quando ativado, o início da linha do terminal costuma mostrar `(venv)`.

### 5. Instalar as dependências

Ainda com o venv ativado, na raiz do projeto:

```bash
pip install -r requirements.txt
```

Para quem for escrever e rodar testes:

```bash
pip install -r requirements-dev.txt
```

### 6. Processamento: Spark (preferencial) ou Pandas

As DAGs Bronze, Silver e Gold precisam **processar dados** (ler da camada anterior, transformar, gravar na próxima). Você pode usar **Spark** ou **Pandas**:

- **Spark (preferencial)**  
  É o mais usado em plataformas de dados reais e escala melhor para volume maior. Porém, **configurar Spark com Airflow local** (principalmente com Airflow rodando em Docker) pode ser **mais trabalhoso**: é preciso instalar PySpark na imagem do Airflow (Dockerfile customizado), garantir memória e variáveis de ambiente (ex.: `SPARK_MASTER=local[*]`), e às vezes ajustar permissões e paths dentro do container. Se quiser usar Spark:
  1. Inclua `pyspark` no **Dockerfile** da imagem do Airflow (ou instale no ambiente onde o Airflow roda).
  2. Nas tasks que processam Bronze/Silver/Gold, crie o `SparkSession` com `master("local[*]")` e use `spark` para ler e escrever (Parquet, etc.). O README da pasta `dags/bronze/` (e os de `silver/` e `gold/`) comentam como fazer isso.

- **Pandas (alternativa mais simples)**  
  Para **começar rápido** ou focar primeiro na **lógica do pipeline** (upsert, modelagem, OBT) sem se preocupar com a configuração do Spark, use **Pandas**: `PythonOperator` chamando um script que lê JSON/CSV/Parquet com `pandas`, faz as transformações e grava com `to_parquet` (ou CSV). Não exige configuração extra no Docker e funciona bem para volumes menores ou estudos. O README de cada pasta de DAGs (`dags/bronze/`, `dags/silver/`, `dags/gold/`) explica que o processamento pode ser feito com Spark ou Pandas.

**Resumo:** Spark é preferível em termos de stack “típica” de engenharia de dados; Pandas é uma opção válida e mais fácil de configurar quando o foco é aprender o fluxo Landing → Bronze → Silver → Gold sem complicar o ambiente.

### 7. Subir o Airflow com Docker (obrigatório)

Neste projeto o **Airflow roda obrigatoriamente em Docker**. Não usamos instalação local do Airflow no venv; tudo fica dentro dos containers para manter o ambiente reproduzível e parecido com produção.

1. Entre na pasta `docker/`.
2. Leia o `docker/README.md` (explica o que cada serviço faz e por que).
3. Copie `docker-compose.yml.example` para `docker-compose.yml` e preencha conforme o README (Airflow + Postgres; MinIO é opcional).
4. Na pasta `docker/`, rode: `docker-compose up -d` (ou `docker compose up -d`).
5. Acesse o Airflow no navegador (em geral `http://localhost:8080`). Login padrão costuma ser `admin` / `admin` (confira no README do docker).

O **MinIO** (storage tipo S3) é **opcional**: use se quiser um datalake em buckets em vez de pastas locais. O README da pasta `docker/` explica como ativá-lo.

---

## Passo a passo: ordem certa para criar os pipelines

Seguir esta ordem mantém a **arquitetura** correta: cada camada só consome a anterior e ninguém “pula” etapa.

### Fase 1: Infraestrutura e integração

1. **Estrutura do datalake**  
   Garantir que existam as pastas `datalake/landing`, `datalake/bronze`, `datalake/silver`, `datalake/gold` (já vêm com `.gitkeep` e READMEs). Leia `datalake/README.md`.

2. **Hook da API**  
   Implementar (ou usar o exemplo) o **Hook** que conecta na API pública: credenciais, autenticação, método que devolve dados (ex.: `get_endpoint`, `get_all_tables`). Pasta `plugins/hooks/`, README em `plugins/hooks/README.md`.

3. **Operator que grava na Landing**  
   Implementar (ou usar o exemplo) o **Operator** que **usa o Hook**, busca os dados (várias “tabelas”/endpoints) e **grava na pasta Landing**. Pasta `plugins/operators/`, README em `plugins/operators/README.md`.

4. **DAG de extração**  
   Criar uma DAG no Airflow que usa esse Operator para extrair da API e gravar na **Landing**. Pode ser a DAG `pipeline_exemplo` na pasta `dags/` ou uma DAG específica em `dags/`.

5. **Testes**  
   Escrever testes para o Hook e para o Operator (mock da API e da gravação). Pasta `plugins/tests/`, README em `plugins/tests/README.md`. Rodar: `PYTHONPATH=plugins pytest plugins/tests/ -v`.

### Fase 2: Bronze (última versão dos dados)

6. **DAG Bronze**  
   DAG que lê os arquivos da **Landing**, aplica **upsert** (uma linha por chave, última versão) e grava na **Bronze** (ex.: Parquet). Pasta `dags/bronze/`, README em `dags/bronze/README.md`. Processamento com **Spark** (preferencial) ou **Pandas** (mais simples de configurar).

### Fase 3: Silver (modelagem)

7. **DAG Silver**  
   DAG que lê da **Bronze**, aplica **pelo menos um** tipo de modelagem (Data Vault, 3NF ou Star Schema) e grava na **Silver**. Pasta `dags/silver/`, README em `dags/silver/README.md`. Processamento com **Spark** (preferencial) ou **Pandas**.

### Fase 4: Gold (análise)

8. **DAG Gold**  
   DAG que lê da **Silver**, cria **tabelas de análise** e agregações (de preferência modelo **OBT**) e grava na **Gold**. Pasta `dags/gold/`, README em `dags/gold/README.md`.

---

## Estrutura do repositório

| Pasta        | O que é |
|-------------|---------|
| `datalake/` | Raiz do datalake: subpastas `landing/`, `bronze/`, `silver/`, `gold/`. Cada uma tem README e pode usar MinIO no lugar de pastas locais. |
| `docker/`   | Arquivos de referência para subir Airflow e (opcional) MinIO com Docker Compose. |
| `dags/`     | DAGs do Airflow: subpastas `bronze/`, `silver/`, `gold/` e a DAG de exemplo `pipeline_exemplo.py`. |
| `plugins/`  | Hooks (conexões) e Operators (regras de negócio que usam os Hooks); inclui exemplo de Hook de API e Operator que grava na Landing, além de testes. |

Cada pasta tem um **README** explicando o intuito e quais arquivos criar, de forma didática.

---

## Checklist e próximos passos

Use como lista de progresso:

- [ ] Ambiente: criar venv, ativar, instalar dependências (`requirements.txt` e, se for testar, `requirements-dev.txt`).
- [ ] Spark local: instalar `pyspark` e configurar `SparkSession` com `master("local[*]")` nas DAGs que forem usar Spark.
- [ ] Docker: ler `docker/README.md`, montar `docker-compose.yml` e subir o Airflow (obrigatório). MinIO é opcional.
- [ ] Datalake: conferir pastas `landing`, `bronze`, `silver`, `gold` e ler `datalake/README.md`.
- [ ] Hook da API: implementar ou usar o exemplo em `plugins/hooks/`.
- [ ] Operator API → Landing: implementar ou usar o exemplo em `plugins/operators/`.
- [ ] DAG de extração: DAG que usa o Operator e grava na Landing.
- [ ] Testes: rodar e, se quiser, ampliar testes em `plugins/tests/`.
- [ ] DAG Bronze: Landing → Upsert → Bronze (Spark ou Pandas).
- [ ] DAG Silver: Bronze → modelagem (Data Vault, 3NF ou Star Schema) → Silver.
- [ ] DAG Gold: Silver → OBT/agregados → Gold.
- [ ] Pipeline completo: encadear extração → Bronze → Silver → Gold em uma DAG (ex.: `pipeline_exemplo`).

Para detalhes do que fazer em cada pasta, abra o README da pasta (por exemplo `dags/bronze/README.md`, `plugins/README.md`).

Bons estudos.
