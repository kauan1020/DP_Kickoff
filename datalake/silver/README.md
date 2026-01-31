# Pasta `datalake/silver/`

A **Silver** é a **terceira camada** do datalake. Aqui os dados da **Bronze** (já com última versão por chave) são **modelados** segundo técnicas de modelagem de dados: **Data Vault**, **3NF** e/ou **Star Schema**. A Silver é a camada de “dados limpos e modelados”, prontos para análise e para a Gold.

---

## O que esta pasta faz?

- **Lê** os dados da **Bronze** (tabelas Parquet, uma por entidade, com última versão).
- **Aplica pelo menos um** tipo de modelagem (obrigatório neste guia; idealmente mais de um para estudo):
  - **Data Vault 2.0**: Hubs (chaves de negócio), Links (relacionamentos), Satellites (atributos e histórico).
  - **3NF** (Terceira Forma Normal): tabelas normalizadas, sem redundância desnecessária.
  - **Star Schema**: dimensões (dim_*) e fato(s) (fact_*) para análise e BI.
- **Grava** as tabelas Silver em formato eficiente (ex.: Parquet) para a camada **Gold** consumir e montar agregados e OBT.

Ou seja: Silver = “dados prontos para negócio”, organizados em um (ou mais) modelo(s) de dados.

---

## Por que modelar os dados na Silver?

- **Organização**: Em vez de tabelas “flat” só com última versão, você passa a ter estruturas que refletem entidades, relacionamentos e métricas (Star Schema) ou histórico e integração (Data Vault).
- **Reuso**: Várias tabelas Gold ou relatórios podem consumir a mesma Silver; você modela uma vez e usa em vários lugares.
- **Padrões de mercado**: Data Vault, 3NF e Star Schema são modelos conhecidos; aprender aqui ajuda em outros projetos e em entrevistas.
- **Preparação para análise**: A Gold vai fazer agregações e OBT; ter dimensões e fatos bem definidos na Silver facilita isso.

---

## O que é cada modelo (em uma frase)?

- **Data Vault**: Separa **chaves de negócio** (Hubs), **relacionamentos** (Links) e **atributos/histórico** (Satellites). Bom para integração de várias fontes e histórico.
- **3NF**: Tabelas **normalizadas**: cada atributo depende só da chave; sem repetição desnecessária. Bom para consistência e armazenamento.
- **Star Schema**: **Dimensões** (tabelas descritivas: cliente, produto, data) e **fato(s)** (tabela(s) de métricas com chaves para as dimensões). Bom para BI e consultas analíticas.

Você **deve** aplicar pelo menos um desses modelos; idealmente mais de um para praticar.

---

## Quem escreve e quem lê?

- **Escreve**: a **DAG Silver** (em `dags/silver/`): lê da Bronze, aplica a(s) modelagem(ns), grava aqui.
- **Lê**: a **DAG Gold**: lê da Silver para criar tabelas OBT e agregados.

---

## Que arquivos devem aparecer aqui?

A **DAG Silver** é que cria os arquivos. Sugestão de estrutura (por tipo de modelo):

```
silver/
├── datavault/
│   ├── hub_usuario/
│   ├── hub_pedido/
│   ├── link_pedido_item/
│   ├── satellite_usuario/
│   └── ...
├── normalized_3nf/
│   ├── usuario/
│   ├── pedido/
│   ├── item_pedido/
│   └── ...
├── star_schema/
│   ├── dim_usuario/
│   ├── dim_produto/
│   ├── dim_data/
│   ├── fact_vendas/
│   └── ...
```

Cada modelo pode ser gerado por uma DAG ou por tasks diferentes na mesma DAG. O README da pasta `dags/silver/` descreve quais DAGs criar.

---

## Resumo

| Item | Descrição |
|------|-----------|
| **O que é** | Terceira camada: dados modelados (Data Vault, 3NF e/ou Star Schema). |
| **Por que** | Organização, reuso e preparação para análise; seguir padrões de mercado. |
| **Quem escreve** | DAG Silver (lê da Bronze, modela, grava aqui). |
| **Quem lê** | DAG Gold (para OBT e agregados). |
| **Obrigatório** | Aplicar pelo menos um tipo de modelagem; ideal mais de um. |

Implemente a DAG Silver que lê da Bronze e grava aqui com pelo menos uma (e preferencialmente mais de uma) das modelagens descritas.
