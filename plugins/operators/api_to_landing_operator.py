# =============================================================================
# Operator: API → Landing
# =============================================================================
# Camada de negócio: usa o Hook da API, obtém os dados (várias tabelas)
# e grava na Landing. Utiliza a infra (Hook); não implementa conexão.
# =============================================================================

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from airflow.models import BaseOperator

from hooks.api_publica_hook import ApiPublicaHook

log = logging.getLogger(__name__)


class ApiToLandingOperator(BaseOperator):
    """
    Operator que extrai dados de uma API pública (via Hook) e grava na Landing.

    Responsável por:
    - Instanciar o ApiPublicaHook e obter os dados (várias tabelas/endpoints).
    - Gravar cada tabela na pasta Landing em arquivos JSON (um por tabela por execução).
    - Retornar um resumo (quantidade de tabelas e registros) para logs e downstream.

    Não implementa conexão HTTP; usa apenas o Hook.

    Args:
        conn_id: ID da Connection usada pelo Hook (ex.: api_publica_default).
        landing_path: Caminho base da pasta Landing (ex.: datalake/landing/api_publica).
            Suporta template: use {{ ds }} para data de execução.
        tables_endpoints: Dict nome_tabela -> path do endpoint.
            Ex.: {"users": "/users", "posts": "/posts"}
        file_format: Formato do arquivo de saída ("json" ou "csv"). Default "json".

    Example:
        ApiToLandingOperator(
            task_id="extrair_api_publica",
            conn_id="api_publica_default",
            landing_path="datalake/landing/api_publica",
            tables_endpoints={"users": "/users", "posts": "/posts"},
        )
    """

    template_fields = ("landing_path",)
    template_ext = ()

    def __init__(
        self,
        conn_id: str = "api_publica_default",
        landing_path: str = "datalake/landing/api_publica",
        tables_endpoints: dict[str, str] | None = None,
        file_format: str = "json",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.conn_id = conn_id
        self.landing_path = landing_path
        self.tables_endpoints = tables_endpoints or {"users": "/users", "posts": "/posts"}
        self.file_format = file_format

    def execute(self, context: Any) -> dict[str, Any]:
        """
        Executa a extração: obtém dados via Hook e grava na Landing.

        Args:
            context: Contexto do Airflow (contém ds, execution_date, etc.).

        Returns:
            Dict com resumo: tables_written (lista de nomes), total_records (soma),
            path_used (caminho base usado).
        """
        hook = ApiPublicaHook(conn_id=self.conn_id)
        data = hook.get_all_tables(self.tables_endpoints)

        base_path = Path(self.landing_path)
        execution_date = context.get("ds", datetime.now().strftime("%Y-%m-%d"))
        run_path = base_path / execution_date
        run_path.mkdir(parents=True, exist_ok=True)

        tables_written: list[str] = []
        total_records = 0

        for table_name, records in data.items():
            if not records:
                log.warning("Tabela %s sem registros; arquivo não criado.", table_name)
                continue
            table_path = run_path / table_name
            table_path.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = table_path / f"dados_{timestamp}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            tables_written.append(table_name)
            total_records += len(records)
            log.info("Escrito %s: %d registros em %s", table_name, len(records), file_path)

        result = {
            "tables_written": tables_written,
            "total_records": total_records,
            "path_used": str(run_path),
        }
        log.info("Landing escrita: %s", result)
        return result
