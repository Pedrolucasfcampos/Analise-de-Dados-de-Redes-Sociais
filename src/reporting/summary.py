"""
Geração de relatórios a partir das métricas consolidadas.

Este módulo é responsável por formatar e persistir os resultados das análises
em formato Markdown, criando relatórios legíveis e bem estruturados.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable

import pandas as pd

# Diretório onde os relatórios serão salvos
RELATORIOS_DIR = Path(__file__).resolve().parents[2] / "relatorios"


def dataframe_to_markdown(df: pd.DataFrame, headers: Iterable[str]) -> str:
    """
    Converte um DataFrame pequeno em uma tabela Markdown sem dependências.
    
    Esta função auxiliar cria tabelas Markdown manualmente, sem usar bibliotecas
    externas, garantindo compatibilidade e simplicidade.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame a ser convertido em tabela Markdown.
    headers : Iterable[str]
        Lista de nomes das colunas que devem aparecer no cabeçalho da tabela.
    
    Returns
    -------
    str
        String contendo a tabela formatada em Markdown.
    """

    # Cria linha de cabeçalho: | Col1 | Col2 | Col3 |
    header_row = "| " + " | ".join(headers) + " |"
    
    # Cria separador: | --- | --- | --- |
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    
    # Cria linhas de conteúdo: uma linha por linha do DataFrame
    content_rows = [
        "| " + " | ".join(str(row[h]) for h in headers) + " |"
        for _, row in df.iterrows()
    ]
    
    # Junta tudo em uma única string separada por quebras de linha
    return "\n".join([header_row, separator, *content_rows])


def build_markdown_report(
    metrics: Dict[str, float],
    ranking_autores: pd.DataFrame,
    categorias: pd.DataFrame,
    distribuicao: pd.DataFrame,
) -> str:
    """
    Monta um relatório enxuto em Markdown com os principais resultados.
    
    Esta função consolida todas as métricas calculadas em um único relatório
    formatado em Markdown, organizado em seções lógicas para fácil leitura.
    
    Parameters
    ----------
    metrics : Dict[str, float]
        Dicionário com métricas globais de engajamento.
    ranking_autores : pd.DataFrame
        DataFrame com ranking dos autores por engajamento.
    categorias : pd.DataFrame
        DataFrame com interações agregadas por categoria.
    distribuicao : pd.DataFrame
        DataFrame com distribuição percentual dos tipos de interação.
    
    Returns
    -------
    str
        String contendo o relatório completo em formato Markdown.
    """

    # Formata métricas globais como lista com bullets
    # Converte chaves de snake_case para Title Case para melhor legibilidade
    linhas_metricas = "\n".join(
        f"- **{k.replace('_', ' ').title()}**: {v}" for k, v in metrics.items()
    )

    # Monta o relatório em blocos, cada bloco é uma seção
    blocos = [
        "# Relatório de Engajamento",
        
        "## KPIs Gerais",
        linhas_metricas,
        
        "## Autores com Maior Engajamento",
        # Converte DataFrame em tabela Markdown com colunas renomeadas
        dataframe_to_markdown(
            ranking_autores.rename(
                columns={
                    "autor_nome": "Autor",
                    "score_engajamento": "Score",
                }
            ),
            headers=["Autor", "Score"],
        ),
        
        "## Interações por Categoria",
        # Converte DataFrame em tabela Markdown com colunas renomeadas
        dataframe_to_markdown(
            categorias.rename(
                columns={
                    "categoria": "Categoria",
                    "interacoes": "Interações",
                    "score": "Score",
                }
            ),
            headers=["Categoria", "Interações", "Score"],
        ),
        
        "## Distribuição dos Tipos de Interação",
        # Converte DataFrame em tabela Markdown com colunas renomeadas
        dataframe_to_markdown(
            distribuicao.rename(
                columns={
                    "tipo_interacao": "Tipo",
                    "quantidade": "Qtd",
                    "percentual": "%",
                },
            ),
            headers=["Tipo", "Qtd", "%"],
        ),
    ]

    # Junta todos os blocos separados por duas quebras de linha
    return "\n\n".join(blocos)


def persist_report(content: str, filename: str = "relatorio_engajamento.md") -> Path:
    """
    Salva o relatório final na pasta `relatorios`.
    
    Esta função cria o diretório de relatórios se necessário e salva o
    conteúdo do relatório em um arquivo Markdown com encoding UTF-8.
    
    Parameters
    ----------
    content : str
        Conteúdo do relatório em formato Markdown.
    filename : str, optional
        Nome do arquivo a ser criado. Por padrão é "relatorio_engajamento.md".

    Returns
    -------
    Path
        Caminho absoluto do arquivo de relatório criado.
    """

    # Cria o diretório se não existir (incluindo diretórios pais)
    RELATORIOS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Define o caminho completo do arquivo de destino
    destino = RELATORIOS_DIR / filename
    
    # Salva o conteúdo em UTF-8 para suportar caracteres especiais
    destino.write_text(content, encoding="utf-8")
    
    return destino
