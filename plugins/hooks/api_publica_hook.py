# =============================================================================
# Hook: API Pública Externa
# =============================================================================
# Camada de integração: credenciais (Connection), autenticação (se necessário)
# e métodos para obter dados da API. Não contém regras de negócio.
# =============================================================================

from __future__ import annotations

import logging
from typing import Any

import requests
from airflow.hooks.base import BaseHook

log = logging.getLogger(__name__)


class ApiPublicaHook(BaseHook):
    """
    Hook para conectar a uma API pública externa (ex.: JSONPlaceholder).

    Responsável por:
    - Obter credenciais via Airflow Connection (conn_id).
    - Fazer requests HTTP (GET) para endpoints.
    - Retornar dados em formato dict/list para uso pelo Operator.

    Não implementa regras de negócio; apenas integração com a fonte externa.

    Args:
        conn_id: ID da Connection no Airflow. Deve ter:
            - host: URL base da API (ex.: https://jsonplaceholder.typicode.com)
            - login ou password: API key se a API exigir (opcional para APIs públicas)
        timeout: Timeout em segundos para as requisições. Default 30.

    Example:
        hook = ApiPublicaHook(conn_id="api_publica_default")
        users = hook.get_endpoint("/users")
        tables = hook.get_all_tables({"users": "/users", "posts": "/posts"})
    """

    conn_name_attr = "api_publica_conn_id"
    default_conn_name = "api_publica_default"
    conn_type = "http"
    hook_name = "Api Publica"

    def __init__(
        self,
        conn_id: str = default_conn_name,
        timeout: int = 30,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.conn_id = conn_id
        self.timeout = timeout

    def get_connection(self) -> Any:
        """
        Obtém a Connection do Airflow para este conn_id.

        Returns:
            Objeto Connection com host, login, password (se configurados).

        Raises:
            AirflowException: Se a Connection não existir.
        """
        return super().get_connection(self.conn_id)

    def _request(self, method: str, path: str) -> requests.Response:
        """
        Executa uma requisição HTTP (DRY: reutilizado por get_endpoint e outros).

        Args:
            method: Método HTTP (ex.: "GET").
            path: Caminho do endpoint (ex.: "/users"). Será anexado ao host.

        Returns:
            Objeto Response do requests.

        Raises:
            requests.RequestException: Em caso de erro de rede ou HTTP (ex.: 404, 500).
        """
        conn = self.get_connection()
        base_url = conn.host.rstrip("/")
        url = f"{base_url}{path}" if path.startswith("/") else f"{base_url}/{path}"
        log.info("Request %s %s", method, url)
        response = requests.request(
            method=method,
            url=url,
            timeout=self.timeout,
            headers={"Accept": "application/json"},
            auth=(conn.login, conn.password) if conn.login or conn.password else None,
        )
        response.raise_for_status()
        return response

    def get_endpoint(self, path: str) -> dict | list:
        """
        Obtém dados de um único endpoint via GET.

        Args:
            path: Caminho do endpoint (ex.: "/users", "/posts/1").

        Returns:
            Conteúdo JSON da resposta como dict ou list.

        Raises:
            requests.RequestException: Se a requisição falhar (4xx, 5xx, timeout).
        """
        response = self._request("GET", path)
        return response.json()

    def get_all_tables(self, endpoints: dict[str, str]) -> dict[str, list | dict]:
        """
        Obtém vários endpoints e retorna um dict nome_tabela -> dados.

        Útil para o Operator gravar várias "tabelas" na Landing de uma vez.

        Args:
            endpoints: Dict com nome da tabela -> path do endpoint.
                Ex.: {"users": "/users", "posts": "/posts"}

        Returns:
            Dict com nome da tabela -> lista (ou dict) de registros retornados pela API.
            Em caso de erro em um endpoint, o erro é logado e a chave pode ficar
            com valor vazio ou ser omitida (implementação pode variar).
        """
        result: dict[str, list | dict] = {}
        for table_name, path in endpoints.items():
            try:
                data = self.get_endpoint(path)
                result[table_name] = data if isinstance(data, list) else [data]
            except requests.RequestException as e:
                log.warning("Falha ao obter endpoint %s para tabela %s: %s", path, table_name, e)
                result[table_name] = []
        return result
