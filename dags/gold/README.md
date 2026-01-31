# Pasta `dags/gold/`

Aqui ficam as **DAGs do Airflow** que implementam a camada **Gold** do datalake: elas leem os dados da **Silver** (já modelados) e gravam na **Gold** com **tabelas de análise** e **agregações**, de preferência no modelo **OBT (One Big Table)**.

---

## O que esta pasta faz?

Cada DAG (ou conjunto de tasks) nesta pasta deve:

1. **Ler** as tabelas da **Silver** (Star Schema, 3NF ou Data Vault — conforme você modelou).
2. **Criar tabelas de análise** agregadas: somas, contagens, médias, por período, por dimensão (ex.: vendas por mês, por produto, por cliente).
3. **Preferencialmente** aplicar o modelo **OBT**: tabelas “wide” com dimensões + métricas em uma única tabela por caso de uso, para facilitar BI e consultas.
4. **Gravar** o resultado na pasta **Gold**.

A Gold é a **última camada** do datalake; sua saída é consumida por relatórios, dashboards e análises.

---

## Por que ter DAGs dedicadas à Gold?

- **Responsabilidade única**: Uma DAG (ou uma por tipo de saída) cuida só de “Silver → Gold”; não mistura modelagem Silver nem extração.
- **Reprocessamento**: Você pode rodar só a DAG Gold de novo (ex.: após mudar uma agregação) sem rodar Silver ou Bronze.
- **Clareza**: Quem consome (BI, analistas) sabe que a Gold é alimentada por DAGs específicas e pode confiar na atualização.

---

## O que você precisa criar

### 1. DAG(s) Gold

**Nomes sugeridos:**

- `silver_to_gold_obt.py` — monta uma ou mais OBTs (ex.: obt_vendas_por_cliente, obt_pedidos_completos).
- `silver_to_gold_agregados.py` — monta tabelas agregadas (vendas por mês, por produto, top clientes, etc.).

Ou **uma única DAG** com várias tasks (OBT + agregados).

**O que cada DAG/task deve fazer:**

- **Entrada:** caminho da pasta **Silver** (ex.: `datalake/silver/star_schema/` ou `/opt/airflow/datalake/silver/star_schema/` no container).
- **Processamento:**
  - Ler dimensões e fatos da Silver (Spark preferencial, ou Pandas como alternativa mais simples de configurar).
  - **OBT:** fazer joins e criar tabelas “wide” (dimensões + métricas em uma tabela por caso de uso).
  - **Agregados:** agrupar por período, por dimensão (ex.: vendas por mês, por produto, por cliente).
  - Gravar na pasta **Gold** (ex.: `datalake/gold/obt_vendas_por_cliente/`, `datalake/gold/agregados/vendas_por_mes/`).
- **Saída:** tabelas Parquet na Gold (OBT e agregados).

### 2. Scripts auxiliares (opcional)

- Scripts Spark (preferencial) ou Pandas que montam as OBTs e agregados (ex.: `scripts/build_obt_vendas.py`).
- Ou Operators customizados em `plugins/` que encapsulam essa lógica.

---

## Detalhes didáticos

### O que é OBT (One Big Table)?

- Uma tabela que contém, na **mesma linha**, **dimensões** (atributos para filtro/agrupamento) e **métricas** (valores numéricos).
- **Objetivo:** reduzir joins na camada de consumo; ferramentas de BI e analistas consultam uma tabela só.
- **Exemplo:** `obt_vendas_mensal` com colunas como `ano`, `mes`, `cliente_id`, `nome_cliente`, `qtd_pedidos`, `valor_total`, `ticket_medio`.

### Agregados

- Tabelas de resumo: vendas por mês, por produto, por região, top N clientes, etc.
- Podem ser consumidas diretamente por dashboards ou servir de base para outras análises.

---

## Resumo

| Item | Descrição |
|------|-----------|
| **O que é** | DAGs que leem da Silver e escrevem na Gold com OBT e agregados. |
| **Por que** | Responsabilidade única, reprocessamento e clareza para quem consome. |
| **Entrada** | Pasta Silver (tabelas modeladas: Star Schema, 3NF ou Data Vault). |
| **Saída** | Pasta Gold (OBT e agregados em Parquet). |
| **Arquivos a criar** | Uma ou mais DAGs (ex.: `silver_to_gold_obt.py`, `silver_to_gold_agregados.py`) e, se quiser, scripts com Spark (preferencial) ou Pandas. |

Implemente a(s) DAG(s) nesta pasta para que os dados da Silver virem tabelas OBT e agregados na Gold.
