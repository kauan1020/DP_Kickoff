# Pasta `datalake/`

Esta pasta é a **raiz do seu datalake**: é aqui que os dados do projeto ficam armazenados, organizados em **quatro camadas** — Landing, Bronze, Silver e Gold. Tudo que as DAGs do Airflow leem e escrevem (ou que o MinIO representa, se você usar buckets) segue essa estrutura.

---

## O que esta pasta faz?

Ela concentra **todo o armazenamento de dados** do projeto em um único lugar e com uma **ordem clara**:

1. **Landing** — onde os dados **chegam** (brutos, sem transformação).
2. **Bronze** — onde guardamos a **última versão** de cada registro (upsert).
3. **Silver** — onde os dados são **modelados** (Data Vault, 3NF, Star Schema).
4. **Gold** — onde ficam as **tabelas de análise** e agregações (OBT).

Cada subpasta tem um README explicando **o que** é aquela camada, **por que** ela existe e **quais arquivos** os pipelines devem criar.

---

## Por que separar em camadas?

- **Rastreabilidade**: Dá para saber de onde veio cada dado (Landing = fonte; Bronze = última versão; Silver = modelagem; Gold = análise).
- **Reprocessamento**: Se algo der errado na Silver ou na Gold, você não perde o dado bruto; ele está na Landing e na Bronze.
- **Responsabilidade clara**: Cada camada tem um papel. Quem lê da Landing não deve pular direto para a Gold; o fluxo é Landing → Bronze → Silver → Gold.
- **Padrão de mercado**: Essa ideia de “medallion” (Landing / Bronze / Silver / Gold) é usada em muitos projetos de dados; aprender aqui ajuda a falar a mesma língua em outros lugares.

---

## Estrutura das pastas

```
datalake/
├── README.md     (este arquivo)
├── landing/      → dados brutos (API, arquivos) — quem escreve: Operators
├── bronze/       → última versão por chave (upsert) — quem escreve: DAG Bronze
├── silver/       → dados modelados — quem escreve: DAG Silver
└── gold/         → tabelas de análise e OBT — quem escreve: DAG Gold
```

Cada subpasta **já existe** no repositório (com um `.gitkeep` e um README). No início não há arquivos de dados dentro delas; os **pipelines** (DAGs e Operators) é que vão criar os arquivos (JSON, Parquet, etc.) quando você implementá-los.

---

## Onde o Airflow “vê” essa pasta?

O Airflow roda **dentro do Docker**. No `docker-compose.yml` você monta a pasta do projeto dentro do container; por exemplo:

- No seu PC: `datalake/landing/`, `datalake/bronze/`, etc.
- No container: `/opt/airflow/datalake/landing/`, `/opt/airflow/datalake/bronze/`, etc.

Assim, quando uma DAG ou um Operator grava em `datalake/landing/...`, ele usa o caminho **dentro do container** (ex.: `/opt/airflow/datalake/landing/...`). O README da pasta `docker/` explica como configurar esses volumes.

---

## E se eu quiser usar MinIO em vez de pastas?

Se você subir o **MinIO** no Docker, pode criar um bucket para cada camada (landing, bronze, silver, gold). A **lógica** é a mesma: os dados ainda passam por Landing → Bronze → Silver → Gold; só muda o **lugar** onde são guardados (objeto storage tipo S3 em vez de disco local). As DAGs passariam a usar caminhos como `s3://landing/...` (apontando para o endpoint do MinIO) em vez de `/opt/airflow/datalake/landing/...`.

---

## Resumo

| Item | Descrição |
|------|-----------|
| **O que é** | Raiz do datalake: quatro camadas (Landing, Bronze, Silver, Gold). |
| **Por que** | Organizar dados, rastrear origem, permitir reprocessamento e seguir um padrão usado no mercado. |
| **Quem escreve** | Operators na Landing; DAGs Bronze, Silver e Gold nas demais camadas. |
| **Onde o Airflow vê** | Via volume montado no Docker (ex.: `/opt/airflow/datalake/`). |

Leia o README de cada subpasta (`landing/`, `bronze/`, `silver/`, `gold/`) para entender em detalhe o que fazer em cada camada.
