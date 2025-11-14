"""
Funções de visualização utilizando apenas Matplotlib.

Este módulo contém todas as funções responsáveis por criar gráficos
e visualizações dos dados de engajamento usando Matplotlib.
Os gráficos são salvos como arquivos PNG na pasta visualizacoes/.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# Diretório onde os gráficos serão salvos
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "visualizacoes"


def _prepare_output_dir() -> None:
    """
    Função auxiliar que garante que o diretório de saída existe.
    
    Esta função é chamada antes de salvar qualquer gráfico para garantir
    que o diretório visualizacoes/ existe, criando-o se necessário.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def plot_interacoes_por_categoria(df: pd.DataFrame) -> Path:
    """
    Gera um gráfico de barras simples mostrando o score por categoria.
    
    Este gráfico visualiza o engajamento (score) por categoria de conteúdo,
    facilitando a identificação de quais categorias geram mais engajamento.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame com colunas "categoria" e "score" já agregadas.
    
    Returns
    -------
    Path
        Caminho absoluto do arquivo PNG gerado.
    """

    # Garante que o diretório de saída existe
    _prepare_output_dir()
    
    # Cria figura e eixos com tamanho padrão
    fig, ax = plt.subplots(figsize=(6, 4))
    
    # Cria gráfico de barras com cor azul padrão
    ax.bar(df["categoria"], df["score"], color="#4C72B0")
    
    # Configura labels e título
    ax.set_xlabel("Categoria")
    ax.set_ylabel("Score de Engajamento")
    ax.set_title("Score por Categoria")
    
    # Rotaciona labels do eixo X para melhor legibilidade
    plt.xticks(rotation=20, ha="right")
    
    # Ajusta layout para evitar cortes
    plt.tight_layout()
    
    # Define caminho do arquivo de saída
    output = OUTPUT_DIR / "score_por_categoria.png"
    
    # Salva o gráfico em PNG com resolução adequada
    fig.savefig(output, dpi=120)
    
    # Fecha a figura para liberar memória
    plt.close(fig)
    
    return output


def plot_timeline_engajamento(df: pd.DataFrame) -> Path:
    """
    Desenha a evolução diária do score.
    
    Este gráfico de linha mostra como o engajamento evolui ao longo do tempo,
    permitindo identificar tendências, picos e quedas no engajamento diário.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame com colunas "data_interacao" (datetime) e "score" já agregadas
        por dia.
    
    Returns
    -------
    Path
        Caminho absoluto do arquivo PNG gerado.
    """

    # Garante que o diretório de saída existe
    _prepare_output_dir()
    
    # Cria figura e eixos com tamanho padrão
    fig, ax = plt.subplots(figsize=(6, 4))
    
    # Cria gráfico de linha com marcadores circulares e cor verde
    ax.plot(df["data_interacao"], df["score"], marker="o", color="#55A868")
    
    # Configura labels e título
    ax.set_xlabel("Data")
    ax.set_ylabel("Score de Engajamento")
    ax.set_title("Evolução diária do engajamento")
    
    # Adiciona grade sutil para facilitar leitura
    ax.grid(alpha=0.3)
    
    # Ajusta layout para evitar cortes
    plt.tight_layout()
    
    # Define caminho do arquivo de saída
    output = OUTPUT_DIR / "timeline_engajamento.png"
    
    # Formata automaticamente as datas no eixo X para melhor legibilidade
    fig.autofmt_xdate()
    
    # Salva o gráfico em PNG com resolução adequada
    fig.savefig(output, dpi=120)
    
    # Fecha a figura para liberar memória
    plt.close(fig)
    
    return output
