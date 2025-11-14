"""
Camada de ingestão de dados do projeto.

Esta etapa centraliza a leitura dos arquivos CSV que compõem o dataset da
rede social simulada. Apesar de os arquivos de exemplo estarem em
``dados/raw``, o módulo permite informar um diretório diferente, o que facilita
testes automatizados e execuções em ambientes distintos (dev/test/prod).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Optional

import pandas as pd


# Diretório padrão onde os arquivos CSV brutos estão localizados
# Usa caminho relativo ao arquivo atual para garantir portabilidade
DEFAULT_RAW_DIR = Path(__file__).resolve().parents[2] / "dados" / "raw"


class DataIngestionError(Exception):
    """
    Exceção customizada para problemas durante a ingestão de dados.
    
    Esta exceção é levantada quando há problemas ao ler os arquivos CSV,
    como arquivo não encontrado, formato inválido ou arquivo vazio.
    """


@dataclass(frozen=True)
class DatasetConfig:
    """
    Configuração mínima para leitura consistente dos arquivos CSV.
    
    Esta classe encapsula as configurações necessárias para ler cada
    dataset de forma padronizada, garantindo tipos de dados corretos
    e parsing adequado de colunas temporais.
    
    Attributes
    ----------
    filename : str
        Nome do arquivo CSV (sem caminho completo).
    dtype_map : Optional[Dict[str, str]], optional
        Mapeamento de nomes de colunas para tipos de dados do pandas.
        Garante consistência de tipos entre execuções.
    parse_dates : Optional[Iterable[str]], optional
        Lista de colunas que devem ser parseadas como datas.
    """

    filename: str
    dtype_map: Optional[Dict[str, str]] = None
    parse_dates: Optional[Iterable[str]] = None


# Configuração de todos os datasets do projeto
# Cada entrada define como o arquivo CSV correspondente deve ser lido
DATASETS = {
    "usuarios": DatasetConfig(
        filename="usuarios.csv",
        # Define tipos explícitos para garantir consistência
        dtype_map={"usuario_id": "int64", "nome": "string", "segmento": "string"},
    ),
    "conteudos": DatasetConfig(
        filename="conteudos.csv",
        dtype_map={
            "conteudo_id": "int64",
            "autor_id": "int64",
            "categoria": "string",
        },
        # Coluna de data deve ser parseada automaticamente
        parse_dates=["data_publicacao"],
    ),
    "interacoes": DatasetConfig(
        filename="interacoes.csv",
        dtype_map={
            "interacao_id": "int64",
            "conteudo_id": "int64",
            "usuario_id": "int64",
            "tipo_interacao": "string",
        },
        # Coluna de data deve ser parseada automaticamente
        parse_dates=["data_interacao"],
    ),
}


def _resolve_path(filename: str, base_dir: Optional[Path]) -> Path:
    """
    Resolve o caminho absoluto do arquivo a partir do diretório base.
    
    Esta função auxiliar garante que o caminho do arquivo seja sempre
    absoluto, facilitando o tratamento de erros e logs.
    
    Parameters
    ----------
    filename : str
        Nome do arquivo ou caminho relativo.
    base_dir : Optional[Path]
        Diretório base opcional. Se None, usa o diretório padrão.
    
    Returns
    -------
    Path
        Caminho absoluto resolvido do arquivo.
    """

    # Usa diretório padrão se nenhum foi especificado
    base = base_dir or DEFAULT_RAW_DIR
    
    # Converte para Path se necessário
    candidate = filename if isinstance(filename, Path) else Path(filename)
    
    # Se o caminho não é absoluto, combina com o diretório base
    if not candidate.is_absolute():
        candidate = base / candidate
    
    return candidate


def load_csv_dataset(
    dataset: DatasetConfig, *, base_dir: Optional[Path] = None
) -> pd.DataFrame:
    """
    Lê um dataset específico com validações básicas.

    A função adiciona algumas salvaguardas:
    - garante que o arquivo exista;
    - aplica mapeamento de tipos para manter consistência;
    - realiza parsing explícito de colunas temporais.

    Parameters
    ----------
    dataset : DatasetConfig
        Configuração do dataset a ser carregado.
    base_dir : Optional[Path], optional
        Diretório base opcional para localizar o arquivo.
        Se None, usa o diretório padrão.

    Returns
    -------
    pd.DataFrame
        DataFrame com os dados do arquivo CSV.

    Raises
    ------
    DataIngestionError
        Se o arquivo não existir, estiver vazio ou houver erro na leitura.
    """

    # Resolve o caminho absoluto do arquivo
    csv_path = _resolve_path(dataset.filename, base_dir)
    
    # Validação: verifica se o arquivo existe
    if not csv_path.exists():
        raise DataIngestionError(f"Arquivo {csv_path} não encontrado.")

    try:
        # Lê o CSV aplicando configurações de tipo e parsing de datas
        df = pd.read_csv(
            csv_path,
            dtype=dataset.dtype_map,
            parse_dates=dataset.parse_dates,
        )
    except Exception as exc:  # pragma: no cover - mensagem amigável
        # Captura qualquer erro e relança com mensagem mais clara
        raise DataIngestionError(f"Falha ao ler {csv_path}: {exc}") from exc

    # Validação: verifica se o DataFrame não está vazio
    if df.empty:
        raise DataIngestionError(f"O arquivo {csv_path} está vazio.")

    return df


def load_all_datasets(base_dir: Optional[Path] = None) -> Dict[str, pd.DataFrame]:
    """
    Carrega todos os datasets configurados e devolve um dicionário.

    Esta função itera sobre todos os datasets definidos em DATASETS
    e carrega cada um deles, retornando um dicionário indexado pelo
    nome do dataset.

    Parameters
    ----------
    base_dir : Optional[Path], optional
        Diretório base opcional para localizar os arquivos.
        Se None, usa o diretório padrão (dados/raw).

    Returns
    -------
    Dict[str, pd.DataFrame]
        Dicionário onde as chaves são os nomes dos datasets ("usuarios",
        "conteudos", "interacoes") e os valores são os DataFrames carregados.

    Raises
    ------
    DataIngestionError
        Se algum arquivo não puder ser carregado.
    """

    # Inicializa dicionário para armazenar os datasets carregados
    loaded: Dict[str, pd.DataFrame] = {}
    
    # Itera sobre todos os datasets configurados
    for name, config in DATASETS.items():
        # Carrega cada dataset usando sua configuração específica
        loaded[name] = load_csv_dataset(config, base_dir=base_dir)
    
    return loaded
