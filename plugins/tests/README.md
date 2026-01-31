# Pasta `plugins/tests/`

Aqui ficam os **testes** dos plugins (Hooks e Operators) do Airflow. O objetivo é garantir que a **integração** (Hook) e a **lógica de negócio** (Operator) funcionem conforme esperado, usando **testes unitários** com mocks (API, Connection, filesystem) para que os testes sejam rápidos e não dependam de rede ou ambiente real.

---

## O que esta pasta faz?

Ela centraliza os **testes** dos Hooks e Operators:

- **Testes do Hook**: verificar que o Hook obtém a Connection corretamente, que `get_endpoint` (ou equivalente) retorna o esperado quando a API “responde” 200, e que erros (404, 500, timeout) são tratados. Tudo isso **sem chamar a API de verdade** — usando **mock** da Connection e das requisições HTTP.
- **Testes do Operator**: verificar que o Operator instancia o Hook, chama o método esperado (ex.: `get_all_tables`) e grava os arquivos no caminho esperado (ex.: na Landing). Tudo isso **sem chamar a API de verdade** e **sem gravar na pasta real** do datalake — usando **mock** do Hook e **tmp_path** (pasta temporária do pytest) para gravação.

Cada Hook e cada Operator deve ter pelo menos um arquivo de teste correspondente (ex.: `test_api_publica_hook.py`, `test_api_to_landing_operator.py`).

---

## Por que testar?

- **Segurança ao mudar código**: Quando você alterar um Hook ou um Operator, os testes avisam se algo quebrou, sem precisar subir o Airflow e rodar a DAG inteira.
- **Documentação viva**: Os testes mostram **como** o código deve se comportar (ex.: “quando a API retorna 200, o Hook devolve o JSON”; “quando o Hook retorna dados, o Operator grava um arquivo por tabela”).
- **Confiança**: Quem for usar ou dar manutenção no projeto sabe que há testes cobrindo os pontos críticos (conexão, obtenção de dados, gravação na Landing).
- **Boas práticas**: Testar Hooks e Operators é uma prática comum em projetos com Airflow; este guia incentiva esse hábito desde o estudo.

---

## O que você precisa criar

### 1. `tests/__init__.py`

Pode ser vazio; torna o diretório um pacote Python para o pytest descobrir os testes.

### 2. Testes do Hook (ex.: `test_api_publica_hook.py`)

**O que conter:**

- **Fixture ou mock da Connection:** simular `BaseHook.get_connection(conn_id)` retornando um objeto com `host`, `login` (ou API key), etc.
- **Testes:**
  - Que o Hook obtém a Connection corretamente.
  - Que `get_endpoint("/users")` retorna o JSON esperado quando a resposta HTTP é 200 (mock do `requests`).
  - Que, quando a API retorna 404 ou 500, o Hook trata o erro (ex.: log + raise ou retorno controlado).
  - (Opcional) Que `get_all_tables` retorna um dict com as chaves esperadas (ex.: "users", "posts") quando vários endpoints são mockados.
- **Docstrings:** em cada teste, descrever o cenário (ex.: “Quando get_endpoint recebe 200, retorna o JSON da resposta”).

Use **pytest** e **unittest.mock** (ou **pytest-mock**) para mockar `requests` e `BaseHook.get_connection`.

### 3. Testes do Operator (ex.: `test_api_to_landing_operator.py`)

**O que conter:**

- **Mock do Hook:** simular `ApiPublicaHook` para que `get_all_tables` (ou `get_endpoint`) retornem dados fixos (ex.: `[{"id": 1, "name": "Test"}]`) sem chamar a API real.
- **Gravação em pasta temporária:** usar **tmp_path** do pytest para que o Operator grave em uma pasta temporária, sem escrever na pasta real do datalake.
- **Testes:**
  - Que `execute()` instancia o Hook e chama o método esperado (ex.: `get_all_tables`).
  - Que, quando o Hook retorna dados, o Operator grava arquivos no caminho esperado (ex.: em `tmp_path`) com o conteúdo esperado (ex.: JSON).
  - Que o retorno de `execute()` contém informações úteis (ex.: contagem de tabelas/registros).
- **Docstrings:** descrever o cenário de cada teste.

Use **pytest** e **tmp_path** para diretório temporário; mock do Hook para isolar a lógica do Operator.

---

## Como rodar os testes

Na **raiz do projeto**, com a pasta `plugins` no `PYTHONPATH` (o Airflow usa a pasta plugins no path; o `conftest.py` desta pasta adiciona o path necessário):

```bash
# Instale as dependências de desenvolvimento primeiro
pip install -r requirements-dev.txt

# Execute todos os testes dos plugins
PYTHONPATH=plugins pytest plugins/tests/ -v
```

Para rodar só um arquivo:

```bash
PYTHONPATH=plugins pytest plugins/tests/test_api_publica_hook.py -v
```

Garanta que as dependências (airflow, pytest, requests, etc.) estejam instaladas no ambiente (venv ou onde você roda os testes).

---

## Boas práticas

- **Mock de I/O:** não chamar API real nem escrever em disco real nos testes unitários; usar mocks e `tmp_path`.
- **Um assert claro por teste** (ou poucos relacionados): facilita entender falhas.
- **Nomes descritivos:** ex. `test_get_endpoint_returns_json_when_status_200`.
- **DRY:** fixtures para Connection e para resposta mock da API; reutilizar nos testes.

---

## Resumo

| Item | Descrição |
|------|-----------|
| **O que é** | Testes unitários (e opcionalmente integração) dos Hooks e Operators. |
| **Por que** | Segurança ao mudar código, documentação viva e confiança. |
| **Arquivos a criar** | `__init__.py` + `test_<hook>.py` + `test_<operator>.py`. |
| **Ferramentas** | pytest, mock (requests, Connection, filesystem), tmp_path. |
| **Cobertura** | Hook: conexão, get_endpoint, tratamento de erro. Operator: chamada ao Hook, gravação na Landing, retorno. |

Implemente os testes conforme este README para garantir que os plugins funcionem antes de usar nas DAGs.
