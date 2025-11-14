"""
Funções de limpeza e preparação dos dados.

Mantemos esta etapa separada da ingestão para facilitar testes unitários e para
permitir ajustes de regras de negócio sem acoplar o restante do pipeline.

Este módulo é responsável por:
- Normalização e limpeza de strings
- Remoção de duplicatas
- Validação e conversão de tipos
- Criação de features derivadas (pesos de interação, datas normalizadas)
- Combinação de datasets através de joins
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd

# Pesos atribuídos a cada tipo de interação para cálculo de score de engajamento
# Curtidas têm peso menor, compartilhamentos têm peso maior (mais valiosos)
INTERACTION_WEIGHTS = {
    "curtida": 1,
    "comentario": 2,
    "compartilhamento": 3,
}

# Diretório onde os datasets processados serão salvos
PROCESSED_DIR = Path(__file__).resolve().parents[2] / "dados" / "processed"


def _normalize_str_series(series: pd.Series) -> pd.Series:
    """
    Normaliza strings removendo espaços extras e aplicando minúsculas.
    
    Esta função auxiliar garante consistência nos dados de texto, facilitando
    comparações e agregações posteriores.
    
    Parameters
    ----------
    series : pd.Series
        Série pandas contendo valores de texto a serem normalizados.
    
    Returns
    -------
    pd.Series
        Série com strings normalizadas (sem espaços extras, em minúsculas).
    """

    # Converte para tipo string do pandas, remove espaços e converte para minúsculas
    return series.astype("string").str.strip().str.lower()


def clean_usuarios(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicidades e padroniza textos dos usuários.
    
    Esta função limpa o dataset de usuários garantindo:
    - Nomes sem espaços extras
    - Segmentos normalizados (minúsculas, sem espaços)
    - Remoção de usuários duplicados (mantém apenas um por usuario_id)
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame com dados brutos de usuários.
    
    Returns
    -------
    pd.DataFrame
        DataFrame limpo e padronizado.
    """

    # Cria cópia para não modificar o DataFrame original
    cleaned = df.copy()
    
    # Normaliza nomes: remove espaços extras
    cleaned["nome"] = cleaned["nome"].astype("string").str.strip()
    
    # Normaliza segmentos: remove espaços e converte para minúsculas
    cleaned["segmento"] = _normalize_str_series(cleaned["segmento"])
    
    # Remove duplicatas baseado no ID do usuário e reseta índices
    cleaned = cleaned.drop_duplicates(subset="usuario_id").reset_index(drop=True)
    
    return cleaned


def clean_conteudos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Padroniza categorias e garante tipos corretos.
    
    Esta função limpa o dataset de conteúdos garantindo:
    - Categorias normalizadas (minúsculas, sem espaços)
    - Datas de publicação válidas (remove linhas com datas inválidas)
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame com dados brutos de conteúdos.
    
    Returns
    -------
    pd.DataFrame
        DataFrame limpo com apenas conteúdos com datas válidas.
    """

    # Cria cópia para não modificar o DataFrame original
    cleaned = df.copy()
    
    # Normaliza categorias: remove espaços e converte para minúsculas
    cleaned["categoria"] = _normalize_str_series(cleaned["categoria"])
    
    # Converte data_publicacao para datetime, marcando inválidas como NaT
    cleaned["data_publicacao"] = pd.to_datetime(
        cleaned["data_publicacao"], errors="coerce"
    )
    
    # Remove linhas onde a data não pôde ser parseada (essenciais para análises temporais)
    cleaned = cleaned.dropna(subset=["data_publicacao"])
    
    return cleaned


def clean_interacoes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza o tipo de interação e converte timestamps.
    
    Esta função limpa o dataset de interações garantindo:
    - Tipos de interação normalizados
    - Datas válidas
    - Apenas tipos de interação conhecidos (filtra inválidos)
    - Criação da coluna peso_interacao para cálculos de score
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame com dados brutos de interações.
    
    Returns
    -------
    pd.DataFrame
        DataFrame limpo com coluna peso_interacao adicionada.
    """

    # Cria cópia para não modificar o DataFrame original
    cleaned = df.copy()
    
    # Normaliza tipos de interação: remove espaços e converte para minúsculas
    cleaned["tipo_interacao"] = _normalize_str_series(cleaned["tipo_interacao"])
    
    # Converte data_interacao para datetime, marcando inválidas como NaT
    cleaned["data_interacao"] = pd.to_datetime(
        cleaned["data_interacao"], errors="coerce"
    )
    
    # Remove linhas onde a data não pôde ser parseada
    cleaned = cleaned.dropna(subset=["data_interacao"])
    
    # Filtra apenas tipos de interação válidos (definidos em INTERACTION_WEIGHTS)
    cleaned = cleaned[cleaned["tipo_interacao"].isin(INTERACTION_WEIGHTS)].copy()
    
    # Adiciona coluna peso_interacao mapeando o tipo para seu peso correspondente
    # Esta coluna será usada para calcular scores de engajamento
    cleaned["peso_interacao"] = cleaned["tipo_interacao"].map(INTERACTION_WEIGHTS)
    
    return cleaned.reset_index(drop=True)


