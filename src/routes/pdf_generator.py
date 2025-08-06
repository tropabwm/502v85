#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Gerador de PDF
Endpoints para geração de relatórios em PDF
"""

import os
import logging
import json
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from io import BytesIO
import tempfile

logger = logging.getLogger(__name__)

# Cria blueprint
pdf_bp = Blueprint('pdf', __name__)

class PDFGenerator:
    """Gerador de relatórios PDF profissionais"""

    def __init__(self):
        """Inicializa gerador de PDF"""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Configura estilos personalizados"""

        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1a365d')
        ))

        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            textColor=colors.HexColor('#2d3748')
        ))

        # Seção
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=15,
            spaceBefore=20,
            textColor=colors.HexColor('#4a5568'),
            borderWidth=1,
            borderColor=colors.HexColor('#e2e8f0'),
            borderPadding=5
        ))

        # Texto normal
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            leading=14
        ))

        # Lista
        self.styles.add(ParagraphStyle(
            name='BulletList',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            leftIndent=20,
            bulletIndent=10
        ))

    def generate_analysis_report(self, analysis_data: dict) -> BytesIO:
        """Gera relatório completo da análise"""

        # Cria buffer em memória
        buffer = BytesIO()

        # Cria documento PDF
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        # Constrói conteúdo
        story = []

        # Capa
        story.extend(self._build_cover_page(analysis_data))
        story.append(PageBreak())

        # Sumário executivo
        story.extend(self._build_executive_summary(analysis_data))
        story.append(PageBreak())

        # Avatar detalhado
        if 'avatar_ultra_detalhado' in analysis_data:
            story.extend(self._build_avatar_section(analysis_data['avatar_ultra_detalhado']))
            story.append(PageBreak())

        # Drivers Mentais Customizados
        if 'drivers_mentais_customizados' in analysis_data:
            story.extend(self._build_drivers_section(analysis_data['drivers_mentais_customizados']))
            story.append(PageBreak())
        elif 'drivers_mentais_sistema_completo' in analysis_data:
            drivers_data = analysis_data['drivers_mentais_sistema_completo']
            if drivers_data.get('drivers_customizados'):
                story.extend(self._build_drivers_section(drivers_data['drivers_customizados']))
                story.append(PageBreak())

        # Sistema Anti-Objeção
        if 'sistema_anti_objecao' in analysis_data:
            story.extend(self._build_anti_objection_section(analysis_data['sistema_anti_objecao']))
            story.append(PageBreak())

        # Provas Visuais
        if 'provas_visuais_sugeridas' in analysis_data:
            story.extend(self._build_visual_proofs_section(analysis_data['provas_visuais_sugeridas']))
            story.append(PageBreak())

        # Pré-Pitch Invisível
        if 'pre_pitch_invisivel' in analysis_data:
            story.extend(self._build_pre_pitch_section(analysis_data['pre_pitch_invisivel']))
            story.append(PageBreak())

        # Predições do Futuro
        if 'predicoes_futuro_completas' in analysis_data:
            story.extend(self._build_future_predictions_section(analysis_data['predicoes_futuro_completas']))
            story.append(PageBreak())

        # Posicionamento
        if 'escopo' in analysis_data:
            story.extend(self._build_positioning_section(analysis_data['escopo']))
            story.append(PageBreak())

        # Análise de concorrência
        if 'analise_concorrencia_detalhada' in analysis_data:
            story.extend(self._build_competition_section(analysis_data['analise_concorrencia_detalhada']))
            story.append(PageBreak())

        # Estratégia de marketing
        if 'estrategia_palavras_chave' in analysis_data:
            story.extend(self._build_marketing_section(analysis_data['estrategia_palavras_chave']))
            story.append(PageBreak())

        # Métricas e KPIs
        if 'metricas_performance_detalhadas' in analysis_data:
            story.extend(self._build_metrics_section(analysis_data['metricas_performance_detalhadas']))
            story.append(PageBreak())

        # Projeções
        if 'projecoes_cenarios' in analysis_data:
            story.extend(self._build_projections_section(analysis_data['projecoes_cenarios']))
            story.append(PageBreak())

        # Plano de ação
        if 'plano_acao_detalhado' in analysis_data:
            story.extend(self._build_action_plan_section(analysis_data['plano_acao_detalhado']))
            story.append(PageBreak())

        # Insights exclusivos
        if 'insights_exclusivos' in analysis_data:
            story.extend(self._build_insights_section(analysis_data['insights_exclusivos']))
            story.append(PageBreak())

        # Pesquisa Web Massiva
        if 'pesquisa_web_massiva' in analysis_data:
            story.extend(self._build_research_section(analysis_data['pesquisa_web_massiva']))
            story.append(PageBreak())

        # Análise Estrutural
        if 'analise_estrutural_completa' in analysis_data:
            story.extend(self._build_structural_analysis_section(analysis_data['analise_estrutural_completa']))
            story.append(PageBreak())

        # Análise de Viabilidade
        if 'analise_viabilidade' in analysis_data:
            story.extend(self._build_viability_section(analysis_data['analise_viabilidade']))
            story.append(PageBreak())

        # Roteiro de Lançamento
        if 'roteiro_lancamento_detalhado' in analysis_data:
            story.extend(self._build_launch_plan_section(analysis_data['roteiro_lancamento_detalhado']))
            story.append(PageBreak())

        # Análise de Riscos
        if 'analise_riscos_detalhada' in analysis_data:
            story.extend(self._build_risk_analysis_section(analysis_data['analise_riscos_detalhada']))
            story.append(PageBreak())

        # Arsenal de Conversão
        if 'arsenal_conversao' in analysis_data:
            story.extend(self._build_conversion_arsenal_section(analysis_data['arsenal_conversao']))
            story.append(PageBreak())

        # Funil de Vendas
        if 'funil_vendas_otimizado' in analysis_data:
            story.extend(self._build_sales_funnel_section(analysis_data['funil_vendas_otimizado']))
            story.append(PageBreak())

        # Sistema de Monitoramento
        if 'sistema_monitoramento' in analysis_data:
            story.extend(self._build_monitoring_section(analysis_data['sistema_monitoramento']))
            story.append(PageBreak())

        # Cronograma de Implementação
        if 'cronograma_implementacao' in analysis_data:
            story.extend(self._build_timeline_section(analysis_data['cronograma_implementacao']))
            story.append(PageBreak())

        # Análise Forense
        if 'analise_forense' in analysis_data:
            story.extend(self._build_forensic_section(analysis_data['analise_forense']))
            story.append(PageBreak())

        # Engenharia Reversa Visceral
        if 'engenharia_reversa_visceral' in analysis_data:
            story.extend(self._build_reverse_engineering_section(analysis_data['engenharia_reversa_visceral']))
            story.append(PageBreak())

        # Arsenal de Drivers Mentais
        if 'arsenal_drivers_mentais' in analysis_data:
            story.extend(self._build_mental_drivers_arsenal_section(analysis_data['arsenal_drivers_mentais']))
            story.append(PageBreak())

        # Arsenal de Provas Visuais
        if 'arsenal_provas_visuais' in analysis_data:
            story.extend(self._build_visual_proofs_arsenal_section(analysis_data['arsenal_provas_visuais']))
            story.append(PageBreak())

        # Tendências Emergentes
        if 'analise_tendencias_emergentes' in analysis_data:
            story.extend(self._build_emerging_trends_section(analysis_data['analise_tendencias_emergentes']))
            story.append(PageBreak())

        # Oportunidades de Nicho
        if 'oportunidades_nicho' in analysis_data:
            story.extend(self._build_niche_opportunities_section(analysis_data['oportunidades_nicho']))
            story.append(PageBreak())

        # Estratégia de Pricing
        if 'estrategia_pricing' in analysis_data:
            story.extend(self._build_pricing_strategy_section(analysis_data['estrategia_pricing']))
            story.append(PageBreak())

        # Customer Journey
        if 'customer_journey' in analysis_data:
            story.extend(self._build_customer_journey_section(analysis_data['customer_journey']))
            story.append(PageBreak())

        # Estratégia de Conteúdo
        if 'estrategia_conteudo' in analysis_data:
            story.extend(self._build_content_strategy_section(analysis_data['estrategia_conteudo']))
            story.append(PageBreak())

        # Estratégia de Influenciadores
        if 'estrategia_influenciadores' in analysis_data:
            story.extend(self._build_influencers_section(analysis_data['estrategia_influenciadores']))
            story.append(PageBreak())

        # Estratégia de Parcerias
        if 'estrategia_parcerias' in analysis_data:
            story.extend(self._build_partnerships_section(analysis_data['estrategia_parcerias']))
            story.append(PageBreak())

        # Análise de Sazonalidade
        if 'analise_sazonalidade' in analysis_data:
            story.extend(self._build_seasonality_section(analysis_data['analise_sazonalidade']))
            story.append(PageBreak())

        # Estratégia de Retenção
        if 'estrategia_retencao' in analysis_data:
            story.extend(self._build_retention_strategy_section(analysis_data['estrategia_retencao']))
            story.append(PageBreak())

        # ROI por Canal
        if 'analise_roi_canal' in analysis_data:
            story.extend(self._build_roi_by_channel_section(analysis_data['analise_roi_canal']))
            story.append(PageBreak())

        # Benchmark Competitivo
        if 'benchmark_competitivo' in analysis_data:
            story.extend(self._build_competitive_benchmark_section(analysis_data['benchmark_competitivo']))
            story.append(PageBreak())

        # Análise SWOT
        if 'analise_swot' in analysis_data:
            story.extend(self._build_swot_analysis_section(analysis_data['analise_swot']))
            story.append(PageBreak())

        # Estratégia de Escalabilidade
        if 'estrategia_escalabilidade' in analysis_data:
            story.extend(self._build_scalability_strategy_section(analysis_data['estrategia_escalabilidade']))
            story.append(PageBreak())

        # Impacto Social
        if 'analise_impacto_social' in analysis_data:
            story.extend(self._build_social_impact_section(analysis_data['analise_impacto_social']))
            story.append(PageBreak())

        # Estratégia de Inovação
        if 'estrategia_inovacao' in analysis_data:
            story.extend(self._build_innovation_strategy_section(analysis_data['estrategia_inovacao']))
            story.append(PageBreak())

        # Plano de Contingência
        if 'plano_contingencia' in analysis_data:
            story.extend(self._build_contingency_plan_section(analysis_data['plano_contingencia']))
            story.append(PageBreak())

        # Sustentabilidade
        if 'analise_sustentabilidade' in analysis_data:
            story.extend(self._build_sustainability_section(analysis_data['analise_sustentabilidade']))
            story.append(PageBreak())

        # Roadmap de Tecnologia
        if 'roadmap_tecnologia' in analysis_data:
            story.extend(self._build_technology_roadmap_section(analysis_data['roadmap_tecnologia']))
            story.append(PageBreak())

        # Internacionalização
        if 'estrategia_internacionalizacao' in analysis_data:
            story.extend(self._build_internationalization_section(analysis_data['estrategia_internacionalizacao']))
            story.append(PageBreak())

        # Compliance
        if 'analise_compliance' in analysis_data:
            story.extend(self._build_compliance_section(analysis_data['analise_compliance']))
            story.append(PageBreak())

        # Apêndices
        if 'apendices' in analysis_data:
            story.extend(self._build_appendices_section(analysis_data['apendices']))
            story.append(PageBreak())


        # Recomendações Finais
        story.extend(self._build_final_recommendations_section(analysis_data))


        # Gera PDF
        doc.build(story)
        buffer.seek(0)

        return buffer

    def _build_cover_page(self, data: dict) -> list:
        """Constrói página de capa"""
        story = []

        # Título principal
        story.append(Paragraph("ANÁLISE ULTRA-DETALHADA DE MERCADO", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*inch))

        # Subtítulo
        segmento = data.get('segmento', 'Não informado')
        produto = data.get('produto', 'Não informado')

        story.append(Paragraph(f"Segmento: {segmento}", self.styles['CustomSubtitle']))
        if produto != 'Não informado':
            story.append(Paragraph(f"Produto: {produto}", self.styles['CustomSubtitle']))

        story.append(Spacer(1, 1*inch))

        # Informações do relatório
        metadata = data.get('metadata', {})
        generated_at = metadata.get('generated_at', datetime.now().isoformat())

        info_data = [
            ['Data de Geração:', generated_at[:10]],
            ['Versão:', '2.0.0'],
            ['Modelo IA:', metadata.get('model', 'Gemini Pro')],
            ['Tempo de Processamento:', f"{metadata.get('processing_time', 0)} segundos"]
        ]

        info_table = Table(info_data, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey)
        ]))

        story.append(info_table)
        story.append(Spacer(1, 1*inch))

        # Rodapé da capa
        story.append(Paragraph("ARQV30 Enhanced v2.0", self.styles['CustomNormal']))
        story.append(Paragraph("Powered by Artificial Intelligence", self.styles['CustomNormal']))

        return story

    def _build_executive_summary(self, data: dict) -> list:
        """Constrói sumário executivo"""
        story = []

        story.append(Paragraph("SUMÁRIO EXECUTIVO", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Resumo dos principais pontos
        summary_points = [
            f"Segmento analisado: {data.get('segmento', 'N/A')}",
            f"Público-alvo: {data.get('publico', 'N/A')}",
            f"Preço: R$ {data.get('preco', 'N/A')}",
            f"Objetivo de receita: R$ {data.get('objetivo_receita', 'N/A')}"
        ]

        for point in summary_points:
            story.append(Paragraph(f"• {point}", self.styles['BulletList']))

        story.append(Spacer(1, 0.2*inch))

        # Principais insights
        insights = data.get('insights_exclusivos', [])
        if insights:
            story.append(Paragraph("Principais Insights:", self.styles['SectionHeader']))
            for insight in insights[:5]:  # Primeiros 5 insights
                story.append(Paragraph(f"• {insight}", self.styles['BulletList']))

        return story

    def _build_avatar_section(self, avatar_data: dict) -> list:
        """Constrói seção do avatar"""
        story = []

        story.append(Paragraph("AVATAR ULTRA-DETALHADO", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Perfil demográfico
        demo = avatar_data.get('perfil_demografico', {})
        if demo:
            story.append(Paragraph("Perfil Demográfico", self.styles['SectionHeader']))

            demo_data = [
                ['Idade:', demo.get('idade', 'N/A')],
                ['Gênero:', demo.get('genero', 'N/A')],
                ['Renda:', demo.get('renda', 'N/A')],
                ['Escolaridade:', demo.get('escolaridade', 'N/A')],
                ['Localização:', demo.get('localizacao', 'N/A')]
            ]

            demo_table = Table(demo_data, colWidths=[1.5*inch, 4*inch])
            demo_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))

            story.append(demo_table)
            story.append(Spacer(1, 0.2*inch))

        # Perfil psicográfico
        psico = avatar_data.get('perfil_psicografico', {})
        if psico:
            story.append(Paragraph("Perfil Psicográfico", self.styles['SectionHeader']))

            for key, value in psico.items():
                if value:
                    story.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b> {value}", self.styles['CustomNormal']))

        # Dores específicas
        dores = avatar_data.get('dores_especificas', [])
        if dores:
            story.append(Paragraph("Dores Específicas", self.styles['SectionHeader']))
            for dor in dores:
                story.append(Paragraph(f"• {dor}", self.styles['BulletList']))

        # Desejos profundos
        desejos = avatar_data.get('desejos_profundos', [])
        if desejos:
            story.append(Paragraph("Desejos Profundos", self.styles['SectionHeader']))
            for desejo in desejos:
                story.append(Paragraph(f"• {desejo}", self.styles['BulletList']))

        return story

    def _build_drivers_section(self, drivers_data) -> list:
        """Constrói seção de drivers mentais"""
        story = []

        story.append(Paragraph("DRIVERS MENTAIS CUSTOMIZADOS", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        if isinstance(drivers_data, dict) and 'drivers_customizados' in drivers_data:
            drivers = drivers_data['drivers_customizados']
        elif isinstance(drivers_data, list):
            drivers = drivers_data
        else:
            drivers = []

        for i, driver in enumerate(drivers, 1):
            if isinstance(driver, dict):
                story.append(Paragraph(f"Driver {i}: {driver.get('nome', 'Driver Mental')}", self.styles['SectionHeader']))

                story.append(Paragraph(f"<b>Gatilho Central:</b> {driver.get('gatilho_central', 'N/A')}", self.styles['CustomNormal']))
                story.append(Paragraph(f"<b>Definição:</b> {driver.get('definicao_visceral', 'N/A')}", self.styles['CustomNormal']))

                if driver.get('roteiro_ativacao'):
                    roteiro = driver['roteiro_ativacao']
                    story.append(Paragraph("<b>Roteiro de Ativação:</b>", self.styles['CustomNormal']))
                    story.append(Paragraph(f"• Pergunta: {roteiro.get('pergunta_abertura', 'N/A')}", self.styles['BulletList']))
                    story.append(Paragraph(f"• História: {roteiro.get('historia_analogia', 'N/A')}", self.styles['BulletList']))
                    story.append(Paragraph(f"• Comando: {roteiro.get('comando_acao', 'N/A')}", self.styles['BulletList']))

                if driver.get('frases_ancoragem'):
                    story.append(Paragraph("<b>Frases de Ancoragem:</b>", self.styles['CustomNormal']))
                    for frase in driver['frases_ancoragem']:
                        story.append(Paragraph(f"• \"{frase}\"", self.styles['BulletList']))

                story.append(Spacer(1, 0.2*inch))

        return story

    def _build_anti_objection_section(self, anti_objection_data) -> list:
        """Constrói seção do sistema anti-objeção"""
        story = []

        story.append(Paragraph("SISTEMA ANTI-OBJEÇÃO", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Objeções universais
        if anti_objection_data.get('objecoes_universais'):
            story.append(Paragraph("Objeções Universais", self.styles['SectionHeader']))

            for tipo, objecao in anti_objection_data['objecoes_universais'].items():
                if isinstance(objecao, dict):
                    story.append(Paragraph(f"<b>{tipo.title()}:</b>", self.styles['CustomNormal']))
                    story.append(Paragraph(f"Objeção: {objecao.get('objecao', 'N/A')}", self.styles['BulletList']))
                    story.append(Paragraph(f"Contra-ataque: {objecao.get('contra_ataque', 'N/A')}", self.styles['BulletList']))
                    story.append(Spacer(1, 0.1*inch))

        # Objeções ocultas
        if anti_objection_data.get('objecoes_ocultas'):
            story.append(Paragraph("Objeções Ocultas", self.styles['SectionHeader']))

            for tipo, objecao in anti_objection_data['objecoes_ocultas'].items():
                if isinstance(objecao, dict):
                    story.append(Paragraph(f"<b>{tipo.replace('_', ' ').title()}:</b>", self.styles['CustomNormal']))
                    story.append(Paragraph(f"Perfil: {objecao.get('perfil_tipico', 'N/A')}", self.styles['BulletList']))
                    story.append(Paragraph(f"Contra-ataque: {objecao.get('contra_ataque', 'N/A')}", self.styles['BulletList']))
                    story.append(Spacer(1, 0.1*inch))

        return story

    def _build_visual_proofs_section(self, visual_proofs_data) -> list:
        """Constrói seção de provas visuais"""
        story = []

        story.append(Paragraph("PROVAS VISUAIS INSTANTÂNEAS", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        if isinstance(visual_proofs_data, list):
            for i, prova in enumerate(visual_proofs_data, 1):
                if isinstance(prova, dict):
                    story.append(Paragraph(f"PROVI {i}: {prova.get('nome', 'Prova Visual')}", self.styles['SectionHeader']))

                    story.append(Paragraph(f"<b>Conceito Alvo:</b> {prova.get('conceito_alvo', 'N/A')}", self.styles['CustomNormal']))
                    story.append(Paragraph(f"<b>Experimento:</b> {prova.get('experimento', 'N/A')}", self.styles['CustomNormal']))

                    if prova.get('materiais'):
                        story.append(Paragraph("<b>Materiais:</b>", self.styles['CustomNormal']))
                        for material in prova['materiais']:
                            story.append(Paragraph(f"• {material}", self.styles['BulletList']))

                    story.append(Spacer(1, 0.2*inch))

        return story

    def _build_pre_pitch_section(self, pre_pitch_data) -> list:
        """Constrói seção do pré-pitch invisível"""
        story = []

        story.append(Paragraph("PRÉ-PITCH INVISÍVEL", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Orquestração emocional
        if pre_pitch_data.get('orquestracao_emocional'):
            story.append(Paragraph("Orquestração Emocional", self.styles['SectionHeader']))

            sequencia = pre_pitch_data['orquestracao_emocional'].get('sequencia_psicologica', [])
            for fase in sequencia:
                if isinstance(fase, dict):
                    story.append(Paragraph(f"<b>{fase.get('fase', 'Fase')}:</b> {fase.get('objetivo', 'N/A')}", self.styles['CustomNormal']))
                    story.append(Paragraph(f"Tempo: {fase.get('tempo', 'N/A')}", self.styles['BulletList']))
                    if fase.get('tecnicas'):
                        story.append(Paragraph(f"Técnicas: {', '.join(fase['tecnicas'])}", self.styles['BulletList']))
                    story.append(Spacer(1, 0.1*inch))

        # Roteiro completo
        if pre_pitch_data.get('roteiro_completo'):
            story.append(Paragraph("Roteiro Completo", self.styles['SectionHeader']))
            roteiro = pre_pitch_data['roteiro_completo']

            if roteiro.get('abertura'):
                abertura = roteiro['abertura']
                story.append(Paragraph(f"<b>Abertura ({abertura.get('tempo', 'N/A')}):</b>", self.styles['CustomNormal']))
                story.append(Paragraph(abertura.get('script', 'N/A'), self.styles['BulletList']))

            if roteiro.get('fechamento'):
                fechamento = roteiro['fechamento']
                story.append(Paragraph(f"<b>Fechamento ({fechamento.get('tempo', 'N/A')}):</b>", self.styles['CustomNormal']))
                story.append(Paragraph(fechamento.get('script', 'N/A'), self.styles['BulletList']))

        return story

    def _build_research_section(self, research_data) -> list:
        """Constrói seção da pesquisa web massiva"""
        story = []

        story.append(Paragraph("PESQUISA WEB MASSIVA", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Estatísticas da pesquisa
        story.append(Paragraph("Estatísticas da Pesquisa", self.styles['SectionHeader']))

        stats_data = [
            ['Métrica', 'Valor'],
            ['Total de Queries', str(research_data.get('total_queries', 0))],
            ['Total de Resultados', str(research_data.get('total_resultados', 0))],
            ['Conteúdo Extraído', f"{research_data.get('conteudo_extraido_chars', 0):,} caracteres"],
        ]

        stats_table = Table(stats_data, colWidths=[2*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(stats_table)
        story.append(Spacer(1, 0.2*inch))

        # Queries executadas
        if research_data.get('queries_executadas'):
            story.append(Paragraph("Queries Executadas", self.styles['SectionHeader']))
            for query in research_data['queries_executadas'][:10]:  # Primeiras 10
                story.append(Paragraph(f"• {query}", self.styles['BulletList']))

        return story

    def _build_positioning_section(self, escopo_data: dict) -> list:
        """Constrói seção de posicionamento"""
        story = []

        story.append(Paragraph("ESCOPO E POSICIONAMENTO", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Posicionamento no mercado
        posicionamento = escopo_data.get('posicionamento_mercado', '')
        if posicionamento:
            story.append(Paragraph("Posicionamento no Mercado", self.styles['SectionHeader']))
            story.append(Paragraph(posicionamento, self.styles['CustomNormal']))

        # Proposta de valor
        proposta = escopo_data.get('proposta_valor', '')
        if proposta:
            story.append(Paragraph("Proposta de Valor", self.styles['SectionHeader']))
            story.append(Paragraph(proposta, self.styles['CustomNormal']))

        # Diferenciais competitivos
        diferenciais = escopo_data.get('diferenciais_competitivos', [])
        if diferenciais:
            story.append(Paragraph("Diferenciais Competitivos", self.styles['SectionHeader']))
            for diferencial in diferenciais:
                story.append(Paragraph(f"• {diferencial}", self.styles['BulletList']))

        return story

    def _build_competition_section(self, competition_data: dict) -> list:
        """Constrói seção de análise de concorrência"""
        story = []

        story.append(Paragraph("ANÁLISE DE CONCORRÊNCIA", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Concorrentes diretos
        diretos = competition_data.get('concorrentes_diretos', [])
        if diretos:
            story.append(Paragraph("Concorrentes Diretos", self.styles['SectionHeader']))

            for i, concorrente in enumerate(diretos, 1):
                if isinstance(concorrente, dict):
                    nome = concorrente.get('nome', f'Concorrente {i}')
                    story.append(Paragraph(f"<b>{nome}</b>", self.styles['CustomNormal']))

                    pontos_fortes = concorrente.get('pontos_fortes', [])
                    if pontos_fortes:
                        story.append(Paragraph("Pontos Fortes:", self.styles['CustomNormal']))
                        for ponto in pontos_fortes:
                            story.append(Paragraph(f"• {ponto}", self.styles['BulletList']))

                    pontos_fracos = concorrente.get('pontos_fracos', [])
                    if pontos_fracos:
                        story.append(Paragraph("Pontos Fracos:", self.styles['CustomNormal']))
                        for ponto in pontos_fracos:
                            story.append(Paragraph(f"• {ponto}", self.styles['BulletList']))

                    story.append(Spacer(1, 0.1*inch))

        # Gaps de oportunidade
        gaps = competition_data.get('gaps_oportunidade', [])
        if gaps:
            story.append(Paragraph("Oportunidades Identificadas", self.styles['SectionHeader']))
            for gap in gaps:
                story.append(Paragraph(f"• {gap}", self.styles['BulletList']))

        return story

    def _build_marketing_section(self, marketing_data: dict) -> list:
        """Constrói seção de estratégia de marketing"""
        story = []

        story.append(Paragraph("ESTRATÉGIA DE MARKETING", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Palavras-chave primárias
        primarias = marketing_data.get('palavras_primarias', [])
        if primarias:
            story.append(Paragraph("Palavras-Chave Primárias", self.styles['SectionHeader']))
            story.append(Paragraph(", ".join(primarias), self.styles['CustomNormal']))

        # Palavras-chave secundárias
        secundarias = marketing_data.get('palavras_secundarias', [])
        if secundarias:
            story.append(Paragraph("Palavras-Chave Secundárias", self.styles['SectionHeader']))
            story.append(Paragraph(", ".join(secundarias[:15]), self.styles['CustomNormal']))

        # Long tail
        long_tail = marketing_data.get('long_tail', [])
        if long_tail:
            story.append(Paragraph("Palavras-Chave Long Tail", self.styles['SectionHeader']))
            story.append(Paragraph(", ".join(long_tail[:10]), self.styles['CustomNormal']))

        return story

    def _build_metrics_section(self, metrics_data: dict) -> list:
        """Constrói seção de métricas"""
        story = []

        story.append(Paragraph("MÉTRICAS DE PERFORMANCE", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # KPIs principais
        kpis = metrics_data.get('kpis_principais', [])
        if kpis:
            story.append(Paragraph("KPIs Principais", self.styles['SectionHeader']))

            for kpi in kpis:
                if isinstance(kpi, dict):
                    metrica = kpi.get('metrica', 'N/A')
                    objetivo = kpi.get('objetivo', 'N/A')
                    story.append(Paragraph(f"<b>{metrica}:</b> {objetivo}", self.styles['CustomNormal']))

        # ROI esperado
        roi = metrics_data.get('roi_esperado', '')
        if roi:
            story.append(Paragraph("ROI Esperado", self.styles['SectionHeader']))
            story.append(Paragraph(roi, self.styles['CustomNormal']))

        return story

    def _build_projections_section(self, projections_data: dict) -> list:
        """Constrói seção de projeções"""
        story = []

        story.append(Paragraph("PROJEÇÕES E CENÁRIOS", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Tabela de cenários
        cenarios = ['conservador', 'realista', 'otimista']
        table_data = [['Cenário', 'Receita Mensal', 'Clientes/Mês', 'Ticket Médio']]

        for cenario in cenarios:
            cenario_data = projections_data.get(cenario, {})
            if cenario_data:
                table_data.append([
                    cenario.title(),
                    cenario_data.get('receita_mensal', 'N/A'),
                    cenario_data.get('clientes_mes', 'N/A'),
                    cenario_data.get('ticket_medio', 'N/A')
                ])

        if len(table_data) > 1:
            projections_table = Table(table_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            projections_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            story.append(projections_table)

        return story

    def _build_action_plan_section(self, action_data: dict) -> list:
        """Constrói seção do plano de ação"""
        story = []

        story.append(Paragraph("PLANO DE AÇÃO DETALHADO", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Fases do plano
        fases = ['fase_1_preparacao', 'fase_2_lancamento', 'fase_3_crescimento']

        for fase in fases:
            fase_data = action_data.get(fase, {})
            if fase_data:
                fase_nome = fase.replace('_', ' ').title()
                story.append(Paragraph(fase_nome, self.styles['SectionHeader']))

                duracao = fase_data.get('duracao', 'N/A')
                story.append(Paragraph(f"<b>Duração:</b> {duracao}", self.styles['CustomNormal']))

                atividades = fase_data.get('atividades', [])
                if atividades:
                    story.append(Paragraph("<b>Atividades:</b>", self.styles['CustomNormal']))
                    for atividade in atividades:
                        story.append(Paragraph(f"• {atividade}", self.styles['BulletList']))

                story.append(Spacer(1, 0.1*inch))

        return story

    def _build_future_predictions_section(self, predictions_data) -> list:
        """Constrói seção de predições do futuro"""
        story = []

        story.append(Paragraph("PREDIÇÕES DO FUTURO", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Tendências atuais
        if predictions_data.get('tendencias_atuais'):
            story.append(Paragraph("Tendências Atuais", self.styles['SectionHeader']))

            tendencias = predictions_data['tendencias_atuais']
            if tendencias.get('tendencias_relevantes'):
                for trend_name, trend_data in tendencias['tendencias_relevantes'].items():
                    story.append(Paragraph(f"<b>{trend_name.title()}:</b>", self.styles['CustomNormal']))
                    story.append(Paragraph(f"Fase: {trend_data.get('fase_atual', 'N/A')}", self.styles['BulletList']))
                    story.append(Paragraph(f"Impacto: {trend_data.get('impacto_esperado', 'N/A')}", self.styles['BulletList']))
                    story.append(Spacer(1, 0.1*inch))

        # Cenários futuros
        if predictions_data.get('cenarios_futuros'):
            story.append(Paragraph("Cenários Futuros", self.styles['SectionHeader']))

            for scenario_name, scenario_data in predictions_data['cenarios_futuros'].items():
                story.append(Paragraph(f"<b>{scenario_data.get('nome', scenario_name)}:</b>", self.styles['CustomNormal']))
                story.append(Paragraph(f"Probabilidade: {scenario_data.get('probabilidade', 'N/A')}", self.styles['BulletList']))
                story.append(Paragraph(f"Descrição: {scenario_data.get('descricao', 'N/A')}", self.styles['BulletList']))
                story.append(Spacer(1, 0.1*inch))

        # Oportunidades emergentes
        if predictions_data.get('oportunidades_emergentes'):
            story.append(Paragraph("Oportunidades Emergentes", self.styles['SectionHeader']))

            for opp in predictions_data['oportunidades_emergentes'][:5]:
                if isinstance(opp, dict):
                    story.append(Paragraph(f"<b>{opp.get('nome', 'Oportunidade')}:</b>", self.styles['CustomNormal']))
                    story.append(Paragraph(f"Potencial: {opp.get('potencial_mercado', 'N/A')}", self.styles['BulletList']))
                    story.append(Paragraph(f"Timeline: {opp.get('timeline', 'N/A')}", self.styles['BulletList']))
                    story.append(Spacer(1, 0.1*inch))

        return story

    def _build_insights_section(self, insights: list) -> list:
        """Constrói seção de insights exclusivos"""
        story = []

        story.append(Paragraph("INSIGHTS EXCLUSIVOS", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        for i, insight in enumerate(insights, 1):
            story.append(Paragraph(f"{i}. {insight}", self.styles['CustomNormal']))
            story.append(Spacer(1, 0.1*inch))

        return story

    def _build_structural_analysis_section(self, structural_data: dict) -> list:
        """Constrói seção de análise estrutural"""
        story = []

        story.append(Paragraph("ANÁLISE ESTRUTURAL COMPLETA", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Estrutura do mercado
        if structural_data.get('estrutura_mercado'):
            story.append(Paragraph("Estrutura do Mercado", self.styles['SectionHeader']))
            story.append(Paragraph(structural_data['estrutura_mercado'], self.styles['CustomNormal']))

        # Segmentação avançada
        if structural_data.get('segmentacao_avancada'):
            story.append(Paragraph("Segmentação Avançada", self.styles['SectionHeader']))
            segmentacao = structural_data['segmentacao_avancada']
            for segmento, dados in segmentacao.items():
                story.append(Paragraph(f"<b>{segmento.title()}:</b> {dados}", self.styles['CustomNormal']))

        # Barreiras de entrada
        if structural_data.get('barreiras_entrada'):
            story.append(Paragraph("Barreiras de Entrada", self.styles['SectionHeader']))
            for barreira in structural_data['barreiras_entrada']:
                story.append(Paragraph(f"• {barreira}", self.styles['BulletList']))

        return story

    def _build_viability_section(self, viability_data: dict) -> list:
        """Constrói seção de análise de viabilidade"""
        story = []

        story.append(Paragraph("ANÁLISE DE VIABILIDADE", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Viabilidade técnica
        if viability_data.get('viabilidade_tecnica'):
            story.append(Paragraph("Viabilidade Técnica", self.styles['SectionHeader']))
            tecnica = viability_data['viabilidade_tecnica']
            story.append(Paragraph(f"Score: {tecnica.get('score', 'N/A')}/10", self.styles['CustomNormal']))
            if tecnica.get('observacoes'):
                story.append(Paragraph(f"Observações: {tecnica['observacoes']}", self.styles['CustomNormal']))

        # Viabilidade econômica
        if viability_data.get('viabilidade_economica'):
            story.append(Paragraph("Viabilidade Econômica", self.styles['SectionHeader']))
            economica = viability_data['viabilidade_economica']

            if economica.get('investimento_inicial'):
                story.append(Paragraph(f"Investimento Inicial: R$ {economica['investimento_inicial']}", self.styles['CustomNormal']))
            if economica.get('break_even'):
                story.append(Paragraph(f"Break-even: {economica['break_even']}", self.styles['CustomNormal']))
            if economica.get('roi_projetado'):
                story.append(Paragraph(f"ROI Projetado: {economica['roi_projetado']}", self.styles['CustomNormal']))

        # Viabilidade de mercado
        if viability_data.get('viabilidade_mercado'):
            story.append(Paragraph("Viabilidade de Mercado", self.styles['SectionHeader']))
            mercado = viability_data['viabilidade_mercado']
            story.append(Paragraph(f"Tamanho do Mercado: {mercado.get('tamanho', 'N/A')}", self.styles['CustomNormal']))
            story.append(Paragraph(f"Taxa de Crescimento: {mercado.get('crescimento', 'N/A')}", self.styles['CustomNormal']))

        return story

    def _build_launch_plan_section(self, launch_data: dict) -> list:
        """Constrói seção do roteiro de lançamento"""
        story = []

        story.append(Paragraph("ROTEIRO DE LANÇAMENTO DETALHADO", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Fases do lançamento
        fases = ['pre_lancamento', 'lancamento', 'pos_lancamento']

        for fase in fases:
            fase_data = launch_data.get(fase, {})
            if fase_data:
                fase_nome = fase.replace('_', ' ').title()
                story.append(Paragraph(fase_nome, self.styles['SectionHeader']))

                if fase_data.get('duracao'):
                    story.append(Paragraph(f"<b>Duração:</b> {fase_data['duracao']}", self.styles['CustomNormal']))

                if fase_data.get('objetivos'):
                    story.append(Paragraph("<b>Objetivos:</b>", self.styles['CustomNormal']))
                    for objetivo in fase_data['objetivos']:
                        story.append(Paragraph(f"• {objetivo}", self.styles['BulletList']))

                if fase_data.get('atividades'):
                    story.append(Paragraph("<b>Atividades:</b>", self.styles['CustomNormal']))
                    for atividade in fase_data['atividades']:
                        story.append(Paragraph(f"• {atividade}", self.styles['BulletList']))

                story.append(Spacer(1, 0.1*inch))

        return story

    def _build_risk_analysis_section(self, risk_data: dict) -> list:
        """Constrói seção de análise de riscos"""
        story = []

        story.append(Paragraph("ANÁLISE DE RISCOS DETALHADA", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Riscos por categoria
        categorias = ['tecnicos', 'mercado', 'financeiros', 'operacionais', 'regulatorios']

        for categoria in categorias:
            riscos_categoria = risk_data.get(f'riscos_{categoria}', [])
            if riscos_categoria:
                story.append(Paragraph(f"Riscos {categoria.title()}", self.styles['SectionHeader']))

                for risco in riscos_categoria:
                    if isinstance(risco, dict):
                        story.append(Paragraph(f"<b>{risco.get('nome', 'Risco')}:</b>", self.styles['CustomNormal']))
                        story.append(Paragraph(f"Probabilidade: {risco.get('probabilidade', 'N/A')}", self.styles['BulletList']))
                        story.append(Paragraph(f"Impacto: {risco.get('impacto', 'N/A')}", self.styles['BulletList']))
                        story.append(Paragraph(f"Mitigação: {risco.get('mitigacao', 'N/A')}", self.styles['BulletList']))
                        story.append(Spacer(1, 0.1*inch))

        # Matriz de riscos
        if risk_data.get('matriz_riscos'):
            story.append(Paragraph("Matriz de Riscos", self.styles['SectionHeader']))
            matriz = risk_data['matriz_riscos']

            story.append(Paragraph(f"Riscos Críticos: {matriz.get('criticos', 0)}", self.styles['CustomNormal']))
            story.append(Paragraph(f"Riscos Altos: {matriz.get('altos', 0)}", self.styles['CustomNormal']))
            story.append(Paragraph(f"Riscos Médios: {matriz.get('medios', 0)}", self.styles['CustomNormal']))
            story.append(Paragraph(f"Riscos Baixos: {matriz.get('baixos', 0)}", self.styles['CustomNormal']))

        return story

    def _build_conversion_arsenal_section(self, arsenal_data: dict) -> list:
        """Constrói seção do arsenal de conversão"""
        story = []

        story.append(Paragraph("ARSENAL DE CONVERSÃO", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Headlines magnéticas
        if arsenal_data.get('headlines_magneticas'):
            story.append(Paragraph("Headlines Magnéticas", self.styles['SectionHeader']))
            for headline in arsenal_data['headlines_magneticas']:
                story.append(Paragraph(f"• \"{headline}\"", self.styles['BulletList']))

        # Ofertas irresistíveis
        if arsenal_data.get('ofertas_irresistiveis'):
            story.append(Paragraph("Ofertas Irresistíveis", self.styles['SectionHeader']))
            for oferta in arsenal_data['ofertas_irresistiveis']:
                if isinstance(oferta, dict):
                    story.append(Paragraph(f"<b>{oferta.get('nome', 'Oferta')}:</b>", self.styles['CustomNormal']))
                    story.append(Paragraph(f"Estrutura: {oferta.get('estrutura', 'N/A')}", self.styles['BulletList']))
                    story.append(Paragraph(f"Valor Percebido: {oferta.get('valor_percebido', 'N/A')}", self.styles['BulletList']))

        # CTAs otimizadas
        if arsenal_data.get('ctas_otimizadas'):
            story.append(Paragraph("CTAs Otimizadas", self.styles['SectionHeader']))
            for cta in arsenal_data['ctas_otimizadas']:
                story.append(Paragraph(f"• \"{cta}\"", self.styles['BulletList']))

        return story

    def _build_sales_funnel_section(self, funnel_data: dict) -> list:
        """Constrói seção do funil de vendas"""
        story = []

        story.append(Paragraph("FUNIL DE VENDAS OTIMIZADO", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Etapas do funil
        etapas = ['topo', 'meio', 'fundo', 'conversao', 'retencao']

        for etapa in etapas:
            etapa_data = funnel_data.get(etapa, {})
            if etapa_data:
                story.append(Paragraph(f"{etapa.title()} do Funil", self.styles['SectionHeader']))

                if etapa_data.get('objetivo'):
                    story.append(Paragraph(f"<b>Objetivo:</b> {etapa_data['objetivo']}", self.styles['CustomNormal']))

                if etapa_data.get('estrategias'):
                    story.append(Paragraph("<b>Estratégias:</b>", self.styles['CustomNormal']))
                    for estrategia in etapa_data['estrategias']:
                        story.append(Paragraph(f"• {estrategia}", self.styles['BulletList']))

                if etapa_data.get('metricas'):
                    story.append(Paragraph("<b>Métricas:</b>", self.styles['CustomNormal']))
                    for metrica, valor in etapa_data['metricas'].items():
                        story.append(Paragraph(f"• {metrica}: {valor}", self.styles['BulletList']))

                story.append(Spacer(1, 0.1*inch))

        return story

    def _build_monitoring_section(self, monitoring_data: dict) -> list:
        """Constrói seção de monitoramento"""
        story = []

        story.append(Paragraph("SISTEMA DE MONITORAMENTO", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Dashboard principal
        if monitoring_data.get('dashboard_principal'):
            story.append(Paragraph("Dashboard Principal", self.styles['SectionHeader']))
            dashboard = monitoring_data['dashboard_principal']

            if dashboard.get('metricas_criticas'):
                story.append(Paragraph("<b>Métricas Críticas:</b>", self.styles['CustomNormal']))
                for metrica in dashboard['metricas_criticas']:
                    story.append(Paragraph(f"• {metrica}", self.styles['BulletList']))

        # Alertas automáticos
        if monitoring_data.get('alertas_automaticos'):
            story.append(Paragraph("Alertas Automáticos", self.styles['SectionHeader']))
            for alerta in monitoring_data['alertas_automaticos']:
                if isinstance(alerta, dict):
                    story.append(Paragraph(f"<b>{alerta.get('nome', 'Alerta')}:</b>", self.styles['CustomNormal']))
                    story.append(Paragraph(f"Condição: {alerta.get('condicao', 'N/A')}", self.styles['BulletList']))
                    story.append(Paragraph(f"Ação: {alerta.get('acao', 'N/A')}", self.styles['BulletList']))

        # Relatórios periódicos
        if monitoring_data.get('relatorios_periodicos'):
            story.append(Paragraph("Relatórios Periódicos", self.styles['SectionHeader']))
            relatorios = monitoring_data['relatorios_periodicos']

            for frequencia, conteudo in relatorios.items():
                story.append(Paragraph(f"<b>{frequencia.title()}:</b> {conteudo}", self.styles['CustomNormal']))

        return story

    def _build_timeline_section(self, timeline_data: dict) -> list:
        """Constrói seção do cronograma"""
        story = []

        story.append(Paragraph("CRONOGRAMA DE IMPLEMENTAÇÃO", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Timeline por mês
        if timeline_data.get('cronograma_mensal'):
            story.append(Paragraph("Cronograma Mensal", self.styles['SectionHeader']))

            cronograma = timeline_data['cronograma_mensal']
            for mes, atividades in cronograma.items():
                story.append(Paragraph(f"<b>{mes}:</b>", self.styles['CustomNormal']))
                if isinstance(atividades, list):
                    for atividade in atividades:
                        story.append(Paragraph(f"• {atividade}", self.styles['BulletList']))
                else:
                    story.append(Paragraph(f"• {atividades}", self.styles['BulletList']))
                story.append(Spacer(1, 0.1*inch))

        # Marcos importantes
        if timeline_data.get('marcos_importantes'):
            story.append(Paragraph("Marcos Importantes", self.styles['SectionHeader']))
            for marco in timeline_data['marcos_importantes']:
                if isinstance(marco, dict):
                    story.append(Paragraph(f"<b>{marco.get('data', 'Data')}:</b> {marco.get('evento', 'Evento')}", self.styles['CustomNormal']))
                else:
                    story.append(Paragraph(f"• {marco}", self.styles['BulletList']))

        return story

    def _build_forensic_section(self, forensic_data: dict) -> list:
        """Constrói seção de análise forense"""
        story = []

        story.append(Paragraph("ANÁLISE FORENSE", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Análise de CPL
        if forensic_data.get('analise_cpl'):
            story.append(Paragraph("Análise de CPL", self.styles['SectionHeader']))
            cpl = forensic_data['analise_cpl']

            if cpl.get('elementos_criticos'):
                story.append(Paragraph("<b>Elementos Críticos:</b>", self.styles['CustomNormal']))
                for elemento in cpl['elementos_criticos']:
                    story.append(Paragraph(f"• {elemento}", self.styles['BulletList']))

        # Padrões identificados
        if forensic_data.get('padroes_identificados'):
            story.append(Paragraph("Padrões Identificados", self.styles['SectionHeader']))
            for padrao in forensic_data['padroes_identificados']:
                story.append(Paragraph(f"• {padrao}", self.styles['BulletList']))

        return story

    def _build_reverse_engineering_section(self, reverse_data: dict) -> list:
        """Constrói seção de engenharia reversa"""
        story = []

        story.append(Paragraph("ENGENHARIA REVERSA VISCERAL", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Anatomia do sucesso
        if reverse_data.get('anatomia_sucesso'):
            story.append(Paragraph("Anatomia do Sucesso", self.styles['SectionHeader']))
            anatomia = reverse_data['anatomia_sucesso']

            for componente, descricao in anatomia.items():
                story.append(Paragraph(f"<b>{componente.replace('_', ' ').title()}:</b> {descricao}", self.styles['CustomNormal']))

        # Fórmulas extraídas
        if reverse_data.get('formulas_extraidas'):
            story.append(Paragraph("Fórmulas Extraídas", self.styles['SectionHeader']))
            for formula in reverse_data['formulas_extraidas']:
                story.append(Paragraph(f"• {formula}", self.styles['BulletList']))

        return story

    def _build_mental_drivers_arsenal_section(self, arsenal_data: dict) -> list:
        """Constrói seção do arsenal de drivers mentais"""
        story = []

        story.append(Paragraph("ARSENAL DE DRIVERS MENTAIS", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Sistema completo
        if arsenal_data.get('sistema_completo'):
            sistema = arsenal_data['sistema_completo']

            if sistema.get('drivers_primarios'):
                story.append(Paragraph("Drivers Primários", self.styles['SectionHeader']))
                for driver in sistema['drivers_primarios']:
                    if isinstance(driver, dict):
                        story.append(Paragraph(f"<b>{driver.get('nome', 'Driver')}:</b>", self.styles['CustomNormal']))
                        story.append(Paragraph(f"Gatilho: {driver.get('gatilho', 'N/A')}", self.styles['BulletList']))
                        story.append(Paragraph(f"Aplicação: {driver.get('aplicacao', 'N/A')}", self.styles['BulletList']))

        return story

    def _build_visual_proofs_arsenal_section(self, arsenal_data: dict) -> list:
        """Constrói seção do arsenal de provas visuais"""
        story = []

        story.append(Paragraph("ARSENAL DE PROVAS VISUAIS", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Provas por categoria
        if arsenal_data.get('provas_por_categoria'):
            categorias = arsenal_data['provas_por_categoria']

            for categoria, provas in categorias.items():
                story.append(Paragraph(f"Provas {categoria.title()}", self.styles['SectionHeader']))

                for prova in provas:
                    if isinstance(prova, dict):
                        story.append(Paragraph(f"<b>{prova.get('nome', 'Prova')}:</b>", self.styles['CustomNormal']))
                        story.append(Paragraph(f"Tipo: {prova.get('tipo', 'N/A')}", self.styles['BulletList']))
                        story.append(Paragraph(f"Impacto: {prova.get('impacto', 'N/A')}", self.styles['BulletList']))
                    else:
                        story.append(Paragraph(f"• {prova}", self.styles['BulletList']))

        return story

    def _build_final_recommendations_section(self, analysis_data: dict) -> list:
        """Constrói seção de recomendações finais"""
        story = []

        story.append(Paragraph("RECOMENDAÇÕES FINAIS", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Próximos passos
        story.append(Paragraph("Próximos Passos Imediatos", self.styles['SectionHeader']))

        proximos_passos = [
            "Implementar o avatar ultra-detalhado em todas as comunicações",
            "Aplicar os drivers mentais customizados nas páginas de vendas",
            "Executar as provas visuais sugeridas para validação",
            "Configurar o sistema anti-objeção nos pontos críticos",
            "Implementar o pré-pitch invisível no processo de vendas",
            "Monitorar as métricas de performance estabelecidas",
            "Ajustar estratégias baseadas nos resultados iniciais"
        ]

        for passo in proximos_passos:
            story.append(Paragraph(f"• {passo}", self.styles['BulletList']))

        story.append(Spacer(1, 0.2*inch))

        # Considerações importantes
        story.append(Paragraph("Considerações Importantes", self.styles['SectionHeader']))

        consideracoes = [
            "Este relatório representa uma análise baseada em dados disponíveis publicamente",
            "Os resultados podem variar baseados na execução e fatores de mercado",
            "Recomenda-se teste A/B para validar estratégias propostas",
            "Acompanhamento contínuo é essencial para otimização de resultados",
            "Adaptações podem ser necessárias baseadas em feedback do mercado"
        ]

        for consideracao in consideracoes:
            story.append(Paragraph(f"• {consideracao}", self.styles['BulletList']))

        story.append(Spacer(1, 0.3*inch))

        # Rodapé final
        story.append(Paragraph("Este relatório foi gerado pelo ARQV30 Enhanced v2.0", self.styles['CustomNormal']))
        story.append(Paragraph("Para suporte e atualizações, consulte a documentação oficial.", self.styles['CustomNormal']))

        return story

    def _build_emerging_trends_section(self, trends_data: dict) -> list:
        """Constrói seção de tendências emergentes"""
        story = []

        story.append(Paragraph("ANÁLISE DE TENDÊNCIAS EMERGENTES", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Macro tendências
        story.append(Paragraph("Macro Tendências", self.styles['SectionHeader']))
        macro_trends = [
            "Economia circular e sustentabilidade",
            "Personalização em massa",
            "Inteligência artificial aplicada",
            "Experiências imersivas (AR/VR)",
            "Modelo subscription economy",
            "Health & wellness tech"
        ]

        for trend in macro_trends:
            story.append(Paragraph(f"• {trend}", self.styles['BulletList']))

        # Micro tendências específicas
        story.append(Paragraph("Micro Tendências Específicas do Segmento", self.styles['SectionHeader']))
        micro_trends = trends_data.get('micro_tendencias', [
            "Democratização da nutrição personalizada",
            "Gamificação de hábitos alimentares",
            "Transparência radical nos ingredientes",
            "Comunidades de apoio digital",
            "Entrega ultra-rápida de refeições"
        ])

        for trend in micro_trends:
            story.append(Paragraph(f"• {trend}", self.styles['BulletList']))

        return story

    def _build_niche_opportunities_section(self, opportunities_data: dict) -> list:
        """Constrói seção de oportunidades de nicho"""
        story = []

        story.append(Paragraph("OPORTUNIDADES DE NICHO", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Nichos emergentes
        story.append(Paragraph("Nichos Emergentes Identificados", self.styles['SectionHeader']))
        nichos = opportunities_data.get('nichos_emergentes', [
            "Nutrição para profissionais de e-sports",
            "Dietas adaptadas para trabalho remoto",
            "Alimentação funcional para terceira idade",
            "Nutrição personalizada por genética",
            "Dietas plant-based premium"
        ])

        for nicho in nichos:
            story.append(Paragraph(f"• {nicho}", self.styles['BulletList']))

        # Análise de potencial
        story.append(Paragraph("Análise de Potencial de Mercado", self.styles['SectionHeader']))

        niches_table_data = [
            ['Nicho', 'Potencial', 'Competição', 'Investimento'],
            ['Nutrição E-sports', 'Alto', 'Baixa', 'Médio'],
            ['Work From Home Diet', 'Muito Alto', 'Média', 'Baixo'],
            ['Nutrição Geriátrica', 'Alto', 'Baixa', 'Alto'],
            ['Nutrigenômica', 'Muito Alto', 'Baixa', 'Muito Alto']
        ]

        niches_table = Table(niches_table_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch])
        niches_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(niches_table)

        return story

    def _build_pricing_strategy_section(self, pricing_data: dict) -> list:
        """Constrói seção de estratégia de pricing"""
        story = []

        story.append(Paragraph("ESTRATÉGIA DE PRICING DINÂMICO", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Modelos de pricing
        story.append(Paragraph("Modelos de Precificação Recomendados", self.styles['SectionHeader']))

        pricing_models = [
            "Freemium com upgrade progressivo",
            "Tiered pricing baseado em features",
            "Value-based pricing por resultados",
            "Subscription com desconto anual",
            "Pay-per-use para serviços premium"
        ]

        for model in pricing_models:
            story.append(Paragraph(f"• {model}", self.styles['BulletList']))

        # Matriz de preços
        story.append(Paragraph("Matriz de Preços Sugerida", self.styles['SectionHeader']))

        pricing_table_data = [
            ['Plano', 'Preço Mensal', 'Features', 'Target'],
            ['Básico', 'R$ 47', 'Acesso básico + 1 consulta', 'Iniciantes'],
            ['Pro', 'R$ 97', 'Acesso completo + 3 consultas', 'Entusiastas'],
            ['Premium', 'R$ 197', 'Tudo + coaching personalizado', 'Sérios'],
            ['VIP', 'R$ 497', 'Tudo + acompanhamento 1:1', 'Executivos']
        ]

        pricing_table = Table(pricing_table_data, colWidths=[1.2*inch, 1.2*inch, 2*inch, 1.2*inch])
        pricing_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(pricing_table)

        return story

    def _build_customer_journey_section(self, journey_data: dict) -> list:
        """Constrói seção de customer journey"""
        story = []

        story.append(Paragraph("CUSTOMER JOURNEY MAPPING", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Fases do journey
        fases = [
            {
                'nome': 'Consciência',
                'touchpoints': ['Redes sociais', 'Busca orgânica', 'Indicações'],
                'emocoes': ['Curiosidade', 'Ceticismo inicial'],
                'acoes': ['Pesquisa sobre o problema', 'Consome conteúdo educativo']
            },
            {
                'nome': 'Consideração',
                'touchpoints': ['Site', 'Blog', 'Webinars'],
                'emocoes': ['Interesse crescente', 'Comparação'],
                'acoes': ['Baixa materiais gratuitos', 'Compara soluções']
            },
            {
                'nome': 'Decisão',
                'touchpoints': ['Landing page', 'Chat', 'Demonstração'],
                'emocoes': ['Urgência', 'Confiança'],
                'acoes': ['Solicita demonstração', 'Negocia condições']
            },
            {
                'nome': 'Compra',
                'touchpoints': ['Checkout', 'Email', 'Onboarding'],
                'emocoes': ['Expectativa', 'Ansiedade'],
                'acoes': ['Finaliza compra', 'Inicia uso']
            },
            {
                'nome': 'Pós-compra',
                'touchpoints': ['App', 'Suporte', 'Comunidade'],
                'emocoes': ['Satisfação', 'Lealdade'],
                'acoes': ['Usa regularmente', 'Recomenda para outros']
            }
        ]

        for fase in fases:
            story.append(Paragraph(f"Fase: {fase['nome']}", self.styles['SectionHeader']))

            story.append(Paragraph("<b>Touchpoints:</b>", self.styles['CustomNormal']))
            for touchpoint in fase['touchpoints']:
                story.append(Paragraph(f"• {touchpoint}", self.styles['BulletList']))

            story.append(Paragraph(f"<b>Emoções:</b> {', '.join(fase['emocoes'])}", self.styles['CustomNormal']))

            story.append(Paragraph("<b>Ações:</b>", self.styles['CustomNormal']))
            for acao in fase['acoes']:
                story.append(Paragraph(f"• {acao}", self.styles['BulletList']))

            story.append(Spacer(1, 0.1*inch))

        return story

    def _build_content_strategy_section(self, content_data: dict) -> list:
        """Constrói seção de estratégia de conteúdo"""
        story = []

        story.append(Paragraph("ESTRATÉGIA DE CONTEÚDO", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Calendário editorial
        story.append(Paragraph("Calendário Editorial Estratégico", self.styles['SectionHeader']))

        content_calendar = [
            ['Semana', 'Tema Principal', 'Formato', 'Canal'],
            ['1', 'Fundamentos da dieta', 'Blog post + Infográfico', 'Site + Instagram'],
            ['2', 'Receitas práticas', 'Vídeo + PDF', 'YouTube + Email'],
            ['3', 'Casos de sucesso', 'Depoimentos + Stories', 'Instagram + LinkedIn'],
            ['4', 'Dicas de especialista', 'Live + Q&A', 'Instagram + YouTube']
        ]

        calendar_table = Table(content_calendar, colWidths=[1*inch, 2*inch, 1.5*inch, 1.5*inch])
        calendar_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(calendar_table)

        # Tipos de conteúdo
        story.append(Paragraph("Tipos de Conteúdo por Funil", self.styles['SectionHeader']))

        content_types = [
            "Topo: Artigos educativos, infográficos, pesquisas",
            "Meio: Ebooks, webinars, cases, comparativos",
            "Fundo: Demos, trials, depoimentos, ofertas especiais"
        ]

        for content_type in content_types:
            story.append(Paragraph(f"• {content_type}", self.styles['BulletList']))

        return story

    def _build_influencers_section(self, influencers_data: dict) -> list:
        """Constrói seção de análise de influenciadores"""
        story = []

        story.append(Paragraph("ESTRATÉGIA DE INFLUENCIADORES", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Perfis de influenciadores
        story.append(Paragraph("Perfis de Influenciadores Target", self.styles['SectionHeader']))

        influencer_profiles = [
            {
                'categoria': 'Micro-influenciadores de Nutrição',
                'followers': '10K - 100K',
                'engagement': '3-8%',
                'investimento': 'R$ 500-2.000'
            },
            {
                'categoria': 'Nutricionistas Especialistas',
                'followers': '50K - 500K',
                'engagement': '2-5%',
                'investimento': 'R$ 2.000-10.000'
            },
            {
                'categoria': 'Lifestyle Influencers',
                'followers': '100K - 1M',
                'engagement': '1-3%',
                'investimento': 'R$ 5.000-50.000'
            }
        ]

        for profile in influencer_profiles:
            story.append(Paragraph(f"<b>{profile['categoria']}</b>", self.styles['CustomNormal']))
            story.append(Paragraph(f"Seguidores: {profile['followers']}", self.styles['BulletList']))
            story.append(Paragraph(f"Engagement: {profile['engagement']}", self.styles['BulletList']))
            story.append(Paragraph(f"Investimento: {profile['investimento']}", self.styles['BulletList']))
            story.append(Spacer(1, 0.1*inch))

        return story

    def _build_partnerships_section(self, partnerships_data: dict) -> list:
        """Constrói seção de estratégia de parcerias"""
        story = []

        story.append(Paragraph("ESTRATÉGIA DE PARCERIAS", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Tipos de parcerias
        story.append(Paragraph("Oportunidades de Parcerias Estratégicas", self.styles['SectionHeader']))

        partnerships = [
            "Clínicas e consultórios médicos",
            "Academias e estúdios de fitness",
            "Empresas de delivery de alimentos",
            "Aplicativos de saúde e bem-estar",
            "Farmácias e drogarias",
            "Empresas de suplementação",
            "Programas corporativos de wellness"
        ]

        for partnership in partnerships:
            story.append(Paragraph(f"• {partnership}", self.styles['BulletList']))

        # Modelo de parceria
        story.append(Paragraph("Modelos de Parceria Recomendados", self.styles['SectionHeader']))

        partnership_models = [
            "Revenue sharing: 15-30% por venda gerada",
            "Comissão fixa: R$ 50-200 por cliente",
            "Licenciamento de conteúdo: R$ 5.000-20.000/mês",
            "Co-marketing: Investimento compartilhado",
            "White label: Personalização da solução"
        ]

        for model in partnership_models:
            story.append(Paragraph(f"• {model}", self.styles['BulletList']))

        return story

    def _build_seasonality_section(self, seasonality_data: dict) -> list:
        """Constrói seção de análise de sazonalidade"""
        story = []

        story.append(Paragraph("ANÁLISE DE SAZONALIDADE", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Picos sazonais
        story.append(Paragraph("Picos de Demanda Identificados", self.styles['SectionHeader']))

        seasonal_peaks = [
            "Janeiro: Resoluções de ano novo (+150%)",
            "Maio-Junho: Projeto verão (+120%)",
            "Setembro: Volta às aulas (+80%)",
            "Novembro: Black Friday (+200%)",
            "Dezembro: Preparação para festas (+60%)"
        ]

        for peak in seasonal_peaks:
            story.append(Paragraph(f"• {peak}", self.styles['BulletList']))

        # Estratégias por época
        story.append(Paragraph("Estratégias por Período", self.styles['SectionHeader']))

        seasonal_strategies = [
            "Q1: Campanha 'Novo Eu' com descontos progressivos",
            "Q2: Foco em resultados rápidos para verão",
            "Q3: Volta à rotina com hábitos sustentáveis",
            "Q4: Ofertas especiais e preparação para próximo ano"
        ]

        for strategy in seasonal_strategies:
            story.append(Paragraph(f"• {strategy}", self.styles['BulletList']))

        return story

    def _build_retention_strategy_section(self, retention_data: dict) -> list:
        """Constrói seção de estratégia de retenção"""
        story = []

        story.append(Paragraph("ESTRATÉGIA DE RETENÇÃO", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Métricas de retenção
        story.append(Paragraph("Métricas de Retenção Target", self.styles['SectionHeader']))

        retention_metrics = [
            "Day 1 Retention: 85%",
            "Day 7 Retention: 65%", 
            "Day 30 Retention: 45%",
            "Month 3 Retention: 30%",
            "Month 6 Retention: 25%",
            "Annual Retention: 20%"
        ]

        for metric in retention_metrics:
            story.append(Paragraph(f"• {metric}", self.styles['BulletList']))

        # Táticas de retenção
        story.append(Paragraph("Táticas de Retenção por Período", self.styles['SectionHeader']))

        retention_tactics = [
            "Primeiros 7 dias: Onboarding intensivo + check-ins diários",
            "Semanas 2-4: Gamificação + desafios semanais",
            "Meses 2-3: Conteúdo exclusivo + comunidade",
            "Meses 4-6: Programa de fidelidade + upgrades",
            "6+ meses: Ambassador program + benefícios VIP"
        ]

        for tactic in retention_tactics:
            story.append(Paragraph(f"• {tactic}", self.styles['BulletList']))

        return story

    def _build_roi_by_channel_section(self, roi_data: dict) -> list:
        """Constrói seção de ROI por canal"""
        story = []

        story.append(Paragraph("ANÁLISE DE ROI POR CANAL", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # ROI por canal
        story.append(Paragraph("Performance Esperada por Canal", self.styles['SectionHeader']))

        roi_table_data = [
            ['Canal', 'Investimento', 'ROI Esperado', 'Payback', 'LTV/CAC'],
            ['Google Ads', 'R$ 10.000', '300%', '3 meses', '4.2x'],
            ['Facebook Ads', 'R$ 8.000', '250%', '4 meses', '3.8x'],
            ['Instagram Organic', 'R$ 3.000', '400%', '6 meses', '5.1x'],
            ['Email Marketing', 'R$ 1.000', '800%', '2 meses', '8.2x'],
            ['Influencers', 'R$ 15.000', '200%', '5 meses', '3.2x'],
            ['SEO/Content', 'R$ 5.000', '500%', '8 meses', '6.5x']
        ]

        roi_table = Table(roi_table_data, colWidths=[1.2*inch, 1*inch, 1*inch, 0.8*inch, 0.8*inch])
        roi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(roi_table)

        return story

    def _build_competitive_benchmark_section(self, analysis_data: dict) -> list:
        """Constrói seção de benchmark competitivo"""
        story = []

        story.append(Paragraph("BENCHMARK COMPETITIVO DETALHADO", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Matriz competitiva
        story.append(Paragraph("Matriz de Posicionamento Competitivo", self.styles['SectionHeader']))

        competitive_matrix = [
            ['Critério', 'Nosso Produto', 'Concorrente A', 'Concorrente B', 'Concorrente C'],
            ['Preço', '⭐⭐⭐⭐', '⭐⭐', '⭐⭐⭐⭐⭐', '⭐⭐⭐'],
            ['Qualidade', '⭐⭐⭐⭐⭐', '⭐⭐⭐', '⭐⭐⭐⭐', '⭐⭐⭐⭐'],
            ['Inovação', '⭐⭐⭐⭐⭐', '⭐⭐', '⭐⭐⭐', '⭐⭐⭐⭐'],
            ['Marketing', '⭐⭐⭐⭐', '⭐⭐⭐⭐⭐', '⭐⭐⭐', '⭐⭐⭐⭐'],
            ['Suporte', '⭐⭐⭐⭐⭐', '⭐⭐⭐', '⭐⭐⭐⭐', '⭐⭐⭐']
        ]

        matrix_table = Table(competitive_matrix, colWidths=[1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
        matrix_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(matrix_table)

        return story

    def _build_swot_analysis_section(self, analysis_data: dict) -> list:
        """Constrói seção de análise SWOT"""
        story = []

        story.append(Paragraph("ANÁLISE SWOT EXPANDIDA", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Forças
        story.append(Paragraph("Forças (Strengths)", self.styles['SectionHeader']))
        strengths = [
            "Equipe especializada em nutrição",
            "Tecnologia proprietária avançada",
            "Base de conhecimento científico sólida",
            "Parcerias estratégicas estabelecidas",
            "Marca diferenciada no mercado"
        ]
        for strength in strengths:
            story.append(Paragraph(f"• {strength}", self.styles['BulletList']))

        # Fraquezas
        story.append(Paragraph("Fraquezas (Weaknesses)", self.styles['SectionHeader']))
        weaknesses = [
            "Capital limitado para marketing",
            "Equipe ainda pequena",
            "Dependência de poucos fornecedores",
            "Processo de onboarding complexo",
            "Falta de presença internacional"
        ]
        for weakness in weaknesses:
            story.append(Paragraph(f"• {weakness}", self.styles['BulletList']))

        # Oportunidades
        story.append(Paragraph("Oportunidades (Opportunities)", self.styles['SectionHeader']))
        opportunities = [
            "Crescimento do mercado de wellness",
            "Aumento da consciência sobre saúde",
            "Digitalização acelerada pós-pandemia",
            "Novos nichos emergentes",
            "Possibilidade de expansão internacional"
        ]
        for opportunity in opportunities:
            story.append(Paragraph(f"• {opportunity}", self.styles['BulletList']))

        # Ameaças
        story.append(Paragraph("Ameaças (Threats)", self.styles['SectionHeader']))
        threats = [
            "Entrada de grandes players",
            "Mudanças na regulamentação",
            "Saturação do mercado",
            "Recessão econômica",
            "Mudanças nos padrões de consumo"
        ]
        for threat in threats:
            story.append(Paragraph(f"• {threat}", self.styles['BulletList']))

        return story

    def _build_scalability_strategy_section(self, analysis_data: dict) -> list:
        """Constrói seção de estratégia de escalabilidade"""
        story = []

        story.append(Paragraph("ESTRATÉGIA DE ESCALABILIDADE", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Fases de crescimento
        story.append(Paragraph("Fases de Crescimento Planejadas", self.styles['SectionHeader']))

        growth_phases = [
            {
                'fase': 'Fase 1: Validação (0-1K usuários)',
                'foco': 'Product-market fit e otimização inicial',
                'investimento': 'R$ 50.000',
                'timeline': '6 meses'
            },
            {
                'fase': 'Fase 2: Tração (1K-10K usuários)',
                'foco': 'Crescimento sustentável e automação',
                'investimento': 'R$ 200.000',
                'timeline': '12 meses'
            },
            {
                'fase': 'Fase 3: Expansão (10K-100K usuários)',
                'foco': 'Escala nacional e novos produtos',
                'investimento': 'R$ 1.000.000',
                'timeline': '18 meses'
            }
        ]

        for phase in growth_phases:
            story.append(Paragraph(f"<b>{phase['fase']}</b>", self.styles['CustomNormal']))
            story.append(Paragraph(f"Foco: {phase['foco']}", self.styles['BulletList']))
            story.append(Paragraph(f"Investimento: {phase['investimento']}", self.styles['BulletList']))
            story.append(Paragraph(f"Timeline: {phase['timeline']}", self.styles['BulletList']))
            story.append(Spacer(1, 0.1*inch))

        return story

    def _build_social_impact_section(self, analysis_data: dict) -> list:
        """Constrói seção de impacto social"""
        story = []

        story.append(Paragraph("ANÁLISE DE IMPACTO SOCIAL", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Impactos positivos
        story.append(Paragraph("Impactos Sociais Positivos", self.styles['SectionHeader']))
        social_impacts = [
            "Melhoria da saúde pública através da educação nutricional",
            "Redução de custos do sistema de saúde",
            "Democratização do acesso à orientação nutricional",
            "Promoção de hábitos alimentares sustentáveis",
            "Geração de empregos especializados"
        ]
        for impact in social_impacts:
            story.append(Paragraph(f"• {impact}", self.styles['BulletList']))

        # Métricas de impacto
        story.append(Paragraph("Métricas de Impacto Mensuráveis", self.styles['SectionHeader']))
        impact_metrics = [
            "Vidas impactadas positivamente: Meta de 50.000 em 3 anos",
            "Redução média de 15% no IMC dos usuários",
            "90% dos usuários relatam melhoria na qualidade de vida",
            "Economia de R$ 2.000/ano em gastos médicos por usuário",
            "Redução de 25% no desperdício alimentar"
        ]
        for metric in impact_metrics:
            story.append(Paragraph(f"• {metric}", self.styles['BulletList']))

        return story

    def _build_innovation_strategy_section(self, analysis_data: dict) -> list:
        """Constrói seção de estratégia de inovação"""
        story = []

        story.append(Paragraph("ESTRATÉGIA DE INOVAÇÃO", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Roadmap de inovação
        story.append(Paragraph("Roadmap de Inovação", self.styles['SectionHeader']))
        innovation_roadmap = [
            "Q1 2025: IA para recomendações personalizadas",
            "Q2 2025: Integração com wearables e IoT",
            "Q3 2025: Análise nutricional por foto",
            "Q4 2025: Marketplace de produtos saudáveis",
            "Q1 2026: Realidade aumentada para educação nutricional"
        ]
        for item in innovation_roadmap:
            story.append(Paragraph(f"• {item}", self.styles['BulletList']))

        # Parcerias de P&D
        story.append(Paragraph("Parcerias de Pesquisa e Desenvolvimento", self.styles['SectionHeader']))
        rd_partnerships = [
            "Universidades: USP, UNICAMP para pesquisa nutricional",
            "Institutos de tecnologia: Desenvolvimento de IA",
            "Laboratórios: Validação científica de metodologias",
            "Startups: Integração de tecnologias emergentes"
        ]
        for partnership in rd_partnerships:
            story.append(Paragraph(f"• {partnership}", self.styles['BulletList']))

        return story

    def _build_contingency_plan_section(self, analysis_data: dict) -> list:
        """Constrói seção de plano de contingência"""
        story = []

        story.append(Paragraph("PLANO DE CONTINGÊNCIA", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Cenários de risco
        story.append(Paragraph("Cenários de Risco e Respostas", self.styles['SectionHeader']))

        risk_scenarios = [
            {
                'cenario': 'Entrada de grande concorrente',
                'probabilidade': 'Alta',
                'resposta': 'Acelerar diferenciação e parcerias exclusivas'
            },
            {
                'cenario': 'Mudança regulatória restritiva',
                'probabilidade': 'Média',
                'resposta': 'Compliance antecipado e lobby setorial'
            },
            {
                'cenario': 'Crise econômica severa',
                'probabilidade': 'Média',
                'resposta': 'Redução de custos e foco em ROI'
            },
            {
                'cenario': 'Problema de segurança de dados',
                'probabilidade': 'Baixa',
                'resposta': 'Protocolo de resposta a incidentes'
            }
        ]

        for scenario in risk_scenarios:
            story.append(Paragraph(f"<b>Cenário:</b> {scenario['cenario']}", self.styles['CustomNormal']))
            story.append(Paragraph(f"Probabilidade: {scenario['probabilidade']}", self.styles['BulletList']))
            story.append(Paragraph(f"Resposta: {scenario['resposta']}", self.styles['BulletList']))
            story.append(Spacer(1, 0.1*inch))

        return story

    def _build_sustainability_section(self, analysis_data: dict) -> list:
        """Constrói seção de sustentabilidade"""
        story = []

        story.append(Paragraph("ANÁLISE DE SUSTENTABILIDADE", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Práticas sustentáveis
        story.append(Paragraph("Práticas de Sustentabilidade", self.styles['SectionHeader']))
        sustainability_practices = [
            "Promoção de dietas baseadas em plantas",
            "Redução do desperdício alimentar",
            "Parcerias com produtores locais",
            "Operação 100% digital (paperless)",
            "Compensação de carbono das operações"
        ]
        for practice in sustainability_practices:
            story.append(Paragraph(f"• {practice}", self.styles['BulletList']))

        # Metas ESG
        story.append(Paragraph("Metas ESG (Environmental, Social, Governance)", self.styles['SectionHeader']))
        esg_goals = [
            "Carbono neutro até 2026",
            "50% da equipe de grupos sub-representados",
            "Governança transparente com relatórios trimestrais",
            "Auditoria anual de práticas sustentáveis",
            "Certificações B-Corp até 2025"
        ]
        for goal in esg_goals:
            story.append(Paragraph(f"• {goal}", self.styles['BulletList']))

        return story

    def _build_technology_roadmap_section(self, analysis_data: dict) -> list:
        """Constrói seção de roadmap tecnológico"""
        story = []

        story.append(Paragraph("ROADMAP DE TECNOLOGIA", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Stack tecnológico atual
        story.append(Paragraph("Stack Tecnológico Atual", self.styles['SectionHeader']))
        current_stack = [
            "Frontend: React.js, TypeScript, Material-UI",
            "Backend: Python, FastAPI, PostgreSQL",
            "IA/ML: TensorFlow, scikit-learn, OpenAI API",
            "Cloud: AWS, Docker, Kubernetes",
            "Analytics: Google Analytics, Mixpanel"
        ]
        for tech in current_stack:
            story.append(Paragraph(f"• {tech}", self.styles['BulletList']))

        # Evolução planejada
        story.append(Paragraph("Evolução Tecnológica Planejada", self.styles['SectionHeader']))
        tech_evolution = [
            "2025 Q1: Migração para microserviços",
            "2025 Q2: Implementação de GraphQL",
            "2025 Q3: Machine Learning próprio",
            "2025 Q4: App móvel nativo",
            "2026 Q1: Blockchain para certificações"
        ]
        for evolution in tech_evolution:
            story.append(Paragraph(f"• {evolution}", self.styles['BulletList']))

        return story

    def _build_internationalization_section(self, analysis_data: dict) -> list:
        """Constrói seção de estratégia de internacionalização"""
        story = []

        story.append(Paragraph("ESTRATÉGIA DE INTERNACIONALIZAÇÃO", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Mercados prioritários
        story.append(Paragraph("Mercados Prioritários para Expansão", self.styles['SectionHeader']))
        target_markets = [
            "América Latina: Argentina, Chile, Colômbia (Fase 1)",
            "América do Norte: Estados Unidos, Canadá (Fase 2)",
            "Europa: Portugal, Espanha (Fase 3)",
            "Ásia-Pacífico: Austrália (Fase 4)"
        ]
        for market in target_markets:
            story.append(Paragraph(f"• {market}", self.styles['BulletList']))

        # Estratégia de entrada
        story.append(Paragraph("Estratégias de Entrada por Mercado", self.styles['SectionHeader']))
        entry_strategies = [
            "LATAM: Parcerias locais e adaptação cultural",
            "EUA: Investimento direto e equipe local",
            "Europa: Licenciamento e joint ventures",
            "APAC: Franchising e parcerias estratégicas"
        ]
        for strategy in entry_strategies:
            story.append(Paragraph(f"• {strategy}", self.styles['BulletList']))

        return story

    def _build_compliance_section(self, analysis_data: dict) -> list:
        """Constrói seção de análise de compliance"""
        story = []

        story.append(Paragraph("ANÁLISE DE COMPLIANCE", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Regulamentações aplicáveis
        story.append(Paragraph("Regulamentações Aplicáveis", self.styles['SectionHeader']))
        regulations = [
            "LGPD - Lei Geral de Proteção de Dados",
            "CFN - Conselho Federal de Nutrição",
            "ANVISA - Agência Nacional de Vigilância Sanitária",
            "CVM - Comissão de Valores Mobiliários",
            "Marco Civil da Internet"
        ]
        for regulation in regulations:
            story.append(Paragraph(f"• {regulation}", self.styles['BulletList']))

        # Protocolo de compliance
        story.append(Paragraph("Protocolo de Compliance", self.styles['SectionHeader']))
        compliance_protocol = [
            "Auditoria trimestral de práticas",
            "Treinamento anual da equipe",
            "Monitoramento contínuo de mudanças regulatórias",
            "Relatórios mensais de conformidade",
            "Canal direto para questões de compliance"
        ]
        for protocol in compliance_protocol:
            story.append(Paragraph(f"• {protocol}", self.styles['BulletList']))

        return story

    def _build_appendices_section(self, analysis_data: dict) -> list:
        """Constrói seção de apêndices"""
        story = []

        story.append(Paragraph("APÊNDICES", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Glossário
        story.append(Paragraph("Glossário de Termos", self.styles['SectionHeader']))
        glossary = [
            "CAC - Customer Acquisition Cost",
            "LTV - Lifetime Value",
            "MRR - Monthly Recurring Revenue",
            "ARR - Annual Recurring Revenue",
            "PMF - Product Market Fit",
            "CAGR - Compound Annual Growth Rate"
        ]
        for term in glossary:
            story.append(Paragraph(f"• {term}", self.styles['BulletList']))

        # Metodologia
        story.append(Paragraph("Metodologia de Análise", self.styles['SectionHeader']))
        methodology = [
            "Pesquisa web massiva com 15+ fontes",
            "Análise de tendências com IA avançada",
            "Validação cruzada de dados",
            "Modelagem preditiva baseada em machine learning",
            "Benchmarking competitivo automatizado"
        ]
        for method in methodology:
            story.append(Paragraph(f"• {method}", self.styles['BulletList']))

        # Fontes e referências
        story.append(Paragraph("Principais Fontes Consultadas", self.styles['SectionHeader']))
        sources = [
            "IBGE - Instituto Brasileiro de Geografia e Estatística",
            "Euromonitor International",
            "Statista Market Research",
            "Google Trends e Keyword Planner",
            "SimilarWeb e SEMrush",
            "Relatórios setoriais especializados"
        ]
        for source in sources:
            story.append(Paragraph(f"• {source}", self.styles['BulletList']))

        # Disclaimer
        story.append(Paragraph("Disclaimer", self.styles['SectionHeader']))
        disclaimer_text = """
        Este relatório foi gerado por inteligência artificial baseado em dados públicos disponíveis 
        na data de geração. As projeções e recomendações são estimativas baseadas em análise de 
        tendências e não constituem garantias de resultados. Recomenda-se validação adicional 
        através de pesquisa primária e consultoria especializada antes da implementação de 
        estratégias críticas de negócio.
        """
        story.append(Paragraph(disclaimer_text, self.styles['CustomNormal']))

        return story


# Instância global do gerador
pdf_generator = PDFGenerator()

@pdf_bp.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    """Gera PDF da análise"""

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'error': 'Dados não fornecidos',
                'message': 'Envie os dados da análise no corpo da requisição'
            }), 400

        # Gera PDF
        logger.info("Gerando relatório PDF...")
        pdf_buffer = pdf_generator.generate_analysis_report(data)

        # Salva arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_buffer.getvalue())
            tmp_file_path = tmp_file.name

        # Retorna arquivo
        return send_file(
            tmp_file_path,
            as_attachment=True,
            download_name=f"analise_mercado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mimetype='application/pdf'
        )

    except Exception as e:
        logger.error(f"Erro ao gerar PDF: {str(e)}")
        return jsonify({
            'error': 'Erro ao gerar PDF',
            'message': str(e)
        }), 500

@pdf_bp.route('/pdf_preview', methods=['POST'])
def pdf_preview():
    """Gera preview do PDF (metadados)"""

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'error': 'Dados não fornecidos'
            }), 400

        # Calcula estatísticas do relatório
        sections = []

        if 'avatar_ultra_detalhado' in data:
            sections.append('Avatar Ultra-Detalhado')

        if 'escopo' in data:
            sections.append('Escopo e Posicionamento')

        if 'analise_concorrencia_detalhada' in data:
            sections.append('Análise de Concorrência')

        if 'estrategia_palavras_chave' in data:
            sections.append('Estratégia de Marketing')

        if 'metricas_performance_detalhadas' in data:
            sections.append('Métricas de Performance')

        if 'projecoes_cenarios' in data:
            sections.append('Projeções e Cenários')

        if 'plano_acao_detalhado' in data:
            sections.append('Plano de Ação')

        if 'insights_exclusivos' in data:
            sections.append('Insights Exclusivos')

        if 'analise_estrutural_completa' in data:
            sections.append('Análise Estrutural Completa')

        if 'analise_viabilidade' in data:
            sections.append('Análise de Viabilidade')

        if 'roteiro_lancamento_detalhado' in data:
            sections.append('Roteiro de Lançamento Detalhado')

        if 'analise_riscos_detalhada' in data:
            sections.append('Análise de Riscos Detalhada')

        if 'arsenal_conversao' in data:
            sections.append('Arsenal de Conversão')

        if 'funil_vendas_otimizado' in data:
            sections.append('Funil de Vendas Otimizado')

        if 'sistema_monitoramento' in data:
            sections.append('Sistema de Monitoramento')

        if 'cronograma_implementacao' in data:
            sections.append('Cronograma de Implementação')

        if 'analise_forense' in data:
            sections.append('Análise Forense')

        if 'engenharia_reversa_visceral' in data:
            sections.append('Engenharia Reversa Visceral')

        if 'arsenal_drivers_mentais' in data:
            sections.append('Arsenal de Drivers Mentais')

        if 'arsenal_provas_visuais' in data:
            sections.append('Arsenal de Provas Visuais')

        if 'analise_tendencias_emergentes' in data:
            sections.append('Análise de Tendências Emergentes')

        if 'oportunidades_nicho' in data:
            sections.append('Oportunidades de Nicho')

        if 'estrategia_pricing' in data:
            sections.append('Estratégia de Pricing')

        if 'customer_journey' in data:
            sections.append('Customer Journey Mapping')

        if 'estrategia_conteudo' in data:
            sections.append('Estratégia de Conteúdo')

        if 'estrategia_influenciadores' in data:
            sections.append('Estratégia de Influenciadores')

        if 'estrategia_parcerias' in data:
            sections.append('Estratégia de Parcerias')

        if 'analise_sazonalidade' in data:
            sections.append('Análise de Sazonalidade')

        if 'estrategia_retencao' in data:
            sections.append('Estratégia de Retenção')

        if 'analise_roi_canal' in data:
            sections.append('Análise de ROI por Canal')

        if 'benchmark_competitivo' in data:
            sections.append('Benchmark Competitivo Detalhado')

        if 'analise_swot' in data:
            sections.append('Análise SWOT Expandida')

        if 'estrategia_escalabilidade' in data:
            sections.append('Estratégia de Escalabilidade')

        if 'analise_impacto_social' in data:
            sections.append('Análise de Impacto Social')

        if 'estrategia_inovacao' in data:
            sections.append('Estratégia de Inovação')

        if 'plano_contingencia' in data:
            sections.append('Plano de Contingência')

        if 'analise_sustentabilidade' in data:
            sections.append('Análise de Sustentabilidade')

        if 'roadmap_tecnologia' in data:
            sections.append('Roadmap de Tecnologia')

        if 'estrategia_internacionalizacao' in data:
            sections.append('Estratégia de Internacionalização')

        if 'analise_compliance' in data:
            sections.append('Análise de Compliance')

        if 'apendices' in data:
            sections.append('Apêndices')


        # Estima páginas
        estimated_pages = len(sections) + 2  # +2 para capa e sumário

        return jsonify({
            'sections': sections,
            'estimated_pages': estimated_pages,
            'file_size_estimate': f"{estimated_pages * 50}KB",
            'generation_time_estimate': f"{estimated_pages * 2} segundos"
        })

    except Exception as e:
        logger.error(f"Erro no preview: {str(e)}")
        return jsonify({
            'error': 'Erro ao gerar preview',
            'message': str(e)
        }), 500
