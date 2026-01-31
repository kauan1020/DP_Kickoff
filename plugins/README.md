# Pasta `plugins/`

Aqui ficam os **plugins** do Apache Airflow do projeto: **Hooks** e **Operators** customizados. O Airflow carrega esta pasta (montada no container em `/opt/airflow/plugins`) e usa os Hooks e Operators nas DAGs. O desafio é construir esses plugins com **boas práticas**: POO, testes, docstrings e DRY (evitar repetição).

---

## O que esta pasta faz?

Ela concentra **dois tipos** de componentes:

- **Hooks**: camada de **integração**. Responsáveis por **conectar** a fontes externas (API, banco, arquivo remoto), receber credenciais, autenticar e **devolver os dados**. Eles **não** decidem o que fazer com os dados nem onde salvar; só “conectam e trazem”.
- **Operators**: camada de **negócio**. Responsáveis por **usar** o Hook para obter os dados, aplicar a regra de negócio (ex.: quais endpoints chamar, como mapear) e **gravar na Landing** (ou disparar o fluxo que grava). Eles são usados nas DAGs como **tasks**.

Cada “plugin” (ex.: “API pública”) deve ter **um Hook** e **um Operator** associado: o Hook conecta na API; o Operator usa o Hook e grava na Landing.

---

## Por que separar Hook e Operator?

- **Reuso**: O mesmo Hook (ex.: “API pública”) pode ser usado por vários Operators ou DAGs (extrair para Landing, fazer backup, etc.) sem repetir código de conexão.
- **Testes mais fáceis**: Você testa a conexão (Hook) separado da lógica de negócio (Operator). No teste do Operator, você “engana” o código com um Hook falso (mock) que devolve dados fixos, sem chamar a API de verdade.
- **Manutenção**: Se a API mudar (URL, autenticação), você mexe só no Hook; os Operators continuam iguais.
- **Responsabilidade única**: Hook = integração; Operator = negócio. Isso segue boas práticas de arquitetura (ex.: Clean Architecture) e deixa o código mais claro.

---

## Estrutura da pasta

```
plugins/
├── README.md                    (este arquivo)
├── __init__.py                  (torna o diretório um pacote Python)
├── hooks/                       → Hooks (conexões externas)
│   ├── __init__.py
│   ├── README.md                (intuito da pasta hooks e arquivos a criar)
│   └── api_publica_hook.py      (exemplo: Hook de API pública)
├── operators/                   → Operators (lógica que usa Hook e grava na Landing)
│   ├── __init__.py
│   ├── README.md                (intuito da pasta operators e arquivos a criar)
│   └── api_to_landing_operator.py  (exemplo: Operator que usa o Hook e grava na Landing)
└── tests/                       → Testes dos plugins (unitários e, se quiser, integração)
    ├── __init__.py
    ├── README.md                (intuito dos testes)
    ├── test_api_publica_hook.py
    └── test_api_to_landing_operator.py
```

Cada subpasta tem um **README** explicando o **intuito**, **por que** aquele componente existe e **quais arquivos** criar.

---

## O que você precisa criar / usar

### 1. `plugins/__init__.py`

Arquivo que torna o diretório um pacote Python. Pode ser vazio ou importar Hooks e Operators para facilitar o uso nas DAGs (ex.: `from hooks.api_publica_hook import ApiPublicaHook`). O Airflow carrega os plugins a partir desta pasta.

### 2. Pasta `hooks/`

Centraliza todos os **Hooks**. Cada Hook representa uma fonte externa (API, banco, arquivo remoto). Leia `hooks/README.md` para entender o que cada Hook deve fazer, por que isolar a conexão e quais métodos expor (ex.: `get_endpoint`, `get_all_tables`).

### 3. Pasta `operators/`

Centraliza todos os **Operators**. Cada Operator usa um Hook e implementa a regra de negócio (ex.: extrair várias tabelas da API e gravar na Landing). Leia `operators/README.md` para entender o que cada Operator deve fazer e por que usar o Hook em vez de conectar direto na API.

### 4. Pasta `tests/`

Centraliza os **testes** dos Hooks e Operators. Leia `tests/README.md` para entender por que testar, como rodar os testes e como usar mocks (API, Connection, filesystem) para testes unitários.

---

## Desafio: API pública → Landing → Bronze (Upsert)

O **desafio principal** do guia é:

1. **Criar o Hook** de uma **API pública externa** (ex.: JSONPlaceholder, OpenWeather, ou outra que retorne várias “tabelas”/endpoints).
2. **Criar o Operator** que usa esse Hook, traz os dados (de preferência **várias tabelas**) e grava na **Landing**.
3. **Pipeline Bronze:** ler da Landing e fazer **Upsert** na Bronze para manter a última versão do dado (isso é feito nas DAGs em `dags/bronze/`).

Os plugins (Hook + Operator) são a base para as etapas 1 e 2; a etapa 3 é implementada nas DAGs da pasta `dags/bronze/`.

---

## Resumo

| Item | Descrição |
|------|-----------|
| **O que é** | Pasta dos plugins do Airflow: Hooks (integração) e Operators (negócio). |
| **Por que** | Reuso, testes mais fáceis, manutenção e responsabilidade única (Hook vs Operator). |
| **Hook** | Integração: credenciais, autenticação, obter dados da fonte externa. |
| **Operator** | Negócio: usar o Hook e gravar na Landing (ou disparar o fluxo). |
| **Boas práticas** | POO, testes, docstrings, DRY. |
| **Desafio** | Hook de API pública + Operator que grava várias tabelas na Landing; depois Upsert na Bronze. |

Leia o README de cada subpasta (`hooks/`, `operators/`, `tests/`) para implementar os componentes de forma didática e alinhada aos padrões do projeto.
