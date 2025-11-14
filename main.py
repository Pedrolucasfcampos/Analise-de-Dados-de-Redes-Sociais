"""
Ponto de entrada para executar o pipeline completo do projeto.

Este módulo orquestra todas as etapas do pipeline de análise de engajamento:
1. Ingestão dos dados brutos (CSV)
2. Preprocessamento e limpeza
3. Cálculo de métricas e análises
4. Geração de relatórios em Markdown
5. Criação de visualizações (opcional)

Uso:
    python main.py                    # Executa pipeline completo com gráficos
    python main.py --skip-plots       # Executa sem gerar gráficos
"""

from __future__ import annotations

import argparse
from typing import Any, Dict, List

# Importações das camadas do projeto
from src.analysis.engajamento import (
    distribuicao_tipo_interacao,
    global_engagement_metrics,
    interacoes_por_categoria,
    timeline_engajamento,
    top_autores_por_engajamento,
)
from src.data.ingestion import load_all_datasets
from src.data.preprocessing import build_engagement_dataset, persist_dataset
from src.reporting.summary import build_markdown_report, persist_report
from src.visualization.matplotlib_charts import (
    plot_interacoes_por_categoria,
    plot_timeline_engajamento,
)

# Tipo customizado para representar o conjunto de métricas calculadas
MetricasEngajamento = Dict[str, Any]


def calcular_metricas_engajamento(engajamento_df) -> MetricasEngajamento:
    """
    Reúne todas as métricas derivadas do dataset de engajamento.
    
    Esta função centraliza o cálculo de todas as métricas de engajamento,
    facilitando a manutenção e permitindo reutilização das métricas em
    diferentes contextos (relatórios, visualizações, etc.).
    
    Parameters
    ----------
    engajamento_df : pd.DataFrame
        DataFrame processado contendo todas as interações com informações
        de conteúdo, autor e usuário.
    
    Returns
    -------
    MetricasEngajamento
        Dicionário contendo:
        - "globais": KPIs gerais (total de interações, conteúdos, etc.)
        - "ranking": Top autores ordenados por score de engajamento
        - "categorias": Agregação de interações por categoria de conteúdo
        - "timeline": Evolução diária do engajamento ao longo do tempo
        - "distribuicao": Percentual de cada tipo de interação
    """

    # Calcula métricas globais (KPIs principais)
    metricas_globais = global_engagement_metrics(engajamento_df)
    
    # Gera ranking dos autores com maior engajamento
    ranking_autores = top_autores_por_engajamento(engajamento_df)
    
    # Agrega interações por categoria de conteúdo
    interacoes_categoria = interacoes_por_categoria(engajamento_df)
    
    # Cria timeline diária do engajamento
    timeline_diaria = timeline_engajamento(engajamento_df)
    
    # Calcula distribuição percentual dos tipos de interação
    distribuicao_tipos = distribuicao_tipo_interacao(engajamento_df)

    return {
        "globais": metricas_globais,
        "ranking": ranking_autores,
        "categorias": interacoes_categoria,
        "timeline": timeline_diaria,
        "distribuicao": distribuicao_tipos,
    }


def gerar_relatorio_markdown(metricas: MetricasEngajamento) -> str:
    """
    Constrói e persiste o relatório markdown a partir das métricas.
    
    Esta função coordena a geração do relatório final em formato Markdown,
    que será salvo na pasta `relatorios/` para visualização posterior.
    
    Parameters
    ----------
    metricas : MetricasEngajamento
        Dicionário contendo todas as métricas calculadas.
    
    Returns
    -------
    str
        Caminho absoluto do arquivo de relatório gerado.
    """

    # Monta o conteúdo do relatório em Markdown
    report_content = build_markdown_report(
        metricas["globais"],
        metricas["ranking"],
        metricas["categorias"],
        metricas["distribuicao"],
    )
    
    # Persiste o relatório em arquivo e retorna o caminho
    return str(persist_report(report_content))


