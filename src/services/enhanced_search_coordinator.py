#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Enhanced Search Coordinator
Coordenador que garante buscas simultâneas e distintas entre Exa e Google
"""

import os
import logging
import time
import asyncio
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from services.exa_client import exa_client
from services.production_search_manager import production_search_manager
from services.auto_save_manager import salvar_etapa, salvar_erro

logger = logging.getLogger(__name__)

class EnhancedSearchCoordinator:
    """Coordenador de buscas simultâneas e distintas"""
    
    def __init__(self):
        """Inicializa coordenador de busca"""
        self.exa_available = exa_client.is_available()
        self.google_available = bool(os.getenv('GOOGLE_SEARCH_KEY') and os.getenv('GOOGLE_CSE_ID'))
        
        logger.info(f"🔍 Enhanced Search Coordinator - Exa: {self.exa_available}, Google: {self.google_available}")
    
    def execute_simultaneous_distinct_search(
        self, 
        base_query: str, 
        context: Dict[str, Any],
        session_id: str = None
    ) -> Dict[str, Any]:
        """Executa buscas simultâneas e distintas entre Exa e Google"""
        
        logger.info(f"🚀 Iniciando buscas simultâneas para: {base_query}")
        
        # Prepara queries distintas para cada provedor
        exa_query = self._prepare_exa_query(base_query, context)
        google_query = self._prepare_google_query(base_query, context)
        
        # Salva queries preparadas
        salvar_etapa("queries_simultaneas", {
            "base_query": base_query,
            "exa_query": exa_query,
            "google_query": google_query,
            "context": context
        }, categoria="pesquisa_web")
        
        search_results = {
            'base_query': base_query,
            'exa_results': [],
            'google_results': [],
            'other_results': [],
            'statistics': {
                'total_results': 0,
                'exa_count': 0,
                'google_count': 0,
                'other_count': 0,
                'search_time': 0
            }
        }
        
        start_time = time.time()
        
        # Executa buscas em paralelo
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            
            # Busca Exa (se disponível)
            if self.exa_available:
                futures.append(
                    executor.submit(self._execute_exa_search, exa_query, context)
                )
            
            # Busca Google (se disponível)
            if self.google_available:
                futures.append(
                    executor.submit(self._execute_google_search, google_query, context)
                )
            
            # Busca outros provedores
            futures.append(
                executor.submit(self._execute_other_search, base_query, context)
            )
            
            # Coleta resultados conforme completam
            for future in as_completed(futures):
                try:
                    result = future.result()
                    
                    if result['provider'] == 'exa':
                        search_results['exa_results'] = result['results']
                        search_results['statistics']['exa_count'] = len(result['results'])
                        logger.info(f"✅ Exa: {len(result['results'])} resultados")
                        
                        # Salva resultados Exa
                        salvar_etapa("exa_results", result, categoria="pesquisa_web")
                        
                    elif result['provider'] == 'google':
                        search_results['google_results'] = result['results']
                        search_results['statistics']['google_count'] = len(result['results'])
                        logger.info(f"✅ Google: {len(result['results'])} resultados")
                        
                        # Salva resultados Google
                        salvar_etapa("google_results", result, categoria="pesquisa_web")
                        
                    elif result['provider'] == 'other':
                        search_results['other_results'] = result['results']
                        search_results['statistics']['other_count'] = len(result['results'])
                        logger.info(f"✅ Outros: {len(result['results'])} resultados")
                        
                        # Salva resultados outros
                        salvar_etapa("other_results", result, categoria="pesquisa_web")
                
                except Exception as e:
                    logger.error(f"❌ Erro em busca paralela: {e}")
                    salvar_erro("busca_paralela", e, contex to={"query": base_query})
                    continue
        
        # Calcula estatísticas finais
        search_time = time.time() - start_time
        search_results['statistics']['search_time'] = search_time
        search_results['statistics']['total_results'] = (
            search_results['statistics']['exa_count'] + 
            search_results['statistics']['google_count'] + 
            search_results['statistics']['other_count']
        )
        
        # Salva resultado consolidado
        salvar_etapa("busca_simultanea_consolidada", search_results, categoria="pesquisa_web")
        
        logger.info(f"✅ Buscas simultâneas concluídas em {search_time:.2f}s - Total: {search_results['statistics']['total_results']} resultados")
        
        return search_results
    
    def _prepare_exa_query(self, base_query: str, context: Dict[str, Any]) -> str:
        """Prepara query específica para Exa (neural search)"""
        
        # Exa é melhor com queries mais conceituais e semânticas
        exa_query = base_query
        
        
        
        # Adiciona contexto semântico
        if context.get('segmento'):
            exa_query += f" {context['segmento']} insights análise"
        
        # Adiciona termos para busca neural
        exa_query += " tendências oportunidades estratégia"
        
        return exa_query.strip()
    
    def _prepare_google_query(self, base_query: str, context: Dict[str, Any]) -> str:
        """Prepara query específica para Google (keyword search)"""
        
        # Google é melhor com keywords específicas
        google_query = base_query
        
        # Adiciona keywords específicas
        if context.get('segmento'):
            google_query += f" {context['segmento']} dados estatísticas"
        
        # Adiciona termos para busca por keywords
        google_query += " Brasil 2024 mercado crescimento"
        
        return google_query.strip()
    
    def _execute_exa_search(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Executa busca específica no Exa"""
        
        try:
             
            # Domínios brasileiros preferenciais para Exa
            include_domains = [
                "g1.globo.com", "exame.com", "valor.globo.com", "estadao.com.br",
                "folha.uol.com.br", "canaltech.com.br", "infomoney.com.br"
            ]
            
            exa_response =  exa_client.search(
                query=query,
                num_results=15,
                include_domains=include_domains,
                start_published_date="2023-01-01",
                use_autoprompt=True,
                type="neural"
            )
            
            if exa_response and 'results' in exa_response:
                results = []
                for item in exa_response['results']:
                    results.append({
                        'title': item.get('title', ''),
                        'url': item.get('url', ''),
                        'snippet': item.get('text', '')[:300],
                        'source': 'exa_neural',
                        'score': item.get('score', 0),
                        'published_date': item.get('publishedDate', ''),
                        'exa_id': item.get('id', '')
                    })
                
                return {
                    'provider': 'exa',
                    'query': query,
                    'results': results,
                    'success': True
                }
            else:
                return {
                    'provider': 'exa',
                    'query': query,
                    'results': [],
                    
                    'success': False,
                    'error': 'Exa não retornou resultados válidos'
                }
                
        except Exception as e:
            logger.error(f"❌ Erro na busca Exa: {e}")
            return {
                'provider': 'exa',
                'query': query,
                'results': [],
                'success': False,
                '
                error': str(e)
            }
    
    def _execute_google_search(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Executa busca específica no Google"""
        
        try:
            # Usa production search manager para Google
            google_results = production_search_manager.search_with_fallback(query, max_results=15)
            
            # Filtra apenas resultados do Google
            google_only = [r for r in google_results if r.get('source') == 'google']
            
            return {
                'provider': 'google',
                'query': query,
                'results': google_only,
                'success': len(google_only) > 0
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na busca Google: {e}")
            return {
                'provider': 'google',
                'query': query,
                'results': [],
                'success': False,
                'error': str(e)
            }
    
    def _execute_other_search(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Exec uta busca em outros provedores"""
        
        try:
            # Usa outros provedores (Serper, Bing, DuckDuckGo)
            other_results = production_search_manager.search_with_fallback(query, max_results=10)
            
            # Filtra resultados que não são Google ou Exa
            other_only = [r for r in other_results if r.get('source') not in ['google', 'exa']]
            
            return {
                'provider': 'other',
                'query': query,
                'results': other_only,
                'success': len(other_only) > 0
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na busca outros: {e}")
            return {
                'provider': 'other',
                'query': query,
                'results': [],
                'success': False,
                'error': str(e)
            }

# Instância global
enhanced_search_coordinator = EnhancedSearchCoordinator()