# Pasta `datalake/gold/`

A **Gold** é a **última camada** do datalake. Aqui os dados da **Silver** (já modelados) viram **tabelas de análise** e **agregações** prontas para negócio, relatórios e dashboards. O modelo preferencial é o **OBT (One Big Table)**: tabelas “wide”, com dimensões e métricas na mesma tabela, para facilitar consultas e ferramentas de BI.

---

## O que esta pasta faz?

- **Lê** os dados da **Silver** (Data Vault, 3NF e/ou Star Schema — conforme você modelou).
- **Cria tabelas de análise** agregadas: somas, contagens, médias, por período, por dimensão (ex.: vendas por mês, por cliente, por produto).
- **Preferencialmente** aplica o modelo **OBT**: uma tabela (ou um conjunto de OBTs) que junta dimensões e métricas em uma estrutura “wide”, para que relatórios e BI consultem **uma tabela só**, sem vários joins.
- **Persiste** em formato eficiente (ex.: Parquet) para consumo final (BI, relatórios, ML).

Ou seja: Gold = “resposta pronta para perguntas de negócio”.

---

## Por que ter uma camada só para análise?

- **Performance**: Em vez de fazer joins e agregações toda vez que alguém abre um relatório, você faz isso uma vez no pipeline e guarda o resultado na Gold.
- **Simplicidade para quem consome**: Analistas e ferramentas de BI leem tabelas já agregadas ou OBTs; não precisam conhecer Silver nem Bronze.
- **Padrão de mercado**: A ideia de “camada de consumo” ou “curated” (Gold) é comum em datalakes e data warehouses.
- **OBT**: Reduz a quantidade de joins na ponta; uma tabela por caso de uso (ex.: “vendas por cliente e mês”) facilita dashboards e consultas ad hoc.

---

## O que é OBT (One Big Table)?

- **Ideia**: Uma tabela que tem, na **mesma linha**, **dimensões** (atributos para filtro e agrupamento) e **métricas** (valores numéricos: totais, contagens, médias).
- **Vantagem**: Quem consome (BI, analista) faz poucos ou nenhum join; a pergunta “vendas por cliente e mês” já está respondida em uma tabela.
- **Exemplo**: `obt_vendas_mensal` com colunas como `ano`, `mes`, `cliente_id`, `nome_cliente`, `qtd_pedidos`, `valor_total`, `ticket_medio`.

A Gold **deve** consumir a Silver e **deve** criar pelo menos tabelas agregadas; de **preferência** usar OBT para as principais análises.

---

## Quem escreve e quem lê?

- **Escreve**: a **DAG Gold** (em `dags/gold/`): lê da Silver, aplica agregações e monta OBT(s), grava aqui.
- **Lê**: Ferramentas de BI, relatórios, notebooks, processos downstream. **Não há** outra camada do datalake depois da Gold; ela é o fim do fluxo para consumo.

---

## Que arquivos devem aparecer aqui?

A **DAG Gold** é que cria os arquivos. Sugestão de estrutura:

```
gold/
├── obt_vendas_por_cliente/
│   └── *.parquet
├── obt_pedidos_completos/
│   └── *.parquet
├── agregados/
│   ├── vendas_por_mes/
│   ├── vendas_por_produto/
│   ├── top_clientes/
│   └── ...
```

Cada tabela Gold deve ter um **propósito claro** de análise (ex.: “vendas por mês”, “OBT de pedidos para BI”).

---

## Resumo

| Item | Descrição |
|------|-----------|
| **O que é** | Última camada: tabelas de análise e agregações; preferência por OBT. |
| **Por que** | Performance, simplicidade para quem consome e padrão de mercado. |
| **Quem escreve** | DAG Gold (lê da Silver, agrega, monta OBT, grava aqui). |
| **Quem lê** | BI, relatórios, análises; fim do fluxo do datalake. |
| **Obrigatório** | Consumir Silver e criar tabelas agregadas; ideal OBT. |

Implemente a DAG Gold que lê da Silver e grava aqui as tabelas OBT e agregados conforme os casos de uso que você definir.
