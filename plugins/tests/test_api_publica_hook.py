# =============================================================================
# Testes do ApiPublicaHook
# =============================================================================
# Testes unitários com mock de Connection e requests HTTP.
# Execute a partir da raiz do projeto: pytest plugins/tests/test_api_publica_hook.py -v
# =============================================================================

from unittest.mock import MagicMock, patch

import pytest
import requests

from hooks.api_publica_hook import ApiPublicaHook


@pytest.fixture
def mock_connection():
    """Connection mock: host da API e credenciais opcionais."""
    conn = MagicMock()
    conn.host = "https://jsonplaceholder.typicode.com"
    conn.login = None
    conn.password = None
    return conn


class TestApiPublicaHook:
    """Testes do Hook da API pública."""

    @patch.object(ApiPublicaHook, "get_connection")
    def test_get_connection_returns_connection(self, mock_get_conn, mock_connection):
        """Quando get_connection é chamado, retorna o objeto Connection configurado."""
        mock_get_conn.return_value = mock_connection
        hook = ApiPublicaHook(conn_id="api_publica_default")
        conn = hook.get_connection()
        assert conn.host == "https://jsonplaceholder.typicode.com"

    @patch.object(ApiPublicaHook, "get_connection")
    @patch("hooks.api_publica_hook.requests.request")
    def test_get_endpoint_returns_json_when_status_200(
        self, mock_request, mock_get_conn, mock_connection
    ):
        """Quando a API retorna 200, get_endpoint retorna o JSON da resposta."""
        mock_get_conn.return_value = mock_connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = [{"id": 1, "name": "Test User"}]
        mock_request.return_value = mock_response

        hook = ApiPublicaHook(conn_id="api_publica_default")
        result = hook.get_endpoint("/users")

        assert result == [{"id": 1, "name": "Test User"}]
        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args[1]
        assert "https://jsonplaceholder.typicode.com/users" in call_kwargs.get("url", "")

    @patch.object(ApiPublicaHook, "get_connection")
    @patch("hooks.api_publica_hook.requests.request")
    def test_get_endpoint_handles_http_error(self, mock_request, mock_get_conn, mock_connection):
        """Quando a API retorna 404, raise_for_status é chamado e exceção é propagada."""
        mock_get_conn.return_value = mock_connection
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_request.return_value = mock_response

        hook = ApiPublicaHook(conn_id="api_publica_default")
        with pytest.raises(requests.HTTPError):
            hook.get_endpoint("/invalid")

    @patch.object(ApiPublicaHook, "get_connection")
    @patch("hooks.api_publica_hook.requests.request")
    def test_get_all_tables_returns_dict_with_tables(
        self, mock_request, mock_get_conn, mock_connection
    ):
        """Quando get_all_tables é chamado com vários endpoints, retorna dict nome_tabela -> dados."""
        mock_get_conn.return_value = mock_connection

        def side_effect(*args, **kwargs):
            url = kwargs.get("url", "")
            resp = MagicMock()
            resp.status_code = 200
            resp.raise_for_status = MagicMock()
            if "users" in url:
                resp.json.return_value = [{"id": 1, "name": "User"}]
            elif "posts" in url:
                resp.json.return_value = [{"id": 1, "title": "Post"}]
            else:
                resp.json.return_value = []
            return resp

        mock_request.side_effect = side_effect

        hook = ApiPublicaHook(conn_id="api_publica_default")
        result = hook.get_all_tables({"users": "/users", "posts": "/posts"})

        assert "users" in result
        assert "posts" in result
        assert result["users"] == [{"id": 1, "name": "User"}]
        assert result["posts"] == [{"id": 1, "title": "Post"}]
        assert mock_request.call_count == 2
