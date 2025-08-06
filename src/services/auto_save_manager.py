#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Auto Save Manager
Sistema de salvamento automático e imediato de todos os resultados
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)

class AutoSaveManager:
    """Gerenciador de salvamento automático ultra-robusto"""

    def __init__(self):
        """Inicializa o gerenciador de salvamento"""
        self.base_dir = Path("relatorios_intermediarios")
        self.base_dir.mkdir(exist_ok=True)

        # Subdiretórios para organização
        self.subdirs = {
            'pesquisa_web': self.base_dir / 'pesquisa_web',
            'drivers_mentais': self.base_dir / 'drivers_mentais',
            'provas_visuais': self.base_dir / 'provas_visuais',
            'anti_objecao': self.base_dir / 'anti_objecao',
            'pre_pitch': self.base_dir / 'pre_pitch',
            'avatar': self.base_dir / 'avatar',
            'analise_completa': self.base_dir / 'analise_completa',
            'erros': self.base_dir / 'erros',
            'logs': self.base_dir / 'logs'
        }

        # Cria todos os subdiretórios
        for subdir in self.subdirs.values():
            subdir.mkdir(exist_ok=True)

        self.session_id = None
        self.analysis_id = None

        logger.info(f"✅ Auto Save Manager inicializado: {self.base_dir}")

    def iniciar_sessao(self, session_id: str = None) -> str:
        """Inicia nova sessão de salvamento"""
        self.session_id = session_id or f"session_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        self.analysis_id = f"analysis_{int(time.time())}_{uuid.uuid4().hex[:8]}"

        # Cria diretório da sessão
        session_dir = self.base_dir / self.session_id
        session_dir.mkdir(exist_ok=True)

        # Salva metadados da sessão
        self.salvar_etapa("session_metadata", {
            "session_id": self.session_id,
            "analysis_id": self.analysis_id,
            "iniciado_em": datetime.now().isoformat(),
            "status": "iniciado"
        })

        logger.info(f"🚀 Sessão iniciada: {self.session_id}")
        return self.session_id

    def salvar_etapa(
        self,
        nome_etapa: str,
        dados: Any,
        status: str = "sucesso",
        timestamp: Optional[float] = None,
        categoria: str = "geral"
    ) -> str:
        """Salva etapa imediatamente com timestamp único"""

        timestamp = timestamp or time.time()
        timestamp_str = datetime.fromtimestamp(timestamp).strftime("%Y%m%d_%H%M%S_%f")[:-3]

        # Determina diretório baseado na categoria
        if categoria in self.subdirs:
            save_dir = self.subdirs[categoria]
        else:
            save_dir = self.base_dir

        # Se há sessão ativa, cria subdiretório
        if self.session_id:
            save_dir = save_dir / self.session_id
            save_dir.mkdir(exist_ok=True)

        # Nome do arquivo com timestamp único
        filename = f"{nome_etapa}_{timestamp_str}.json"
        filepath = save_dir / filename

        try:
            # Prepara dados para salvamento
            save_data = {
                "etapa": nome_etapa,
                "status": status,
                "dados": dados,
                "timestamp": timestamp,
                "timestamp_iso": datetime.fromtimestamp(timestamp).isoformat(),
                "session_id": self.session_id,
                "analysis_id": self.analysis_id,
                "categoria": categoria,
                "tamanho_dados": len(str(dados)) if dados else 0
            }

            # Salva arquivo JSON
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2, default=str)

            # Log de sucesso
            logger.info(f"💾 Etapa '{nome_etapa}' salva: {filepath}")

            # Salva também um backup compactado se dados grandes
            if len(str(dados)) > 50000:  # > 50KB
                self._salvar_backup_compactado(filepath, save_data)

            return str(filepath)

        except Exception as e:
            # Salvamento de emergência em caso de erro
            emergency_path = self.base_dir / f"EMERGENCY_{nome_etapa}_{timestamp_str}.txt"
            try:
                with open(emergency_path, "w", encoding="utf-8") as f:
                    f.write(f"ERRO AO SALVAR: {str(e)}\n")
                    f.write(f"DADOS: {str(dados)[:1000]}...\n")
                    f.write(f"STATUS: {status}\n")
                    f.write(f"TIMESTAMP: {timestamp}\n")

                logger.error(f"❌ Erro ao salvar '{nome_etapa}': {e}")
                logger.info(f"🆘 Backup de emergência salvo: {emergency_path}")

            except Exception as emergency_error:
                logger.critical(f"🚨 FALHA CRÍTICA no salvamento de emergência: {emergency_error}")

            return str(emergency_path)

    def salvar_erro(self, etapa: str, erro: Exception, contexto: Dict[str, Any] = None) -> str:
        """Salva erro com contexto completo"""

        erro_data = {
            "etapa": etapa,
            "tipo_erro": type(erro).__name__,
            "mensagem_erro": str(erro),
            "contexto": contexto or {},
            "stack_trace": self._get_stack_trace(erro),
            "timestamp_erro": time.time()
        }

        return self.salvar_etapa(f"ERRO_{etapa}", erro_data, status="erro", categoria="erros")

    def salvar_progresso(self, etapa_atual: str, progresso: float, detalhes: str = "") -> str:
        """Salva progresso atual"""

        progresso_data = {
            "etapa_atual": etapa_atual,
            "progresso_percentual": progresso,
            "detalhes": detalhes,
            "timestamp_progresso": time.time()
        }

        return self.salvar_etapa("progresso", progresso_data, categoria="logs")

    def recuperar_etapa(self, nome_etapa: str, session_id: str = None) -> Optional[Dict[str, Any]]:
        """Recupera dados de uma etapa salva"""

        session_id = session_id or self.session_id
        if not session_id:
            return None

        # Busca em todos os subdiretórios
        for categoria, subdir in self.subdirs.items():
            session_dir = subdir / session_id
            if session_dir.exists():
                # Busca arquivos que começam com o nome da etapa
                for filepath in session_dir.glob(f"{nome_etapa}_*.json"):
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            data = json.load(f)

                        if data.get("status") == "sucesso":
                            logger.info(f"📂 Etapa '{nome_etapa}' recuperada: {filepath}")
                            return data

                    except Exception as e:
                        logger.error(f"❌ Erro ao recuperar {filepath}: {e}")
                        continue

        return None

    def listar_etapas_salvas(self, session_id: str = None) -> Dict[str, Any]:
        """Lista todas as etapas salvas de uma sessão"""

        session_id = session_id or self.session_id
        if not session_id:
            return {}

        etapas_encontradas = {}

        for categoria, subdir in self.subdirs.items():
            session_dir = subdir / session_id
            if session_dir.exists():
                for filepath in session_dir.glob("*.json"):
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            data = json.load(f)

                        etapa = data.get("etapa", "unknown")
                        if etapa not in etapas_encontradas:
                            etapas_encontradas[etapa] = []

                        etapas_encontradas[etapa].append({
                            "arquivo": str(filepath),
                            "status": data.get("status"),
                            "timestamp": data.get("timestamp"),
                            "categoria": categoria,
                            "tamanho": data.get("tamanho_dados", 0)
                        })

                    except Exception as e:
                        logger.error(f"❌ Erro ao ler {filepath}: {e}")
                        continue

        return etapas_encontradas

    def consolidar_sessao(self, session_id: str = None) -> str:
        """Consolida todas as etapas de uma sessão em um relatório final"""

        session_id = session_id or self.session_id
        etapas = self.listar_etapas_salvas(session_id)

        # Recupera dados de cada etapa
        relatorio_consolidado = {
            "session_id": session_id,
            "analysis_id": self.analysis_id,
            "consolidado_em": datetime.now().isoformat(),
            "etapas_processadas": {},
            "estatisticas": {
                "total_etapas": len(etapas),
                "etapas_sucesso": 0,
                "etapas_erro": 0,
                "etapas_fallback": 0
            }
        }

        for etapa_nome, arquivos in etapas.items():
            # Pega o arquivo mais recente de cada etapa
            arquivo_mais_recente = max(arquivos, key=lambda x: x["timestamp"])

            try:
                with open(arquivo_mais_recente["arquivo"], "r", encoding="utf-8") as f:
                    dados_etapa = json.load(f)

                relatorio_consolidado["etapas_processadas"][etapa_nome] = dados_etapa

                # Atualiza estatísticas
                status = dados_etapa.get("status", "unknown")
                if status == "sucesso":
                    relatorio_consolidado["estatisticas"]["etapas_sucesso"] += 1
                elif status == "erro":
                    relatorio_consolidado["estatisticas"]["etapas_erro"] += 1
                elif "fallback" in status:
                    relatorio_consolidado["estatisticas"]["etapas_fallback"] += 1

            except Exception as e:
                logger.error(f"❌ Erro ao consolidar etapa {etapa_nome}: {e}")
                continue

        # Salva relatório consolidado
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        relatorio_path = self.subdirs["analise_completa"] / f"CONSOLIDADO_{session_id}_{timestamp_str}.json"

        with open(relatorio_path, "w", encoding="utf-8") as f:
            json.dump(relatorio_consolidado, f, ensure_ascii=False, indent=2, default=str)

        logger.info(f"📋 Relatório consolidado salvo: {relatorio_path}")
        return str(relatorio_path)

    def _salvar_backup_compactado(self, filepath: Path, data: Dict[str, Any]):
        """Salva backup compactado para dados grandes"""
        try:
            import gzip

            backup_path = filepath.with_suffix('.json.gz')
            with gzip.open(backup_path, 'wt', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)

            logger.info(f"🗜️ Backup compactado salvo: {backup_path}")

        except Exception as e:
            logger.error(f"❌ Erro ao salvar backup compactado: {e}")

    def _get_stack_trace(self, erro: Exception) -> str:
        """Obtém stack trace do erro"""
        import traceback
        return traceback.format_exc()

    def limpar_sessoes_antigas(self, dias: int = 7):
        """Remove sessões mais antigas que X dias"""
        try:
            import shutil
            from datetime import timedelta

            cutoff_time = time.time() - (dias * 24 * 60 * 60)
            removidas = 0

            for subdir in self.subdirs.values():
                for session_dir in subdir.iterdir():
                    if session_dir.is_dir():
                        # Verifica se é mais antiga que o cutoff
                        if session_dir.stat().st_mtime < cutoff_time:
                            shutil.rmtree(session_dir)
                            removidas += 1
                            logger.info(f"🗑️ Sessão antiga removida: {session_dir}")

            logger.info(f"🧹 Limpeza concluída: {removidas} sessões antigas removidas")

        except Exception as e:
            logger.error(f"❌ Erro na limpeza de sessões antigas: {e}")

    def save_intermediate_analysis(self, analysis_data: Dict[str, Any], stage: str) -> str:
        """Salva análise intermediária apenas com insights em TXT"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analise_intermediaria_{stage}_{timestamp}.txt"
            filepath = self.base_dir / filename

            # Extrai apenas insights e informações relevantes
            clean_content = self._extract_insights_only(analysis_data)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"=== ANÁLISE INTERMEDIÁRIA - {stage.upper()} ===\n")
                f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
                f.write(clean_content)

            logger.info(f"✅ Análise intermediária salva: {filename}")
            return str(filepath)

        except Exception as e:
            logger.error(f"❌ Erro ao salvar análise intermediária: {e}")
            return ""

    def _extract_insights_only(self, data: Dict[str, Any]) -> str:
        """Extrai apenas insights relevantes sem códigos ou dados brutos"""
        content = ""

        # Lista de campos relevantes para extrair
        relevant_fields = [
            'resumo_executivo', 'insights_principais', 'oportunidades',
            'recomendacoes', 'analise_competitiva', 'tendencias',
            'pontos_fortes', 'pontos_fracos', 'conclusoes',
            'proximos_passos', 'observacoes_importantes'
        ]

        for field in relevant_fields:
            if field in data and data[field]:
                content += f"\n## {field.replace('_', ' ').upper()}\n"
                if isinstance(data[field], list):
                    for item in data[field]:
                        content += f"• {item}\n"
                elif isinstance(data[field], str):
                    content += f"{data[field]}\n"
                elif isinstance(data[field], dict):
                    for key, value in data[field].items():
                        content += f"• {key}: {value}\n"
                content += "\n"

        # Se não encontrou campos específicos, tenta extrair texto readable
        if not content.strip():
            content = self._extract_readable_text(data)

        return content if content.strip() else "Análise em processamento..."

    def _extract_readable_text(self, data: Any, prefix: str = "") -> str:
        """Extrai texto legível de qualquer estrutura de dados"""
        text = ""

        if isinstance(data, dict):
            for key, value in data.items():
                if not key.startswith('_') and key not in ['metadata', 'raw_data', 'debug']:
                    if isinstance(value, (str, int, float)) and str(value).strip():
                        text += f"{prefix}• {key}: {value}\n"
                    elif isinstance(value, list) and value:
                        text += f"{prefix}• {key}:\n"
                        for item in value[:5]:  # Limita a 5 itens
                            if isinstance(item, str) and item.strip():
                                text += f"{prefix}  - {item}\n"
        elif isinstance(data, list):
            for item in data[:10]:  # Limita a 10 itens
                if isinstance(item, str) and item.strip():
                    text += f"{prefix}• {item}\n"
        elif isinstance(data, str) and data.strip():
            text += f"{prefix}{data}\n"

        return text


# Instância global
auto_save_manager = AutoSaveManager()

# Função de conveniência
def salvar_etapa(nome_etapa: str, dados: Any, status: str = "sucesso", categoria: str = "geral") -> str:
    """Função de conveniência para salvamento rápido"""
    return auto_save_manager.salvar_etapa(nome_etapa, dados, status, categoria=categoria)

def salvar_erro(etapa: str, erro: Exception, contexto: Dict[str, Any] = None) -> str:
    """Função de conveniência para salvamento de erros"""
    return auto_save_manager.salvar_erro(etapa, erro, contexto)