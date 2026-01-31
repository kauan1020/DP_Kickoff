# Pasta `dags/`

Aqui ficam as **DAGs** (Directed Acyclic Graphs) do Apache Airflow: são os “fluxos” que orquestram todo o pipeline de dados — extração para Landing, Bronze (upsert), Silver (modelagem) e Gold (OBT e agregados). O Airflow lê esta pasta (montada dentro do container em `/opt/airflow/dags`) e executa as DAGs conforme o agendamento e as dependências que você definir.

---

## O que esta pasta faz?

Ela centraliza **todas as DAGs** do projeto em um único lugar:

- **DAG de extração**: usa o **Operator** (que chama o **Hook** da API), extrai os dados e grava na **Landing**.
- **DAG Bronze**: lê da **Landing**, aplica **upsert** e grava na **Bronze**.
- **DAG Silver**: lê da **Bronze**, aplica **modelagem** (Data Vault, 3NF ou Star Schema) e grava na **Silver**.
- **DAG Gold**: lê da **Silver**, cria **OBT** e **agregações** e grava na **Gold**.

Além disso, há uma **DAG de exemplo** (`pipeline_exemplo.py`) que serve de **molde** para você encadear todas as etapas (Landing → Bronze → Silver → Gold) em um único fluxo.

---

## Por que organizar por camada (bronze, silver, gold)?

- **Clareza**: Quem abre a pasta vê de imediato qual DAG cuida de qual camada (Bronze, Silver, Gold).
- **Manutenção**: Se precisar mudar só a lógica da Bronze, você sabe onde está (`dags/bronze/`).
- **Reuso**: Uma DAG Bronze pode ser disparada pela DAG de pipeline ou por outra DAG; manter cada etapa em um arquivo (ou pasta) facilita reutilizar.
- **Ordem certa**: O fluxo é sempre Landing → Bronze → Silver → Gold; organizar as pastas nessa ordem ajuda a não “pular” etapa.

---

## Estrutura das pastas

```
dags/
├── README.md              (este arquivo)
├── pipeline_exemplo.py     (DAG molde: extração → Bronze → Silver → Gold)
├── bronze/                 → DAGs que leem da Landing e escrevem na Bronze (upsert)
│   └── README.md
├── silver/                 → DAGs que leem da Bronze e escrevem na Silver (modelagem)
│   └── README.md
└── gold/                   → DAGs que leem da Silver e escrevem na Gold (OBT/agregados)
    └── README.md
```

Cada subpasta tem um **README** explicando o **intuito** daquela camada de DAGs, **por que** ela existe e **quais arquivos** criar.

---

## O que é o `pipeline_exemplo.py`?

É uma DAG **vazia** (ou com tasks placeholder) que você vai **preencher** com o pipeline completo:

1. **Task de extração**: chama o Operator que usa o Hook da API e grava na **Landing**.
2. **Task Bronze**: chama a DAG ou a lógica que lê da Landing e faz **Upsert** na **Bronze**.
3. **Task Silver**: chama a DAG ou a lógica que lê da Bronze e aplica **modelagem** na **Silver**.
4. **Task Gold**: chama a DAG ou a lógica que lê da Silver e grava **OBT/agregados** na **Gold**.

Você pode implementar tudo em **uma única DAG** (tasks encadeadas) ou em **DAGs separadas** (uma por camada) e usar `TriggerDagRunOperator` para disparar a próxima. O `pipeline_exemplo.py` serve de **molde** para entender a ordem: Landing → Bronze → Silver → Gold.

---

## Ordem de execução (fluxo)

1. **Extração (Landing)**: DAG ou task que usa o **Operator** (que chama o **Hook** da API) e grava na **Landing**.
2. **Bronze**: DAG em `dags/bronze/` que lê da Landing e faz **Upsert** na Bronze.
3. **Silver**: DAG em `dags/silver/` que lê da Bronze e aplica **modelagem** na Silver.
4. **Gold**: DAG em `dags/gold/` que lê da Silver e grava **OBT/agregados** na Gold.

A DAG `pipeline_exemplo.py` (ou a DAG “master” que você criar) orquestra essas etapas em sequência.

---

## Resumo

| Item | Descrição |
|------|-----------|
| **O que é** | Pasta das DAGs do Airflow (extração, Bronze, Silver, Gold). |
| **Por que** | Centralizar e organizar os fluxos por camada; manter a ordem Landing → Bronze → Silver → Gold. |
| **pipeline_exemplo.py** | DAG molde para você encadear o pipeline completo. |
| **bronze/, silver/, gold/** | Subpastas com DAGs de cada camada; cada uma tem README explicando o que criar. |

Leia o README de cada subpasta (`bronze/`, `silver/`, `gold/`) para implementar as DAGs na ordem certa e com os padrões descritos.
