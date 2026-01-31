# Pasta `plugins/operators/`

Aqui ficam os **Operators** customizados do Airflow. Cada Operator representa a **camada de negócio**: usa o **Hook** para obter os dados e aplica a regra de negócio (ex.: quais endpoints chamar, como mapear, onde gravar). O Operator é usado nas **DAGs** como **task** (ex.: “extrair da API e gravar na Landing”).

---

## O que esta pasta faz?

Ela centraliza todos os **Operators** do projeto. Cada Operator:

- **Herdar** de `airflow.models.baseoperator.BaseOperator` (padrão do Airflow).
- No método **`execute(context)`**: instanciar o **Hook**, chamar os métodos do Hook para obter os dados e **gravar na Landing** (ou disparar o fluxo que grava).
- **Receber parâmetros** via construtor (ex.: `conn_id`, `landing_path`, `tables_endpoints`); incluir em `template_fields` os que precisarem de template do Airflow (ex.: `{{ ds }}`).

Ou seja: Operator = “o que fazer com os dados”; ele **usa** o Hook e **não** implementa conexão HTTP ou banco diretamente.

---

## Por que o Operator usa o Hook (e não conecta direto na API)?

- **Separação de responsabilidades**: Conexão (credenciais, autenticação, request) fica no Hook; regra de negócio (quais tabelas extrair, onde gravar, em que formato) fica no Operator.
- **Reuso**: O mesmo Hook pode ser usado por outro Operator (ex.: “backup da API”) sem repetir código de conexão.
- **Testes**: No teste do Operator você “engana” o código com um Hook mock que devolve dados fixos; não precisa chamar a API de verdade.
- **Manutenção**: Se a API mudar, você altera só o Hook; o Operator continua igual.

---

## O que você precisa criar

### 1. `operators/__init__.py`

Arquivo que torna o diretório um pacote Python. Pode ser vazio ou exportar os Operators (ex.: `from operators.api_to_landing_operator import ApiToLandingOperator`).

### 2. Operator API → Landing (exemplo: `api_to_landing_operator.py`)

**O que é:** Operator que usa o **Hook da API pública**, obtém os dados (de preferência **várias tabelas**/endpoints) e **grava na Landing**.

**O que deve conter:**

- **Classe** que herda de `BaseOperator`.
- **Parâmetros no `__init__` (e em `template_fields` se quiser templating):**
  - `conn_id`: ID da Connection usada pelo Hook (ex.: `api_publica_default`).
  - `landing_path`: caminho base da pasta Landing (ex.: `datalake/landing/api_publica` ou variável do Airflow; dentro do container use o caminho montado).
  - `tables_endpoints`: dict que define quais “tabelas”/endpoints extrair (ex.: `{"users": "/users", "posts": "/posts"}`).
  - (Opcional) `file_format`: "json" ou "csv".
- **Método `execute(context)`:**
  1. Instanciar o Hook (ex.: `ApiPublicaHook(conn_id=self.conn_id)`).
  2. Para cada tabela/endpoint em `tables_endpoints`, chamar o Hook para obter os dados (ex.: `hook.get_all_tables(...)` ou loop com `hook.get_endpoint(path)`).
  3. Gravar cada tabela na Landing (ex.: um arquivo JSON por tabela em `landing_path/tabela/YYYY-MM-DD/dados_TIMESTAMP.json`).
  4. Retornar um resultado útil (ex.: dict com contagem de tabelas e registros) para logs e downstream.
- **Docstrings:** descrever a classe, os parâmetros e o comportamento do `execute`.
- **DRY:** não implementar request HTTP no Operator; usar **apenas** o Hook.

O repositório já inclui um **exemplo** em `api_to_landing_operator.py`; use como molde e adapte para outros casos de uso se quiser.

---

## Boas práticas

- **POO:** uma classe por caso de uso (ex.: um Operator “API → Landing”).
- **Hook:** toda comunicação externa (API, banco) via Hook; o Operator só orquestra e grava.
- **Docstrings:** classe e método `execute` (parâmetros, retorno).
- **Template fields:** incluir `landing_path` (e outros que precisem de template) em `template_fields` para usar variáveis do Airflow (ex.: `{{ ds }}`).
- **Testes:** cobrir com testes unitários em `plugins/tests/test_api_to_landing_operator.py` (mock do Hook e da gravação em disco).

---

## Resumo

| Item | Descrição |
|------|-----------|
| **O que é** | Operators = negócio que usa o Hook e grava na Landing. |
| **Por que usar o Hook** | Separação de responsabilidades, reuso, testes e manutenção. |
| **Arquivos a criar** | `__init__.py` + um arquivo por Operator (ex.: `api_to_landing_operator.py`). |
| **Base** | Herdar de `airflow.models.baseoperator.BaseOperator`. |
| **Desafio** | Operator que usa Hook da API, extrai várias tabelas e grava na Landing. |

Implemente o Operator que usa o Hook da API e grava na Landing conforme este README e use-o na DAG de extração.