def gerar_graficos_matplotlib(metricas: MetricasEngajamento) -> List[str]:
    """
    Gera os gráficos principais e retorna os caminhos gerados.
    
    Esta função cria visualizações usando Matplotlib para facilitar
    a compreensão dos dados. Os gráficos são salvos na pasta
    `visualizacoes/` em formato PNG.
    
    Parameters
    ----------
    metricas : MetricasEngajamento
        Dicionário contendo todas as métricas calculadas.
    
    Returns
    -------
    List[str]
        Lista com os caminhos absolutos dos arquivos PNG gerados.
    """

    # Gera gráfico de barras mostrando score por categoria
    grafico_categorias = plot_interacoes_por_categoria(metricas["categorias"])
    
    # Gera gráfico de linha mostrando evolução temporal do engajamento
    grafico_timeline = plot_timeline_engajamento(metricas["timeline"])

    return [
        str(grafico_categorias),
        str(grafico_timeline),
    ]


def run_pipeline(*, gerar_graficos: bool = True) -> Dict[str, str]:
    """
    Executa todas as etapas do projeto e retorna caminhos/artefatos gerados.
    
    Esta é a função principal que orquestra todo o pipeline de análise:
    1. Carrega os dados brutos dos arquivos CSV
    2. Preprocessa e limpa os dados
    3. Calcula todas as métricas de engajamento
    4. Gera o relatório em Markdown
    5. Opcionalmente cria visualizações gráficas
    
    Parameters
    ----------
    gerar_graficos : bool, optional
        Se True, gera os gráficos em Matplotlib. Se False, pula esta etapa.
        Útil para execuções mais rápidas ou ambientes sem suporte gráfico.
        Por padrão é True.

    Returns
    -------
    Dict[str, str]
        Dicionário com os caminhos dos artefatos gerados:
        - "dataset_processado": caminho do CSV processado
        - "relatorio_markdown": caminho do relatório Markdown
        - "graficos": caminhos dos arquivos PNG (se gerados)
    """

    # Etapa 1: Carrega todos os datasets brutos (usuarios, conteudos, interacoes)
    datasets = load_all_datasets()
    
    # Etapa 2: Preprocessa e combina os datasets em um único DataFrame
    engajamento_df = build_engagement_dataset(datasets)
    
    # Etapa 3: Calcula todas as métricas de engajamento
    metricas = calcular_metricas_engajamento(engajamento_df)
    
    # Persiste o dataset processado para reuso futuro
    dataset_path = persist_dataset(engajamento_df)

    # Inicializa o dicionário de artefatos gerados
    artefatos: Dict[str, str] = {
        "dataset_processado": str(dataset_path),
        "relatorio_markdown": gerar_relatorio_markdown(metricas),
    }

    # Etapa 4 (opcional): Gera gráficos se solicitado e se há dados
    if gerar_graficos and not engajamento_df.empty:
        graficos = gerar_graficos_matplotlib(metricas)
        # Junta os caminhos dos gráficos em uma string separada por vírgula
        artefatos["graficos"] = ", ".join(graficos)

    return artefatos


def parse_args() -> argparse.Namespace:
    """
    Configura e processa os argumentos da linha de comando.
    
    Returns
    -------
    argparse.Namespace
        Objeto contendo os argumentos parseados da linha de comando.
    """
    parser = argparse.ArgumentParser(
        description="Executa a análise de engajamento da rede social."
    )
    parser.add_argument(
        "--skip-plots",
        action="store_true",
        help="Desativa a geração dos gráficos em Matplotlib.",
    )
    return parser.parse_args()


def main() -> None:
    """
    Função principal do programa.
    
    Esta função é o ponto de entrada quando o script é executado diretamente.
    Ela processa os argumentos da linha de comando, executa o pipeline
    completo e imprime os caminhos dos artefatos gerados.
    """
    # Processa argumentos da linha de comando
    args = parse_args()
    
    # Executa o pipeline completo (com ou sem gráficos conforme argumento)
    artefatos = run_pipeline(gerar_graficos=not args.skip_plots)
    
    # Imprime os caminhos dos artefatos gerados para o usuário
    for chave, caminho in artefatos.items():
        print(f"{chave}: {caminho}")


if __name__ == "__main__":
    main()



