"""Testes simples para a camada analítica."""

from __future__ import annotations

import pandas as pd

from src.analysis import engajamento


def _sample_df() -> pd.DataFrame:
    data = {
        "interacao_id": [1, 2, 3],
        "conteudo_id": [101, 101, 102],
        "usuario_id": [1, 2, 3],
        "autor_id": [10, 10, 11],
        "autor_nome": ["Ana", "Ana", "Bruno"],
        "peso_interacao": [1, 2, 3],
        "categoria": ["video", "video", "texto"],
        "data_interacao": pd.to_datetime(
            ["2025-10-01", "2025-10-01", "2025-10-02"]
        ),
        "tipo_interacao": ["curtida", "comentario", "compartilhamento"],
    }
    return pd.DataFrame(data)


def test_global_engagement_metrics():
    df = _sample_df()
    metrics = engajamento.global_engagement_metrics(df)
    assert metrics["total_interacoes"] == 3
    assert metrics["conteudos_analisados"] == 2
    assert metrics["usuarios_participantes"] == 3


def test_top_autores_por_engajamento():
    df = _sample_df()
    ranking = engajamento.top_autores_por_engajamento(df, top_n=1)
    assert ranking.iloc[0]["autor_nome"] == "Ana"
    assert ranking.iloc[0]["score_engajamento"] == 3

