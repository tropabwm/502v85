#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Production Search Manager
Gerenciador de busca para produção com múltiplos provedores e fallbacks
"""

import os
import logging
import time
import requests
from typing import Dict, List, Optional, Any
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import json
import random
from services.exa_client import exa_client
import asyncio # Importar asyncio para buscas assíncronas

logger = logging.getLogger(__name__)

class ProductionSearchManager:
    """Gerenciador de busca para produção com sistema de fallback"""

    def __init__(self):
        """Inicializa o gerenciador de busca"""
        self.providers = {
            'exa': {
                'enabled': exa_client.is_available(),
                'priority': 1,  # Prioridade máxima
                'error_count': 0,
                'max_errors': 3,
                'client': exa_client
            },
            'google': {
                'enabled': bool(os.getenv('GOOGLE_SEARCH_KEY') and os.getenv('GOOGLE_CSE_ID')),
                'priority': 2,
                'error_count': 0,
                'max_errors': 3,
                'api_key': os.getenv('GOOGLE_SEARCH_KEY'),
                'cse_id': os.getenv('GOOGLE_CSE_ID'),
                'base_url': 'https://www.googleapis.com/customsearch/v1'
            },
            'serper': {
                'enabled': bool(os.getenv('SERPER_API_KEY')),
                'priority': 3,
                'error_count': 0,
                'max_errors': 3,
                'api_key': os.getenv('SERPER_API_KEY'),
                'base_url': 'https://google.serper.dev/search'
            },
            'bing': {
                'enabled': True,  # Sempre disponível via scraping
                'priority': 4,
                'error_count': 0,
                'max_errors': 5,
                'base_url': 'https://www.bing.com/search'
            },
            'duckduckgo': {
                'enabled': True,  # Sempre disponível via scraping
                'priority': 5,
                'error_count': 0,
                'max_errors': 5,
                'base_url': 'https://html.duckduckgo.com/html/'
            }
        }

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive'
        }

        self.cache = {}
        self.cache_ttl = 3600  # 1 hora

        enabled_count = sum(1 for p in self.providers.values() if p['enabled'])
        logger.info(f"Production Search Manager inicializado com {enabled_count} provedores")

    def search_with_fallback(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Realiza busca com sistema de fallback automático"""

        # Verifica cache primeiro
        cache_key = f"{query}_{max_results}"
        if cache_key in self.cache:
            cache_data = self.cache[cache_key]
            if time.time() - cache_data['timestamp'] < self.cache_ttl:
                logger.info(f"🔄 Resultado do cache para: {query}")
                return cache_data['results']

        # Busca com fallback
        for provider_name in self._get_provider_order():
            if not self._is_provider_available(provider_name):
                continue

            try:
                logger.info(f"🔍 Buscando com {provider_name}: {query}")

                if provider_name == 'google':
                    results = self._search_google(query, max_results)
                elif provider_name == 'serper':
                    results = self._search_serper(query, max_results)
                elif provider_name == 'bing':
                    results = self._search_bing(query, max_results)
                elif provider_name == 'duckduckgo':
                    results = self._search_duckduckgo(query, max_results)
                else:
                    continue

                if results:
                    # Cache resultado
                    self.cache[cache_key] = {
                        'results': results,
                        'timestamp': time.time(),
                        'provider': provider_name
                    }

                    logger.info(f"✅ {provider_name}: {len(results)} resultados")
                    return results
                else:
                    logger.warning(f"⚠️ {provider_name}: 0 resultados")

            except Exception as e:
                logger.error(f"❌ Erro em {provider_name}: {str(e)}")
                self._record_provider_error(provider_name)
                continue

        logger.error("❌ Todos os provedores de busca falharam")
        return []

    def _get_provider_order(self) -> List[str]:
        """Retorna provedores ordenados por prioridade"""
        available_providers = [
            (name, provider) for name, provider in self.providers.items()
            if self._is_provider_available(name)
        ]

        # Ordena por prioridade e número de erros
        available_providers.sort(key=lambda x: (x[1]['priority'], x[1]['error_count']))

        return [name for name, _ in available_providers]

    def _is_provider_available(self, provider_name: str) -> bool:
        """Verifica se provedor está disponível"""
        provider = self.providers.get(provider_name, {})
        return (provider.get('enabled', False) and
                provider.get('error_count', 0) < provider.get('max_errors', 3))

    def _record_provider_error(self, provider_name: str):
        """Registra erro do provedor"""
        if provider_name in self.providers:
            self.providers[provider_name]['error_count'] += 1

            if self.providers[provider_name]['error_count'] >= self.providers[provider_name]['max_errors']:
                logger.warning(f"⚠️ Provedor {provider_name} desabilitado temporariamente")

    def _search_google(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Busca usando Google Custom Search API"""
        provider = self.providers['google']

        params = {
            'key': provider['api_key'],
            'cx': provider['cse_id'],
            'q': query,
            'num': min(max_results, 10),
            'lr': 'lang_pt',
            'gl': 'br',
            'safe': 'off'
        }

        response = requests.get(
            provider['base_url'],
            params=params,
            headers=self.headers,
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            results = []

            for item in data.get('items', []):
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'source': 'google'
                })

            return results
        else:
            raise Exception(f"Google API retornou status {response.status_code}")

    def _search_serper(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Busca usando Serper API"""
        provider = self.providers['serper']

        headers = {
            **self.headers,
            'X-API-KEY': provider['api_key'],
            'Content-Type': 'application/json'
        }

        payload = {
            'q': query,
            'gl': 'br',
            'hl': 'pt',
            'num': max_results
        }

        response = requests.post(
            provider['base_url'],
            json=payload,
            headers=headers,
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            results = []

            for item in data.get('organic', []):
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'source': 'serper'
                })

            return results
        else:
            raise Exception(f"Serper API retornou status {response.status_code}")

    def _search_bing(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Busca usando Bing (scraping)"""
        search_url = f"{self.providers['bing']['base_url']}?q={quote_plus(query)}&cc=br&setlang=pt-br&count={max_results}"

        response = requests.get(search_url, headers=self.headers, timeout=15)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []

            result_items = soup.find_all('li', class_='b_algo')

            for item in result_items[:max_results]:
                title_elem = item.find('h2')
                if title_elem:
                    link_elem = title_elem.find('a')
                    if link_elem:
                        title = title_elem.get_text(strip=True)
                        url = link_elem.get('href', '')

                        snippet_elem = item.find('p')
                        snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                        if url and title and url.startswith('http'):
                            results.append({
                                'title': title,
                                'url': url,
                                'snippet': snippet,
                                'source': 'bing'
                            })

            return results
        else:
            raise Exception(f"Bing retornou status {response.status_code}")

    def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Busca usando DuckDuckGo (scraping)"""
        search_url = f"{self.providers['duckduckgo']['base_url']}?q={quote_plus(query)}"

        response = requests.get(search_url, headers=self.headers, timeout=15)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []

            result_divs = soup.find_all('div', class_='result')

            for div in result_divs[:max_results]:
                title_elem = div.find('a', class_='result__a')
                snippet_elem = div.find('a', class_='result__snippet')

                if title_elem:
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href', '')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                    if url and title and url.startswith('http'):
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet,
                            'source': 'duckduckgo'
                        })

            return results
        else:
            raise Exception(f"DuckDuckGo retornou status {response.status_code}")

    def get_provider_status(self) -> Dict[str, Any]:
        """Retorna status de todos os provedores"""
        status = {}

        for name, provider in self.providers.items():
            status[name] = {
                'enabled': provider['enabled'],
                'available': self._is_provider_available(name),
                'priority': provider['priority'],
                'error_count': provider['error_count'],
                'max_errors': provider['max_errors']
            }

        return status

    def reset_provider_errors(self, provider_name: str = None):
        """Reset contadores de erro dos provedores"""
        if provider_name:
            if provider_name in self.providers:
                self.providers[provider_name]['error_count'] = 0
                logger.info(f"🔄 Reset erros do provedor: {provider_name}")
        else:
            for provider in self.providers.values():
                provider['error_count'] = 0
            logger.info("🔄 Reset erros de todos os provedores")

    def clear_cache(self):
        """Limpa cache de busca"""
        self.cache = {}
        logger.info("🧹 Cache de busca limpo")

    def test_provider(self, provider_name: str, query: str = "teste", max_results: int = 3) -> bool:
        """Testa um provedor específico"""
        if provider_name not in self.providers:
            return False

        try:
            if provider_name == 'exa':
                # A chamada para _search_exa precisa de query e max_results
                return bool(self._search_exa(query, max_results))
            elif provider_name == 'google':
                results = self._search_google(query, max_results)
            elif provider_name == 'serper':
                results = self._search_serper(query, max_results)
            elif provider_name == 'bing':
                results = self._search_bing(query, max_results)
            elif provider_name == 'duckduckgo':
                results = self._search_duckduckgo(query, max_results)
            else:
                return False

            return len(results) > 0

        except Exception as e:
            logger.error(f"❌ Teste do provedor {provider_name} falhou: {e}")
            return False

    def _search_exa(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Busca usando Exa Neural Search"""
        try:
            # Melhora query para mercado brasileiro
            enhanced_query = self._enhance_query_for_brazil(query)

            # Domínios brasileiros preferenciais
            include_domains = [
                "g1.globo.com", "exame.com", "valor.globo.com", "estadao.com.br",
                "folha.uol.com.br", "canaltech.com.br", "infomoney.com.br"
            ]

            exa_response = exa_client.search(
                query=enhanced_query,
                num_results=max_results,
                include_domains=include_domains,
                start_published_date="2023-01-01",
                use_autoprompt=True,
                type="neural"
            )

            if not exa_response or 'results' not in exa_response:
                raise Exception("Exa não retornou resultados válidos")

            results = []
            for item in exa_response['results']:
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('url', ''),
                    'snippet': item.get('text', '')[:300],
                    'source': 'exa',
                    'score': item.get('score', 0),
                    'published_date': item.get('publishedDate', ''),
                    'exa_id': item.get('id', '')
                })

            logger.info(f"✅ Exa Neural Search: {len(results)} resultados")
            return results

        except Exception as e:
            if "quota" in str(e).lower() or "limit" in str(e).lower():
                logger.warning(f"⚠️ Exa atingiu limite: {str(e)}")
            raise e

    def _enhance_query_for_brazil(self, query: str) -> str:
        """Melhora query para pesquisa no Brasil"""
        enhanced_query = query
        query_lower = query.lower()

        # Adiciona termos brasileiros se não estiverem presentes
        if not any(term in query_lower for term in ["brasil", "brasileiro", "br"]):
            enhanced_query += " Brasil"

        # Adiciona ano atual se não estiver presente
        if not any(year in query for year in ["2024", "2025"]):
            enhanced_query += " 2024"

        return enhanced_query.strip()

    async def _safe_search_provider(self, provider_config: Dict[str, Any], query: str, max_results: int) -> List[Dict[str, Any]]:
        """Envolve a busca do provedor em um try-except seguro"""
        provider_name = provider_config.get('name') # Assumindo que o nome do provedor está na config
        if not provider_name:
            provider_name = [name for name, config in self.providers.items() if config is provider_config][0]

        try:
            logger.info(f"🔍 Iniciando busca assíncrona com {provider_name}: {query}")
            if provider_name == 'exa':
                results = self._search_exa(query, max_results)
            elif provider_name == 'google':
                results = self._search_google(query, max_results)
            elif provider_name == 'serper':
                results = self._search_serper(query, max_results)
            elif provider_name == 'bing':
                results = self._search_bing(query, max_results)
            elif provider_name == 'duckduckgo':
                results = self._search_duckduckgo(query, max_results)
            else:
                results = []

            if not results:
                logger.warning(f"⚠️ {provider_name}: 0 resultados na busca assíncrona")
            return results

        except Exception as e:
            self.logger.warning(f"Erro assíncrono no provedor {provider_name}: {e}")
            self._record_provider_error(provider_name) # Registra erro para fallback
            return []


    async def search_parallel(self, queries: List[str], max_results: int = 10) -> Dict[str, Any]:
        """Busca paralela em todos os provedores com Exa e Google prioritários"""
        results = {
            'total_queries': len(queries),
            'results_by_provider': {},
            'aggregated_results': [],
            'metadata': {},
            'exa_specific_results': [],
            'google_specific_results': []
        }

        for query in queries:
            query_results = []

            # Busca PRIORITÁRIA e SIMULTÂNEA em Exa e Google
            exa_task = None
            google_task = None

            if self.providers.get('exa', {}).get('enabled'):
                exa_task = self._safe_search_provider(self.providers['exa'], query, max_results)

            if self.providers.get('google', {}).get('enabled'):
                google_task = self._safe_search_provider(self.providers['google'], query, max_results)

            # Aguarda Exa e Google prioritariamente
            if exa_task:
                try:
                    exa_results = await exa_task
                    if exa_results:
                        results['results_by_provider']['exa'] = exa_results
                        results['exa_specific_results'].extend(exa_results)
                        query_results.extend(exa_results)
                except Exception as e:
                    self.logger.warning(f"Erro no Exa: {e}")

            if google_task:
                try:
                    google_results = await google_task
                    if google_results:
                        results['results_by_provider']['google'] = google_results
                        results['google_specific_results'].extend(google_results)
                        query_results.extend(google_results)
                except Exception as e:
                    self.logger.warning(f"Erro no Google: {e}")

            # Busca em outros provedores em paralelo (secundária)
            other_tasks = []
            for provider_name, provider in self.providers.items():
                if provider and provider_name not in ['exa', 'google'] and provider.get('enabled'):
                    task = self._safe_search_provider(provider, query, max_results)
                    other_tasks.append((provider_name, task))

            # Aguarda outros provedores
            for provider_name, task in other_tasks:
                try:
                    provider_results = await task
                    if provider_results:
                        results['results_by_provider'][provider_name] = provider_results
                        query_results.extend(provider_results)
                except Exception as e:
                    self.logger.warning(f"Erro no provedor {provider_name}: {e}")

            results['aggregated_results'].extend(query_results)

        # Adicionar metadados gerais
        results['metadata']['timestamp'] = time.time()
        results['metadata']['providers_status'] = self.get_provider_status()

        return results

    # Adicionar um logger para a classe, caso não esteja globalmente configurado
    @property
    def logger(self):
        return logger

# Instância global
production_search_manager = ProductionSearchManager()

# Exemplo de uso (precisa de um loop de eventos asyncio para rodar):
# async def main():
#     search_manager = ProductionSearchManager()
#     queries = ["inteligencia artificial no mercado de trabalho", "novidades carros elétricos 2024"]
#     results = await search_manager.search_parallel(queries, max_results=5)
#
#     print(json.dumps(results, indent=2, ensure_ascii=False))
#
# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)
#     asyncio.run(main())