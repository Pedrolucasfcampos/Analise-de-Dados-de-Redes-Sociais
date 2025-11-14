"""
Camada analítica responsável pelos principais indicadores de engajamento.

Este módulo contém todas as funções de análise que calculam métricas
e indicadores de engajamento a partir do dataset processado.
"""

from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd


def global_engagement_metrics(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calcula KPIs gerais para acompanhamento rápido.
    
    Esta função calcula métricas agregadas que fornecem uma visão geral
    do engajamento na plataforma, útil para dashboards e relatórios executivos.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame processado contendo todas as interações com coluna
        peso_interacao já calculada.
    
    Returns
    -------
    Dict[str, float]
        Dicionário com as métricas globais:
        - total_interacoes: número único de interações
        - conteudos_analisados: número único de conteúdos
        - usuarios_participantes: número único de usuários que interagiram
        - engajamento_medio_por_conteudo: média de score por conteúdo
    """

    # Conta interações únicas (cada interacao_id representa uma interação)
    total_interacoes = int(df["interacao_id"].nunique())
    
    # Conta conteúdos únicos que receberam interações
    total_conteudos = int(df["conteudo_id"].nunique())
    
    # Conta usuários únicos que realizaram interações
    usuarios_participantes = int(df["usuario_id"].nunique())

    # Soma todos os pesos de interação para calcular score total
    soma_pesos = float(df["peso_interacao"].sum())
    
    # Calcula engajamento médio: score total dividido pelo número de conteúdos
    # Evita divisão por zero retornando 0.0 se não houver conteúdos
    engajamento_medio = soma_pesos / total_conteudos if total_conteudos else 0.0

    return {
        "total_interacoes": total_interacoes,
        "conteudos_analisados": total_conteudos,
        "usuarios_participantes": usuarios_participantes,
        "engajamento_medio_por_conteudo": round(engajamento_medio, 2),
    }


def top_autores_por_engajamento(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """
    Ranking simples de autores ordenado pelo score de engajamento.
    
    Esta função agrega todas as interações por autor e calcula o score
    total de engajamento, retornando os top N autores com maior engajamento.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame processado contendo interações com informações de autor.
    top_n : int, optional
        Número de autores a retornar no ranking. Por padrão é 5.
    
    Returns
    -------
    pd.DataFrame
        DataFrame com colunas autor_id, autor_nome e score_engajamento,
        ordenado por score decrescente.
    """

    # Agrupa por autor e soma os pesos de interação
    ranking = (
        df.groupby(["autor_id", "autor_nome"], as_index=False)["peso_interacao"]
        .sum()
        # Renomeia a coluna para um nome mais descritivo
        .rename(columns={"peso_interacao": "score_engajamento"})
        # Ordena do maior para o menor score
        .sort_values(by="score_engajamento", ascending=False)
        # Seleciona apenas os top N
        .head(top_n)
        .reset_index(drop=True)
    )
    return ranking


def interacoes_por_categoria(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega interações por categoria de conteúdo.
    
    Esta função agrupa todas as interações por categoria e calcula tanto
    a quantidade de interações quanto o score total de engajamento para
    cada categoria.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame processado contendo interações com informações de categoria.
    
    Returns
    -------
    pd.DataFrame
        DataFrame com colunas categoria, interacoes (contagem) e score (soma),
        ordenado por score decrescente.
    """

    return (
        df.groupby("categoria", as_index=False)
        # Agrega contando interações e somando pesos
        .agg(
            interacoes=("interacao_id", "count"),  # Conta número de interações
            score=("peso_interacao", "sum"),       # Soma os pesos (score total)
        )
        # Ordena por score do maior para o menor
        .sort_values(by="score", ascending=False)
        .reset_index(drop=True)
    )


def timeline_engajamento(df: pd.DataFrame) -> pd.DataFrame:
    """
    Resume o comportamento diário de engajamento.
    
    Esta função agrega as interações por dia, criando uma série temporal
    que mostra a evolução do engajamento ao longo do tempo. Útil para
    identificar tendências e padrões temporais.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame processado com coluna data_interacao do tipo datetime.
    
    Returns
    -------
    pd.DataFrame
        DataFrame com colunas data_interacao, interacoes (contagem diária)
        e score (soma diária de pesos), uma linha por dia.
    """

    timeline = (
        # Define data_interacao como índice para permitir resample
        df.set_index("data_interacao")
        # Agrupa por dia (resample com frequência diária)
        .resample("D")
        # Agrega contando interações e somando scores por dia
        .agg(
            interacoes=("interacao_id", "count"),
            score=("peso_interacao", "sum"),
        )
        # Remove o índice e transforma data_interacao em coluna novamente
        .reset_index()
    )
    return timeline


def distribuicao_tipo_interacao(df: pd.DataFrame) -> pd.DataFrame:
    """
    Retorna a participação relativa de cada tipo de interação.
    
    Esta função calcula quantas interações de cada tipo ocorreram e
    qual o percentual que cada tipo representa do total de interações.
    Útil para entender quais tipos de engajamento são mais comuns.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame processado contendo interações com coluna tipo_interacao.
    
    Returns
    -------
    pd.DataFrame
        DataFrame com colunas tipo_interacao, quantidade (contagem) e
        percentual (porcentagem do total), ordenado por quantidade decrescente.
    """

    # Conta o total de interações para calcular percentuais
    total = df["interacao_id"].count()
    
    # Agrupa por tipo de interação e conta quantas ocorreram
    distribuicao = (
        df.groupby("tipo_interacao", as_index=False)["interacao_id"]
        .count()
        .rename(columns={"interacao_id": "quantidade"})
    )
    
    # Calcula o percentual de cada tipo em relação ao total
    # Usa np.where para evitar divisão por zero
    distribuicao["percentual"] = np.where(
        total == 0, 0.0, (distribuicao["quantidade"] / total * 100).round(2)
    )
    
    # Ordena do tipo mais frequente para o menos frequente
    return distribuicao.sort_values(by="quantidade", ascending=False).reset_index(
        drop=True
    )
