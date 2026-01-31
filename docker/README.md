# Pasta `docker/`

Aqui ficam os arquivos para subir o **Airflow** (e, se você quiser, o **MinIO**) usando **Docker** e **Docker Compose**. Neste projeto o Airflow **sempre** roda em Docker; não usamos instalação do Airflow direto no seu computador.

---

## O que esta pasta faz?

Ela centraliza a **configuração dos containers** do projeto:

- **Airflow**: ferramenta que orquestra os pipelines (DAGs). Ele precisa de um banco de dados (Postgres) para guardar metadados (quais DAGs existem, quando rodaram, etc.).
- **Postgres**: banco usado pelo Airflow para armazenar essas informações.
- **MinIO** (opcional): serviço de armazenamento de arquivos compatível com S3. Se você ativá-lo, pode usar “buckets” (landing, bronze, silver, gold) em vez de pastas no disco; é um passo a mais para quem quer se aproximar de um ambiente real.

Ou seja: esta pasta é o “motor” do ambiente — sem ela, você não tem Airflow rodando.

---

## Por que usar Docker para o Airflow?

- **Ambiente igual para todos**: Quem clonar o repositório e subir os containers tem o mesmo Airflow, mesma versão do Python e das libs, sem “funciona na minha máquina”.
- **Isolamento**: O Airflow não mistura com outros projetos ou com o Python do seu sistema; tudo roda dentro do container.
- **Parecido com produção**: Em muitos times, o Airflow roda em Kubernetes ou em containers; usar Docker desde o estudo ajuda a se acostumar com esse modelo.
- **Simplicidade**: Em vez de instalar Airflow, Postgres e dependências à mão no seu PC, você só precisa ter Docker instalado e rodar o Compose.

**Desvantagem**: você precisa ter Docker (e Docker Compose) instalados. Se ainda não tiver, siga a documentação oficial do Docker para o seu sistema operacional.

---

## O que você vai encontrar aqui

- **Arquivos de referência** (não a implementação pronta): um esqueleto de `docker-compose` e de `Dockerfile` para você completar.
- **Instruções** de o que colocar em cada serviço (Airflow, Postgres, MinIO) e em que ordem usar.

Assim você **aprende** montando o ambiente, em vez de só rodar um comando e não entender o que está acontecendo.

---

## Arquivos que precisam existir (o que você cria/ajusta)

### 1. `docker-compose.yml`

**O que é:** arquivo que diz ao Docker quais serviços subir (Airflow, Postgres, e opcionalmente MinIO) e como configurá-los.

**O que colocar (resumo didático):**

- **Serviço Postgres**  
  Banco de dados do Airflow. Precisa de: imagem (ex.: `postgres:13`), variáveis de ambiente (usuário, senha, nome do banco) e um volume para persistir os dados. Se não configurar o volume, ao derrubar o container você perde o histórico do Airflow.

- **Serviço Airflow (webserver e scheduler)**  
  O Airflow oficial tem imagem no Docker Hub (ex.: `apache/airflow:2.7.0`). Você precisa:
  - **Variáveis de ambiente**: dizer como conectar no Postgres (`AIRFLOW__DATABASE__SQL_ALCHEMY_CONN`), qual executor usar (ex.: `LocalExecutor`), desligar exemplos (`AIRFLOW__CORE__LOAD_EXAMPLES: "false"`) e definir `AIRFLOW_UID` (ex.: 50000).
  - **Volumes**: montar as pastas do seu projeto dentro do container para o Airflow enxergar DAGs e plugins:
    - `../dags` → `/opt/airflow/dags`
    - `../plugins` → `/opt/airflow/plugins`
    - `../datalake` → `/opt/airflow/datalake` (para as DAGs gravarem nas camadas Landing, Bronze, Silver, Gold)
  - **Dependência**: o serviço Airflow deve depender do Postgres (e esperar ele estar saudável).

- **Serviço MinIO (opcional)**  
  Só inclua se quiser usar buckets em vez de pastas locais. Imagem `minio/minio`, comando `server /data`, portas 9000 e 9001, variáveis de usuário e senha, e um volume para persistir dados.

Você pode **copiar** o `docker-compose.yml.example` para `docker-compose.yml` e ir preenchendo com base na documentação oficial do [Airflow](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html) e do [MinIO](https://min.io/docs/minio/container/index.html).

---

### 2. `Dockerfile` (opcional)

**O que é:** receita para construir uma **imagem customizada** do Airflow (por exemplo, com PySpark, drivers ou libs extras).

**Quando usar:** quando as DAGs ou os Operators precisarem de bibliotecas que não vêm na imagem oficial (ex.: `pyspark`, `apache-airflow-providers-http`). Aí você cria um Dockerfile que parte da imagem do Airflow e faz `pip install` do que precisar, e no `docker-compose.yml` usa `build: .` em vez de só `image: apache/airflow:...`.

O `Dockerfile.example` é um esqueleto para você completar.

---

### 3. `.env`

**O que é:** arquivo com variáveis sensíveis (senhas, usuários). O Docker Compose pode ler esse arquivo e injetar as variáveis nos containers.

**Importante:** **nunca** commite o `.env` no Git (ele deve estar no `.gitignore`). Use o `.env.example` como modelo: copie para `.env`, preencha com os valores reais e não compartilhe esse arquivo.

Exemplos do que colocar: `AIRFLOW_UID`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`; se usar MinIO, `MINIO_ROOT_USER` e `MINIO_ROOT_PASSWORD`.

---

## Ordem de uso (passo a passo)

1. **Ler este README** para entender o que cada serviço faz e por que o Airflow está no Docker.
2. **Copiar** `docker-compose.yml.example` para `docker-compose.yml` e **preencher** os serviços (Postgres, Airflow, e MinIO se quiser).
3. **Copiar** `.env.example` para `.env` e preencher com usuário/senha (não commitar o `.env`).
4. **(Opcional)** Se for usar imagem customizada, editar o `Dockerfile.example`, salvar como `Dockerfile` e no Compose usar `build: .` no serviço do Airflow.
5. **Na pasta `docker/`**, rodar:
   ```bash
   docker-compose up -d
   ```
   (ou `docker compose up -d`, conforme sua versão do Docker.)
6. **Acessar** o Airflow no navegador (em geral `http://localhost:8080`). O usuário e senha padrão costumam ser `admin` / `admin` (confira na documentação da imagem que você usou). Se tiver ativado o MinIO, o console costuma estar em `http://localhost:9001`.

---

## Resumo

| Item | Obrigatório? | Descrição |
|------|--------------|-----------|
| **docker-compose.yml** | Sim | Define Airflow + Postgres (e opcionalmente MinIO). Você monta com base no `.example`. |
| **.env** | Recomendado | Senhas e usuários; não commitar. |
| **Dockerfile** | Não | Só se precisar de imagem customizada do Airflow (ex.: com PySpark). |
| **docker-compose.yml.example** | Referência | Molde já incluído no repositório. |
| **Dockerfile.example** | Referência | Molde para imagem customizada. |

O objetivo é você **entender** o que cada peça faz e **montar** o ambiente; por isso a implementação final do `docker-compose.yml` fica a seu cargo, guiada por este README e pela documentação oficial.
