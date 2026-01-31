# Pasta `dags/silver/`

Aqui ficam as **DAGs do Airflow** que implementam a camada **Silver** do datalake: elas leem os dados da **Bronze** (última versão por entidade) e gravam na **Silver** aplicando **modelagem de dados** (Data Vault, 3NF e/ou Star Schema).

---

## O que esta pasta faz?

Cada DAG (ou conjunto de tasks) nesta pasta deve:

1. **Ler** as tabelas da **Bronze** (Parquet, uma por entidade).
2. **Aplicar pelo menos um** tipo de modelagem (obrigatório neste guia; idealmente mais de um para estudo):
   - **Data Vault 2.0**: Hubs, Links, Satellites.
   - **3NF**: tabelas normalizadas.
   - **Star Schema**: dimensões (dim_*) e fato(s) (fact_*).
3. **Gravar** o resultado na pasta **Silver** (em subpastas por modelo, se fizer sentido: ex. `datavault/`, `normalized_3nf/`, `star_schema/`).

A Silver é a **fonte** da camada Gold; portanto, a saída aqui deve estar modelada e pronta para agregações e OBT.

---

## Por que ter DAGs dedicadas à Silver?

- **Responsabilidade única**: Uma DAG (ou uma por tipo de modelo) cuida só de “Bronze → Silver”; não mistura extração nem Gold.
- **Reprocessamento**: Você pode rodar só a DAG Silver de novo (ex.: após mudar a modelagem) sem rodar Bronze ou Gold.
- **Estudo**: Ter DAGs separadas para Data Vault, 3NF e Star Schema ajuda a comparar os modelos e entender quando usar cada um.

---

## O que você precisa criar

### 1. DAG(s) Silver

**Nomes sugeridos:**

- `bronze_to_silver_datavault.py` — modelagem Data Vault.
- `bronze_to_silver_3nf.py` — modelagem 3NF.
- `bronze_to_silver_star_schema.py` — modelagem Star Schema.

Ou **uma única DAG** com várias tasks (uma por tipo de modelagem).

**O que cada DAG/task deve fazer:**

- **Entrada:** caminho da pasta **Bronze** (ex.: `datalake/bronze/` ou `/opt/airflow/datalake/bronze/` no container).
- **Processamento:**
  - Ler as tabelas Bronze (Spark preferencial, ou Pandas como alternativa mais simples de configurar).
  - Aplicar as regras do modelo escolhido:
    - **Data Vault:** criar Hubs (business keys), Links (relacionamentos), Satellites (atributos + histórico).
    - **3NF:** normalizar em tabelas sem redundância; chaves primárias e estrangeiras.
    - **Star Schema:** criar dimensões (dim_*) e fato(s) (fact_*) com chaves para join.
  - Gravar na pasta **Silver** (ex.: `datalake/silver/star_schema/dim_usuario/`, `datalake/silver/star_schema/fact_vendas/`).
- **Saída:** tabelas Parquet na Silver, organizadas por modelo (datavault/, normalized_3nf/, star_schema/).

### 2. Scripts auxiliares (opcional)

- Scripts Spark ou Python que implementam a lógica de cada modelagem (ex.: `scripts/build_star_schema.py`).
- Ou Operators customizados em `plugins/` que encapsulam essa lógica.

---

## Detalhes didáticos

### Data Vault

- **Hub:** uma tabela por entidade de negócio; contém apenas a business key (ex.: `user_id`).
- **Link:** tabela que relaciona dois ou mais Hubs (ex.: Link Pedido-Item).
- **Satellite:** tabela de atributos e histórico; pertence a um Hub ou Link; contém carga de dados e data de carga.

### 3NF (Terceira Forma Normal)

- Tabelas normalizadas: cada atributo não-chave depende apenas da chave primária; sem dependências transitivas.
- Uma tabela por entidade ou relacionamento; chaves estrangeiras para relacionamentos.

### Star Schema

- **Dimensões:** tabelas descritivas (dim_cliente, dim_produto, dim_data) com atributos para filtro e agrupamento.
- **Fato:** tabela de métricas (fact_vendas) com chaves para as dimensões e medidas (valor, quantidade, etc.).

---

## Resumo

| Item | Descrição |
|------|-----------|
| **O que é** | DAGs que leem da Bronze e escrevem na Silver com modelagem. |
| **Por que** | Responsabilidade única, reprocessamento e estudo dos modelos. |
| **Entrada** | Pasta Bronze (tabelas Parquet por entidade). |
| **Saída** | Pasta Silver (subpastas por modelo: datavault/, 3nf/, star_schema/). |
| **Arquivos a criar** | Uma ou mais DAGs (ex.: `bronze_to_silver_star_schema.py`) e, se quiser, scripts com Spark (preferencial) ou Pandas. |

Implemente a(s) DAG(s) nesta pasta para que os dados da Bronze sejam modelados na Silver antes de seguir para a Gold.
