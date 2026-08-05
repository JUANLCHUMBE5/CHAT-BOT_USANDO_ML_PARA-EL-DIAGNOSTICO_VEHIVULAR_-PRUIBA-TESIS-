## 2026-08-03T23:53:26Z
You are worker_m1_3 working in directory c:\Users\leonc\OneDrive\Desktop\CHAT_BOT_MACHINLEARNING\.agents\worker_m1_3.
You MUST read c:\Users\leonc\OneDrive\Desktop\CHAT_BOT_MACHINLEARNING\.agents\ORIGINAL_REQUEST.md before starting work.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your assignment is to fix the final 2 performance & TTL issues identified by challenger_1_v2:

1. Create your directory c:\Users\leonc\OneDrive\Desktop\CHAT_BOT_MACHINLEARNING\.agents\worker_m1_3 and initialize progress.md.
2. Fix 1 — Remove Redundant 3x ML/RAG Executions (`src/interfaces/api/v1/endpoints/diagnostico.py`):
   - In `analizar_sintoma()`, REMOVE the redundant standalone calls to `gestor.modelo_ml.predecir_falla_con_confianza` and `gestor.motor_rag.recuperar_contexto`.
   - Execute ONLY `respuesta_explicativa = await run_in_threadpool(gestor.procesar_consulta_texto, consulta.sintoma, placa=consulta.placa, session_id=consulta.session_id)`.
   - Populate `DiagnosticResponseDTO` cleanly from `gestor` or returned diagnosis.
3. Fix 2 — Instant Expired Session Eviction & Force Cleanup (`src/core/session_manager.py`):
   - In `obtener_sesion()` and `obtener_o_crear_sesion()`, if `sesion.ha_expirado(ttl_segundos)` is True, immediately pop/delete the expired session from `self._sesiones`.
   - Add an optional parameter `force: bool = False` to `_limpiar_sesiones_expiradas(self, ttl_segundos: int = 1800, force: bool = False)` so if `force=True`, it bypasses the 30-second throttle `ahora - self._ultimo_limpieza < 30`.
4. Verification & Testing:
   - Run `python .agents/challenger_r1_1/stress_test_suite.py` -> VERIFY 33/33 ASSERTIONS PASS CLEANLY (including 4.2, 5.2, 5.4). Verify max REST latency < 2000 ms and max Webhook latency < 2000 ms.
   - Run `python pruebas/test_backend_y_webhooks.py` -> verify 100% pass.
   - Run `python pruebas/test_session_manager.py` -> verify 100% pass.
   - Run `python pruebas/test_patrones_diagnostico.py` -> verify 100% pass.
5. Document all changes, metrics, and test outputs in handoff.md in your directory. Send a message to parent when complete.