def build_engagement_dataset(datasets: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Combina os datasets em uma visão única pronta para análises.

    Esta função realiza a junção (join) de todos os datasets para criar
    uma visão consolidada onde cada linha representa uma interação com
    todas as informações relevantes do conteúdo, autor e usuário.

    Retorna um DataFrame contendo:
    - informações do conteúdo e do autor;
    - informações do usuário que interagiu;
    - pesos de interação para facilitar métricas.

    Parameters
    ----------
    datasets : Dict[str, pd.DataFrame]
        Dicionário contendo os datasets brutos:
        - "usuarios": DataFrame de usuários
        - "conteudos": DataFrame de conteúdos
        - "interacoes": DataFrame de interações

    Returns
    -------
    pd.DataFrame
        DataFrame consolidado com todas as informações necessárias
        para análises de engajamento.
    """

    # Limpa cada dataset individualmente antes de combiná-los
    usuarios = clean_usuarios(datasets["usuarios"])
    conteudos = clean_conteudos(datasets["conteudos"])
    interacoes = clean_interacoes(datasets["interacoes"])

    # Prepara visão de autores: renomeia colunas para distinguir do usuário que interage
    autores = usuarios.rename(
        columns={
            "usuario_id": "autor_id",
            "nome": "autor_nome",
            "segmento": "segmento_autor",
        }
    )
    
    # Prepara visão de participantes: renomeia colunas para distinguir do autor
    participantes = usuarios.rename(
        columns={
            "usuario_id": "usuario_id",
            "nome": "usuario_nome",
            "segmento": "segmento_usuario",
        }
    )

    # Realiza joins sequenciais para combinar todos os dados
    # 1. Junta interações com conteúdos (left join para manter todas as interações)
    # 2. Junta com informações do autor do conteúdo
    # 3. Junta com informações do usuário que interagiu
    dataset = (
        interacoes.merge(conteudos, on="conteudo_id", how="left")
        .merge(autores, on="autor_id", how="left")
        .merge(participantes, on="usuario_id", how="left")
        # Remove linhas onde informações essenciais estão faltando
        .dropna(
            subset=[
                "autor_nome",
                "usuario_nome",
                "categoria",
                "data_publicacao",
            ]
        )
        .reset_index(drop=True)
    )

    # Cria coluna derivada com apenas a data (sem hora) para agregações diárias
    dataset["dia_interacao"] = dataset["data_interacao"].dt.date
    
    return dataset


def persist_dataset(df: pd.DataFrame, filename: str = "engajamento.csv") -> Path:
    """
    Salva o dataset processado para reuso em execuções futuras.
    
    Esta função salva o DataFrame processado em formato CSV na pasta
    `dados/processed/`, permitindo que análises subsequentes possam
    usar os dados já processados sem precisar reprocessar tudo.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame processado a ser salvo.
    filename : str, optional
        Nome do arquivo CSV. Por padrão é "engajamento.csv".

    Returns
    -------
    Path
        Caminho absoluto do arquivo CSV criado.
    """

    # Cria o diretório se não existir
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    # Define o caminho completo do arquivo de saída
    output_path = PROCESSED_DIR / filename
    
    # Salva o DataFrame em CSV sem incluir o índice
    df.to_csv(output_path, index=False)
    
    return output_path
