# =============================================================================
# Configuração do pytest para os testes dos plugins
# =============================================================================
# Adiciona a pasta 'plugins' ao path, igual ao Airflow, para imports como
# "hooks.api_publica_hook" e "operators.api_to_landing_operator".
# Execute os testes na raiz: pytest plugins/tests/ -v
# =============================================================================

import sys
from pathlib import Path

plugins_dir = Path(__file__).resolve().parent.parent
if str(plugins_dir) not in sys.path:
    sys.path.insert(0, str(plugins_dir))
