# Pasta `datalake/bronze/`

A **Bronze** é a **segunda camada** do datalake. Aqui os dados da **Landing** são organizados em formato estruturado (ex.: Parquet) e aplicamos **upsert**: para cada **chave** (ex.: ID do usuário), mantemos **apenas a última versão** do registro. Ou seja, é a camada “raw” mas já **consolidada** e pronta para a Silver.

---

## O que esta pasta faz?

- **Lê** os dados da **Landing** (arquivos brutos da API ou de outras fontes).
- **Aplica upsert**: para cada entidade (usuários, pedidos, etc.), define uma chave (ex.: `id`) e garante que na Bronze exista **uma linha por chave** com o dado **mais recente**.
- **Grava** em formato eficiente (ex.: **Parquet**) para a camada **Silver** consumir.
- **Serve de fonte** para os pipelines Silver (modelagem).

Ou seja: Bronze = “última versão do dado bruto”, em formato estruturado.

---

## Por que ter uma camada “última versão” antes da modelagem?

- **Consistência**: Na Silver e na Gold você trabalha com “uma linha por entidade” (um usuário, um pedido), sem duplicatas por chave. O upsert na Bronze garante isso.
- **Performance**: Ler Parquet (ou Delta) na Silver é mais rápido do que ler vários JSONs brutos da Landing.
- **Controle de versão**: Se a mesma chave aparecer em várias extrações (ex.: o mesmo usuário em dois dias), na Bronze fica só a versão mais nova; você não precisa decidir isso de novo na Silver.
- **Padrão de mercado**: A ideia de Bronze “raw + última versão” é comum em datalakes; facilita reprocessamento e modelagem.

---

## O que é Upsert?

- **Insert**: inserir registros **novos** (chave que ainda não existia).
- **Update**: atualizar registros **que já existem** (mesma chave) com os valores mais recentes.
- **Upsert** = Insert + Update em um passo: na Bronze, cada chave aparece **uma vez**, com o dado mais atual que veio da Landing.

Exemplo: se na Landing você tem dois arquivos com o usuário `id=1` (um de ontem e um de hoje), na Bronze fica **uma linha** para `id=1` com os dados de hoje.

---

## Quem escreve e quem lê?

- **Escreve**: a **DAG Bronze** (em `dags/bronze/`): lê da Landing, aplica upsert, grava aqui em Parquet (ou Delta).
- **Lê**: a **DAG Silver**: lê da Bronze para aplicar modelagem (Data Vault, 3NF, Star Schema).

---

## Que arquivos devem aparecer aqui?

A **DAG Bronze** é que cria os arquivos. Sugestão de estrutura:

```
bronze/
├── usuarios/
│   └── *.parquet   (ou por partição, ex.: por data)
├── pedidos/
│   └── *.parquet
├── produtos/
│   └── *.parquet
```

Cada “tabela” Bronze corresponde a uma entidade que você extraiu para a Landing. O pipeline Bronze lê os arquivos da Landing, aplica upsert por chave e grava os Parquets aqui. Você pode adicionar colunas de controle (ex.: `_bronze_loaded_at`, `_source_file`) para rastreabilidade.

---

## Resumo

| Item | Descrição |
|------|-----------|
| **O que é** | Segunda camada: última versão por chave (upsert), em formato estruturado (Parquet). |
| **Por que** | Consistência, performance e controle de versão antes da modelagem. |
| **Quem escreve** | DAG Bronze (lê da Landing, faz upsert, grava aqui). |
| **Quem lê** | DAG Silver (para modelar em Data Vault, 3NF ou Star Schema). |
| **Formato** | Parquet (ou Delta), uma tabela por entidade. |

Implemente a DAG Bronze que lê da Landing e grava aqui com upsert; depois use a Silver para ler desta pasta e aplicar a modelagem.
