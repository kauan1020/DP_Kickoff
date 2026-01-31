# Pasta `plugins/hooks/`

Aqui ficam os **Hooks** customizados do Airflow. Cada Hook representa a **camada de integração**: conexão com fonte externa (API, banco, arquivo remoto), credenciais, autenticação e métodos para **obter dados**. O Hook **não** implementa regras de negócio; apenas “conecta e traz dados”.

---

## O que esta pasta faz?

Ela centraliza todos os **Hooks** do projeto. Cada Hook:

- **Herdar** de `airflow.hooks.base.BaseHook` (padrão do Airflow).
- **Obter credenciais** via Airflow Connection (`self.get_connection(conn_id)`) ou variáveis de ambiente — nunca hardcodar senha ou API key no código.
- **Autenticar** na fonte externa (API, banco, etc.) e fazer as requisições necessárias.
- **Expor métodos** reutilizáveis para obter dados (ex.: `get_endpoint(path)`, `get_all_tables(endpoints)`).

Ou seja: Hook = “como conectar e trazer dados”; não decide onde salvar nem o que fazer com os dados.

---

## Por que ter Hooks isolados?

- **Reuso**: O mesmo Hook pode ser usado por vários Operators ou DAGs (extrair para Landing, fazer backup, sincronizar, etc.) sem repetir código de conexão.
- **Testes**: Você testa a conexão (Hook) separado da lógica de negócio (Operator). No teste do Operator, você usa um Hook “falso” (mock) que devolve dados fixos, sem chamar a API de verdade.
- **Manutenção**: Se a API mudar (URL, autenticação, formato), você altera só o Hook; os Operators continuam iguais.
- **Responsabilidade única**: Hook cuida só de integração; Operator cuida de negócio. Código mais claro e alinhado a boas práticas (ex.: Clean Architecture).

---

## O que você precisa criar

### 1. `hooks/__init__.py`

Arquivo que torna o diretório um pacote Python. Pode ser vazio ou exportar os Hooks (ex.: `from hooks.api_publica_hook import ApiPublicaHook`).

### 2. Hook de API pública (exemplo: `api_publica_hook.py`)

**O que é:** Hook para conectar a uma **API pública externa** (ex.: JSONPlaceholder, OpenWeather, outra API REST). Será usado pelo Operator que grava na Landing.

**O que deve conter:**

- **Classe** que herda de `BaseHook`.
- **Parâmetros no `__init__`:**
  - `conn_id`: ID da Connection no Airflow (ex.: `api_publica_default`) onde estão a URL base da API e, se a API exigir, API key (login/password).
  - (Opcional) timeout, retry, etc.
- **Métodos:**
  - `get_connection()`: obter a Connection do Airflow e extrair host, login (ou API key), etc.
  - `get_endpoint(path)`: fazer request HTTP (GET) para um endpoint e retornar os dados (dict ou list, conforme o JSON).
  - (Opcional) `get_all_tables(endpoints)`: retornar um dict com vários endpoints/tabelas (ex.: `{"users": [...], "posts": [...]}`) para o Operator gravar várias tabelas na Landing.
- **Docstrings:** descrever a classe, os parâmetros e o retorno de cada método (Google ou NumPy style).
- **Tratamento de erros:** tratar erros HTTP (404, 500) e timeout; logar e relançar ou retornar valor controlado.
- **DRY:** encapsular a lógica de request em um método privado (ex.: `_request(method, path)`) reutilizado por `get_endpoint` e outros.

O repositório já inclui um **exemplo** em `api_publica_hook.py`; use como molde e adapte para outra API se quiser.

---

## Boas práticas

- **POO:** uma classe por fonte; métodos com responsabilidade única.
- **Credenciais:** nunca hardcodar; usar Connection ou Variable do Airflow.
- **Docstrings:** classe e todos os métodos públicos (parâmetros, retorno, exceções).
- **DRY:** não repetir lógica de request; um método `_request` e os demais chamando-o.
- **Testes:** cobrir com testes unitários em `plugins/tests/test_api_publica_hook.py` (mock da Connection e da resposta HTTP).

---

## Resumo

| Item | Descrição |
|------|-----------|
| **O que é** | Hooks = integração (credenciais, autenticação, obter dados da fonte). |
| **Por que** | Reuso, testes, manutenção e responsabilidade única. |
| **Arquivos a criar** | `__init__.py` + um arquivo por Hook (ex.: `api_publica_hook.py`). |
| **Base** | Herdar de `airflow.hooks.base.BaseHook`. |
| **Desafio** | Hook de API pública com `get_endpoint` e, se possível, `get_all_tables`. |

Implemente o Hook da API pública (ou de outra fonte) conforme este README e use-o no Operator que grava na Landing.
