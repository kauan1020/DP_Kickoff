# =============================================================================
# Testes do ApiToLandingOperator
# =============================================================================
# Testes unitários com mock do Hook e gravação em disco (tmp_path).
# Execute a partir da raiz do projeto: pytest plugins/tests/test_api_to_landing_operator.py -v
# =============================================================================

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from operators.api_to_landing_operator import ApiToLandingOperator


@pytest.fixture
def operator():
    """Operator com conn_id e landing_path padrão."""
    return ApiToLandingOperator(
        task_id="test_extrair",
        conn_id="api_publica_default",
        landing_path="datalake/landing/api_publica",
        tables_endpoints={"users": "/users", "posts": "/posts"},
    )


@pytest.fixture
def context():
    """Contexto mínimo do Airflow (ds = data de execução)."""
    return {"ds": "2025-01-30"}


class TestApiToLandingOperator:
    """Testes do Operator API → Landing."""

    @patch("operators.api_to_landing_operator.ApiPublicaHook")
    def test_execute_calls_hook_get_all_tables(self, mock_hook_class, operator, context, tmp_path):
        """Quando execute é chamado, instancia o Hook e chama get_all_tables com tables_endpoints."""
        mock_hook = MagicMock()
        mock_hook.get_all_tables.return_value = {
            "users": [{"id": 1, "name": "Test"}],
            "posts": [{"id": 1, "title": "Post"}],
        }
        mock_hook_class.return_value = mock_hook

        operator.landing_path = str(tmp_path)
        result = operator.execute(context)

        mock_hook_class.assert_called_once_with(conn_id="api_publica_default")
        mock_hook.get_all_tables.assert_called_once_with(
            {"users": "/users", "posts": "/posts"}
        )
        assert "tables_written" in result
        assert "users" in result["tables_written"]
        assert "posts" in result["tables_written"]

    @patch("operators.api_to_landing_operator.ApiPublicaHook")
    def test_execute_writes_to_landing(self, mock_hook_class, operator, context, tmp_path):
        """Quando execute é chamado, grava um arquivo JSON por tabela no landing_path."""
        mock_hook = MagicMock()
        mock_hook.get_all_tables.return_value = {
            "users": [{"id": 1, "name": "User A"}],
            "posts": [{"id": 1, "title": "First Post"}],
        }
        mock_hook_class.return_value = mock_hook

        operator.landing_path = str(tmp_path)
        result = operator.execute(context)

        path_used = Path(result["path_used"])
        assert path_used.exists()
        users_dir = path_used / "users"
        posts_dir = path_used / "posts"
        assert users_dir.exists()
        assert posts_dir.exists()
        user_files = list(users_dir.glob("dados_*.json"))
        post_files = list(posts_dir.glob("dados_*.json"))
        assert len(user_files) == 1
        assert len(post_files) == 1
        import json
        with open(user_files[0]) as f:
            data = json.load(f)
        assert data == [{"id": 1, "name": "User A"}]

    @patch("operators.api_to_landing_operator.ApiPublicaHook")
    def test_execute_returns_summary(self, mock_hook_class, operator, context, tmp_path):
        """Quando execute é chamado, retorna resumo com tables_written, total_records e path_used."""
        mock_hook = MagicMock()
        mock_hook.get_all_tables.return_value = {
            "users": [{"id": 1}, {"id": 2}],
            "posts": [{"id": 1}],
        }
        mock_hook_class.return_value = mock_hook

        operator.landing_path = str(tmp_path)
        result = operator.execute(context)

        assert result["tables_written"] == ["users", "posts"]
        assert result["total_records"] == 3
        assert "path_used" in result
        assert "2025-01-30" in result["path_used"]
