# Pasta `dags/bronze/`

Aqui ficam as **DAGs do Airflow** que implementam a camada **Bronze** do datalake: elas leem os dados da **Landing** (arquivos brutos) e gravam na **Bronze** aplicando **upsert** (uma linha por chave, última versão), em formato estruturado (ex.: Parquet).

---

## O que esta pasta faz?

Cada DAG (ou conjunto de tasks) nesta pasta deve:

1. **Ler** os arquivos da pasta **Landing** (JSON, CSV, etc.) — um ou mais arquivos por entidade (usuários, pedidos, etc.).
2. **Aplicar upsert**: para cada entidade, definir uma **chave** (ex.: `id`, `user_id`) e garantir que na Bronze exista **apenas uma linha por chave** com o dado **mais recente**.
3. **Gravar** o resultado na pasta **Bronze** em formato estruturado (ex.: Parquet ou Delta), uma “tabela” por entidade.

A Bronze é a **fonte** da camada Silver; portanto, a saída aqui deve ser uma tabela por entidade com a **última versão** do dado.

---

## Por que ter DAGs dedicadas à Bronze?

- **Responsabilidade única**: Uma DAG (ou uma por entidade) cuida só de “Landing → Bronze”; não mistura extração da API nem modelagem Silver.
- **Reprocessamento**: Você pode rodar só a DAG Bronze de novo (ex.: para reprocessar um dia) sem rodar extração ou Silver.
- **Clareza**: Quem olha o Airflow vê claramente qual fluxo popula a Bronze e em que ordem ele roda (depois da extração, antes da Silver).

---

## O que você precisa criar

### 1. DAG(s) Bronze

**Nome sugerido:** `landing_to_bronze.py` ou uma DAG por entidade (ex.: `landing_to_bronze_usuarios.py`, `landing_to_bronze_pedidos.py`).

**O que a DAG deve fazer:**

- **Entrada:** caminho da pasta **Landing** (ex.: `datalake/landing/api_xyz/usuarios/` ou variável do Airflow; dentro do container use o caminho montado, ex.: `/opt/airflow/datalake/landing/...`).
- **Processamento:**
  - Ler os arquivos da Landing (Spark, Pandas ou biblioteca de arquivos).
  - Definir a **chave** de upsert por entidade (ex.: `id` para usuários).
  - Fazer **merge**: inserir registros novos e atualizar existentes (mesma chave) com os valores mais recentes.
- **Saída:** gravar na pasta **Bronze** (ex.: `datalake/bronze/usuarios/`) em Parquet (ou Delta).

**Sugestão de tasks:**

- Task 1: listar arquivos novos na Landing (ou usar sensor).
- Task 2: executar o job de upsert (SparkSubmitOperator, PythonOperator chamando script, ou Operator customizado).
- (Opcional) Task 3: notificar ou registrar metadados.

### 2. Scripts auxiliares (opcional)

Se você usar **Spark** ou **Pandas** em um script separado (chamado por PythonOperator ou SparkSubmitOperator), pode criar, por exemplo:

- `scripts/landing_to_bronze_usuarios.py` — script que lê Landing e grava Bronze para a entidade `usuarios`.
- Ou um script genérico que recebe entidade e chave por argumento.

Não é obrigatório ter scripts em pasta separada; você pode colocar a lógica dentro de um **Operator** customizado em `plugins/`.

---

## Detalhes didáticos

### O que é Upsert?

- **Insert**: inserir registros que ainda **não existem** (chave nova).
- **Update**: atualizar registros que **já existem** (mesma chave) com os valores mais recentes.
- **Upsert** = Insert + Update em um passo: na Bronze, cada chave aparece **uma vez**, com o dado mais atual.

### Onde rodar o processamento?

- **Spark (preferencial):** use `SparkSubmitOperator` ou um Operator customizado que chama PySpark. Ideal para volume maior e é a stack mais comum em plataformas de dados. Porém, **configurar Spark com Airflow** (especialmente com Airflow em Docker) pode ser **mais difícil**: é preciso incluir PySpark na imagem do Airflow (Dockerfile), configurar memória e variáveis (ex.: `SPARK_MASTER=local[*]`). Se quiser usar Spark, o README da raiz do projeto comenta o passo a passo.
- **Pandas (alternativa mais simples):** use `PythonOperator` com script que lê CSV/JSON com `pandas`, faz o upsert e grava Parquet com `to_parquet`. Não exige configuração extra no Docker e é uma **opção válida** para começar ou para volume menor. Muitas pessoas fazem o ETL por Pandas primeiro e migram para Spark depois.
- **Delta/Spark:** se usar Delta Lake, pode fazer `MERGE` nativo (continua sendo Spark).

### Caminhos

Ajuste os caminhos conforme o ambiente: pasta local montada no container (ex.: `/opt/airflow/datalake/bronze/`) ou bucket MinIO (ex.: `s3://bronze/`) usando variáveis do Airflow (ex.: `Variable.get("datalake_path")`).

---

## Resumo

| Item | Descrição |
|------|-----------|
| **O que é** | DAGs que leem da Landing e escrevem na Bronze com upsert. |
| **Por que** | Responsabilidade única, reprocessamento e clareza no fluxo. |
| **Entrada** | Pasta Landing (arquivos brutos por entidade). |
| **Saída** | Pasta Bronze (Parquet ou Delta, uma tabela por entidade). |
| **Arquivos a criar** | Pelo menos uma DAG (ex.: `landing_to_bronze.py`) e, se quiser, scripts de Spark (preferencial) ou Pandas (mais simples de configurar). |

Implemente a(s) DAG(s) nesta pasta para que os dados da Landing sejam consolidados na Bronze com upsert antes de seguir para a Silver.
