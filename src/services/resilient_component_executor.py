#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Resilient Component Executor
Executor resiliente que isola falhas e preserva dados
"""

import time
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import asyncio
import signal

# Importação corrigida de auto_save_manager, assumindo que ele existe e tem as funções necessárias
try:
    from services.auto_save_manager import auto_save_manager, salvar_etapa, salvar_erro
except ImportError:
    logger = logging.getLogger(__name__)
    logger.error("services.auto_save_manager não encontrado. Funcionalidades de salvamento podem falhar.")
    # Cria mock objects para permitir a execução sem a importação correta
    class MockAutoSaveManager:
        def __init__(self):
            self.session_id = None
            self.analysis_id = None
            logger.warning("Usando mock para auto_save_manager. Nenhuma análise será salva.")

        def iniciar_sessao(self):
            self.session_id = f"mock_session_{int(time.time())}"
            return self.session_id

        def save_intermediate_analysis(self, data, stage):
            logger.info(f"Mock save_intermediate_analysis: Stage={stage}, Data={data}")

        def save_error_analysis(self, error_details, stage):
            logger.error(f"Mock save_error_analysis: Stage={stage}, Error={error_details}")

    auto_save_manager = MockAutoSaveManager()
    def salvar_etapa(stage, data, categoria=None):
        auto_save_manager.save_intermediate_analysis(data, stage)
    def salvar_erro(stage, error, contexto=None):
        auto_save_manager.save_error_analysis(str(error), stage)


logger = logging.getLogger(__name__)

class ResilientComponentExecutor:
    """Executor resiliente de componentes com isolamento de falhas"""

    def __init__(self):
        """Inicializa o executor resiliente"""
        self.componentes_registrados = {}
        self.ordem_execucao = []
        self.resultados_componentes = {}
        self.estatisticas_execucao = {}
        self.auto_save_manager = auto_save_manager # Atribui para uso em métodos internos
        self.logger = logger # Atribui o logger para métodos internos

        logger.info("Resilient Component Executor inicializado")

    def registrar_componente(
        self,
        nome: str,
        executor: Callable,
        fallback: Optional[Callable] = None,
        obrigatorio: bool = False,
        timeout: int = 300,
        dependencias: List[str] = None
    ):
        """Registra um componente no executor"""

        self.componentes_registrados[nome] = {
            'executor': executor,
            'fallback': fallback,
            'obrigatorio': obrigatorio,
            'timeout': timeout,
            'dependencias': dependencias or [],
            'status': 'pendente'
        }

        if nome not in self.ordem_execucao:
            self.ordem_execucao.append(nome)

        logger.info(f"📝 Componente registrado: {nome}")

    def executar_pipeline_resiliente(
        self,
        dados_entrada: Dict[str, Any],
        session_id: str = None,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Executa pipeline resiliente com isolamento de falhas"""

        logger.info(f"🚀 Iniciando pipeline resiliente com {len(self.componentes_registrados)} componentes")

        # Inicia sessão se não fornecida
        if not session_id:
            session_id = self.auto_save_manager.iniciar_sessao()
            # Corrige o atributo analysis_id se estiver usando o mock
            if not hasattr(self.auto_save_manager, 'analysis_id') or self.auto_save_manager.analysis_id is None:
                self.auto_save_manager.analysis_id = f"analysis_{session_id}"


        # Salva início do pipeline
        salvar_etapa("pipeline_iniciado", {
            "componentes": list(self.componentes_registrados.keys()),
            "dados_entrada": dados_entrada,
            "session_id": session_id
        }, categoria="analise_completa")

        dados_acumulados = dados_entrada.copy()
        componentes_sucesso = []
        componentes_falha = []

        for i, nome_componente in enumerate(self.ordem_execucao):
            if progress_callback:
                progress_callback(i + 1, f"Executando {nome_componente}...")

            try:
                # Verifica dependências
                if not self._verificar_dependencias(nome_componente, componentes_sucesso):
                    logger.warning(f"⚠️ Dependências não atendidas para {nome_componente}")
                    componentes_falha.append(nome_componente)
                    continue

                # Executa componente com isolamento
                resultado = self._executar_componente_isolado(nome_componente, dados_acumulados)

                if resultado is not None:
                    # Sucesso - adiciona aos dados acumulados
                    dados_acumulados[nome_componente] = resultado
                    componentes_sucesso.append(nome_componente)

                    # Salva resultado imediatamente
                    salvar_etapa(f"componente_{nome_componente}", resultado, categoria="analise_completa")

                    logger.info(f"✅ Componente {nome_componente} executado com sucesso")
                else:
                    # Falha - tenta fallback
                    resultado_fallback = self._executar_fallback(nome_componente, dados_acumulados)

                    if resultado_fallback:
                        dados_acumulados[nome_componente] = resultado_fallback
                        componentes_sucesso.append(nome_componente)

                        # Salva fallback
                        salvar_etapa(f"fallback_{nome_componente}", resultado_fallback, categoria="analise_completa")

                        logger.info(f"🔄 Fallback de {nome_componente} executado com sucesso")
                    else:
                        componentes_falha.append(nome_componente)
                        logger.error(f"❌ Componente {nome_componente} falhou completamente")

            except Exception as e:
                logger.error(f"❌ Erro crítico em {nome_componente}: {str(e)}")
                salvar_erro(f"componente_{nome_componente}", e, contexto=dados_entrada)

                # Tenta fallback mesmo com erro crítico
                try:
                    resultado_fallback = self._executar_fallback(nome_componente, dados_acumulados)
                    if resultado_fallback:
                        dados_acumulados[nome_componente] = resultado_fallback
                        componentes_sucesso.append(nome_componente)
                        logger.info(f"🔄 Fallback de emergência para {nome_componente} funcionou")
                    else:
                        componentes_falha.append(nome_componente)
                except Exception as fallback_error:
                    logger.error(f"❌ Fallback de {nome_componente} também falhou: {fallback_error}")
                    componentes_falha.append(nome_componente)

        # Calcula estatísticas
        total_componentes = len(self.componentes_registrados)
        sucessos = len(componentes_sucesso)
        falhas = len(componentes_falha)
        taxa_sucesso = (sucessos / total_componentes) * 100 if total_componentes > 0 else 0

        # Resultado do pipeline
        resultado_pipeline = {
            'session_id': session_id,
            'analysis_id': getattr(self.auto_save_manager, 'analysis_id', None), # Acessa analysis_id de forma segura
            'dados_gerados': {k: v for k, v in dados_acumulados.items() if k != 'dados_entrada'},
            'componentes_sucesso': componentes_sucesso,
            'componentes_falha': componentes_falha,
            'estatisticas': {
                'total_componentes': total_componentes,
                'componentes_executados': sucessos,
                'componentes_falharam': falhas,
                'taxa_sucesso': taxa_sucesso,
                'pipeline_completo': falhas == 0,
                'dados_preservados': sucessos > 0
            },
            'processamento': {
                'inicio': dados_entrada.get('start_time', time.time()),
                'fim': time.time(),
                'duracao': time.time() - dados_entrada.get('start_time', time.time())
            }
        }

        # Salva resultado final do pipeline
        salvar_etapa("pipeline_completo", resultado_pipeline, categoria="analise_completa")

        logger.info(f"📊 Pipeline concluído: {sucessos}/{total_componentes} sucessos ({taxa_sucesso:.1f}%)")

        return resultado_pipeline

    def _verificar_dependencias(self, nome_componente: str, componentes_sucesso: List[str]) -> bool:
        """Verifica se dependências do componente foram atendidas"""

        componente = self.componentes_registrados.get(nome_componente, {})
        dependencias = componente.get('dependencias', [])

        for dependencia in dependencias:
            if dependencia not in componentes_sucesso:
                return False

        return True

    def _executar_componente_isolado(self, nome_componente: str, dados: Dict[str, Any]) -> Any:
        """Executa componente com isolamento de falhas"""

        componente = self.componentes_registrados[nome_componente]
        executor = componente['executor']
        timeout = componente['timeout']

        try:
            # Executa com timeout
            

            def timeout_handler(signum, frame):
                raise TimeoutError(f"Componente {nome_componente} excedeu timeout de {timeout}s")

            # Configura timeout (apenas em sistemas Unix)
            try:
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(timeout)

                resultado = executor(dados)

                signal.alarm(0)  # Cancela timeout
                return resultado

            except AttributeError:
                # Sistema Windows - executa sem timeout por signal
                # Para Windows, podemos usar uma abordagem alternativa se necessário,
                # mas por enquanto, apenas logamos a limitação.
                logger.warning(f"Timeout via signal não suportado no Windows para {nome_componente}. Executando sem timeout.")
                return executor(dados)
            except TimeoutError:
                logger.error(f"⏰ Timeout em {nome_componente}")
                # Tenta salvar o estado parcial em caso de timeout antes de retornar None
                self._save_partial_result(nome_componente, "executor", {"timeout": timeout}, is_error=True)
                return None

        except Exception as e:
            logger.error(f"❌ Erro isolado em {nome_componente}: {str(e)}")
            # Tenta salvar o estado parcial em caso de erro antes de retornar None
            partial_data = self._extract_partial_data(dados)
            self._save_partial_result(nome_componente, "executor", partial_data, is_error=True)
            return None

    def _executar_fallback(self, nome_componente: str, dados: Dict[str, Any]) -> Any:
        """Executa fallback do componente"""

        componente = self.componentes_registrados.get(nome_componente, {})
        fallback = componente.get('fallback')

        if not fallback:
            return None

        try:
            logger.info(f"🔄 Executando fallback para {nome_componente}")
            resultado = fallback(dados)
            # Salva o resultado do fallback
            self._save_partial_result(nome_componente, "fallback", resultado, is_error=False)
            return resultado

        except Exception as e:
            logger.error(f"❌ Fallback de {nome_componente} falhou: {str(e)}")
            # Salva o erro do fallback
            partial_data = self._extract_partial_data(dados)
            self._save_partial_result(nome_componente, "fallback", partial_data, is_error=True)
            return None

    def get_execution_summary(self) -> Dict[str, Any]:
        """Retorna resumo da execução"""

        return {
            'componentes_registrados': list(self.componentes_registrados.keys()),
            'ordem_execucao': self.ordem_execucao,
            'resultados_disponiveis': list(self.resultados_componentes.keys()),
            'estatisticas': self.estatisticas_execucao
        }

    def reset(self):
        """Reseta estado do executor"""

        self.resultados_componentes = {}
        self.estatisticas_execucao = {}

        for componente in self.componentes_registrados.values():
            componente['status'] = 'pendente'

        logger.info("🔄 Executor resiliente resetado")

    # Novas funções para continuidade e salvamento
    async def execute_component_safe(self, component_name: str, method_name: str, *args, **kwargs) -> Dict[str, Any]:
        """Executa componente de forma segura com continuidade"""
        start_time = time.time()

        try:
            # Busca o componente
            if component_name not in self.components:
                raise ValueError(f"Componente {component_name} não encontrado")

            component = self.components[component_name]
            method = getattr(component, method_name)

            # Executa o método
            if asyncio.iscoroutinefunction(method):
                result = await method(*args, **kwargs)
            else:
                result = method(*args, **kwargs)

            execution_time = time.time() - start_time

            # Salva resultado parcial se bem-sucedido
            self._save_partial_result(component_name, method_name, result)

            return {
                'success': True,
                'result': result,
                'component': component_name,
                'method': method_name,
                'execution_time': execution_time,
                'error': None
            }

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)

            self.logger.error(f"❌ Erro em {component_name}.{method_name}: {error_msg}")

            # Salva o que conseguiu obter antes do erro
            partial_result = self._extract_partial_data(*args, **kwargs)
            if partial_result:
                self._save_partial_result(component_name, method_name, partial_result, is_error=True)

            return {
                'success': False,
                'result': partial_result,
                'component': component_name,
                'method': method_name,
                'execution_time': execution_time,
                'error': error_msg,
                'continued': True  # Indica que continuou apesar do erro
            }

    def _save_partial_result(self, component: str, method: str, result: Any, is_error: bool = False):
        """Salva resultado parcial para continuidade"""
        try:
            if hasattr(self, 'auto_save_manager') and self.auto_save_manager:
                stage = f"{component}_{method}"
                if is_error:
                    stage += "_PARTIAL_ERROR"

                # Converte resultado para formato salvável
                save_data = {
                    'component': component,
                    'method': method,
                    'timestamp': datetime.now().isoformat(),
                    'result': result if isinstance(result, (dict, list, str, int, float)) else str(result),
                    'status': 'error' if is_error else 'success'
                }

                self.auto_save_manager.save_intermediate_analysis(save_data, stage)
        except Exception as e:
            self.logger.warning(f"Erro ao salvar resultado parcial: {e}")

    def _extract_partial_data(self, *args, **kwargs) -> Dict[str, Any]:
        """Extrai dados parciais dos argumentos em caso de erro"""
        partial = {}

        try:
            # Tenta extrair informações úteis dos argumentos
            for i, arg in enumerate(args):
                if isinstance(arg, (dict, list)) and arg:
                    partial[f'arg_{i}'] = arg
                elif isinstance(arg, str) and len(arg) > 10:
                    partial[f'input_{i}'] = arg[:500]  # Primeiros 500 chars

            for key, value in kwargs.items():
                if isinstance(value, (dict, list, str)) and value:
                    if isinstance(value, str):
                        partial[key] = value[:500]  # Limita strings
                    else:
                        partial[key] = value

        except Exception:
            partial['note'] = 'Dados parciais não disponíveis'

        return partial if partial else {'note': 'Continuando análise...'}


# Instância global
resilient_executor = ResilientComponentExecutor()