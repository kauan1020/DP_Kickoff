# Pasta `datalake/landing/`

A **Landing** é a **primeira camada** do datalake: é aqui que os dados **chegam** das fontes externas (API, arquivos, etc.) **exatamente como vieram**, sem transformação de negócio. Só guardamos o que a fonte nos enviou.

---

## O que esta pasta faz?

Ela é o **ponto de entrada** de todos os dados que entram no datalake:

- Recebe o que os **Operators** gravam depois de chamar os **Hooks** (ex.: dados de uma API).
- Mantém o formato **original** (JSON, CSV, etc.) para que você sempre tenha o dado bruto.
- Serve de **fonte** para a camada **Bronze**, que vai ler daqui, fazer upsert e gravar na Bronze.

Ou seja: nada de negócio é aplicado aqui; é só “despejo” do que veio da fonte.

---

## Por que ter uma camada só para “dados brutos”?

- **Rastreabilidade**: Se algo der errado depois (Bronze, Silver ou Gold), você ainda tem o dado original na Landing para reprocessar.
- **Auditoria**: Dá para saber exatamente o que a API (ou o arquivo) retornou em cada execução.
- **Separação de responsabilidades**: Quem **conecta** e **traga** o dado é o Hook/Operator; quem **transforma** é a Bronze e as camadas seguintes. A Landing não transforma nada.
- **Histórico de extrações**: Se você gravar por data (ex.: uma pasta ou arquivo por dia), consegue ver evolução e reprocessar apenas um período.

---

## Quem escreve aqui?

Apenas os **Operators** do Airflow (na pasta `plugins/operators/`). Eles usam o **Hook** para obter os dados da fonte (ex.: API) e gravam o resultado nesta pasta (ou no bucket `landing` no MinIO).

Nenhum pipeline de **Bronze**, **Silver** ou **Gold** deve **escrever** na Landing; eles só **leem** da camada anterior (Bronze lê da Landing, Silver lê da Bronze, Gold lê da Silver).

---

## Que arquivos devem aparecer aqui?

Os **pipelines** (Operators) é que criam os arquivos. Sugestão de organização:

**Por fonte e tabela/endpoint:**

```
landing/
├── api_nome_da_fonte/
│   ├── usuarios/
│   │   └── 2025-01-30/
│   │       └── dados_20250130_143022.json
│   └── pedidos/
│       └── ...
```

Ou mais simples, só por tabela:

```
landing/
├── usuarios/
│   └── dados_YYYYMMDD_HHMMSS.json
├── pedidos/
│   └── ...
```

**Tipos de arquivo:**

- **JSON**: resposta bruta de APIs (um arquivo por extração ou por partição).
- **CSV**: se a fonte for CSV.
- **(Opcional)** Metadado: arquivo com timestamp, fonte e status (ex.: `_metadata.json`) para auditoria.

O importante: **não altere** o conteúdo dos arquivos; mantenha o mesmo schema e encoding que a fonte retornou. Incluir **data** (e, se fizer sentido, hora) no nome ou no caminho ajuda a evitar sobrescrita e a ter histórico.

---

## Onde o Airflow grava?

- **Pastas locais** (com volume montado no Docker): ex. `/opt/airflow/datalake/landing/...`.
- **MinIO**: ex. bucket `landing`, caminho como `s3://landing/api_xyz/usuarios/...`.

O Operator que você criar (ex.: `ApiToLandingOperator`) recebe o **caminho base** da Landing (ex.: `datalake/landing/api_publica` ou variável do Airflow) e monta os subcaminhos por tabela e data.

---

## Resumo

| Item | Descrição |
|------|-----------|
| **O que é** | Primeira camada: dados brutos como chegam da fonte. |
| **Por que** | Rastreabilidade, auditoria, reprocessamento; separar “entrada” de “transformação”. |
| **Quem escreve** | Operators (usando Hooks) que extraem das fontes. |
| **Quem lê** | Pipeline Bronze (para fazer upsert e popular a Bronze). |
| **Formato** | Raw (JSON, CSV, etc.), sem transformação de negócio. |

Implemente o Operator que usa o Hook da API e grava nesta pasta; em seguida, a DAG Bronze lerá daqui para popular a Bronze.
