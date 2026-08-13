# Control de PR de `bultodepapas` en VoiceStudio

> Última verificación: **2026-08-13 12:51 COT / 17:51 UTC**
> Upstream: [`debpalash/VoiceStudio`](https://github.com/debpalash/VoiceStudio)
> Autor controlado: [`bultodepapas`](https://github.com/bultodepapas)
> Rama local activa: `fix/remote-admin-session-hardening` → [PR #1528](https://github.com/debpalash/VoiceStudio/pull/1528)

Este es el elemento de control operativo de nuestros PR al upstream. El inventario se obtuvo con una búsqueda global de GitHub por autor y se contrastó contra el repositorio actual y su nombre anterior. Cubre **los 8 PR encontrados**; no incluye commits directos que nunca tuvieron PR ni PR creados desde otra cuenta.

## Tablero ejecutivo

| Estado GitHub | Cantidad | PR |
|---|---:|---|
| Abierto | 1 | [#1528](https://github.com/debpalash/VoiceStudio/pull/1528) |
| Fusionado | 5 | [#1525](https://github.com/debpalash/VoiceStudio/pull/1525), [#1162](https://github.com/debpalash/VoiceStudio/pull/1162), [#1161](https://github.com/debpalash/VoiceStudio/pull/1161), [#1160](https://github.com/debpalash/VoiceStudio/pull/1160), [#1159](https://github.com/debpalash/VoiceStudio/pull/1159) |
| Cerrado sin merge | 2 | [#1163](https://github.com/debpalash/VoiceStudio/pull/1163), [#1158](https://github.com/debpalash/VoiceStudio/pull/1158) |
| **Total** | **8** | 5 fusionados · 2 cerrados · 1 abierto |

Los dos PR cerrados tuvieron seguimiento parcial en `main`, pero no cuentan como merges: el núcleo válido de #1158 fue absorbido con crédito y #1163 produjo una aclaración documental del invariante de concurrencia.

## Acción actual

| Prioridad | PR | Estado verificable | Respuesta upstream | Siguiente control |
|---|---|---|---|---|
| Alta | [#1528 — sesiones de administrador](https://github.com/debpalash/VoiceStudio/pull/1528) | `OPEN`, `MERGEABLE`, `CLEAN`; 17/17 checks verdes; 16/16 hilos resueltos; CodeRabbit sin hallazgos accionables | El maintainer añadió 3 commits, validó las suites y dejó pendiente su verificación manual ([respuesta](https://github.com/debpalash/VoiceStudio/pull/1528#issuecomment-5282085581)) | No hay cambio solicitado pendiente. Vigilar nueva revisión o merge; si cambia el SHA, volver a comprobar CI e hilos. |

No hay otro PR abierto que requiera respuesta.

## Inventario completo

| PR | Resultado actual | Fechas UTC | Tamaño | Revisión / CI | Resolución |
|---|---|---|---:|---|---|
| [#1528](https://github.com/debpalash/VoiceStudio/pull/1528) | **Abierto; listo para verificación del maintainer** | 2026-08-13 → abierto | 70 archivos, +6873/−410, 11 commits | 17/17 checks; 16/16 hilos resueltos | Esperando verificación manual; sin hallazgos pendientes |
| [#1525](https://github.com/debpalash/VoiceStudio/pull/1525) | **Fusionado** | 2026-08-13 03:38 → 05:04 | 28 archivos, +620/−147, 7 commits | 17/17 checks; 6/6 hilos resueltos | Merge [`cd541131`](https://github.com/debpalash/VoiceStudio/commit/cd541131734c5f584d38c42d398e41314e94b1a2) por `debpalash` |
| [#1163](https://github.com/debpalash/VoiceStudio/pull/1163) | **Cerrado; fix declinado** | 2026-07-16 03:03 → 10:33 | 1 archivo, +7/−0, 1 commit | Solo 2 controles de bots; 3 hilos quedaron abiertos al cerrar; Greptile 3/5 | La carrera propuesta era inalcanzable; se documentó el invariante en [`025a358a`](https://github.com/debpalash/VoiceStudio/commit/025a358a582313e652b1b8f87b13e191b5f4f673) |
| [#1162](https://github.com/debpalash/VoiceStudio/pull/1162) | **Fusionado** | 2026-07-16 03:02 → 12:58 | 2 archivos, +115/−6, 3 commits | 16/16 checks; Greptile 5/5 | Merge [`b1bf00a2`](https://github.com/debpalash/VoiceStudio/commit/b1bf00a25786d2908e643163a6ed8dc05f80876b); se preservó el contrato `resolve(null)` |
| [#1161](https://github.com/debpalash/VoiceStudio/pull/1161) | **Fusionado** | 2026-07-16 03:02 → 12:49 | 2 archivos, +102/−1, 2 commits | 16/16 checks; Greptile 4/5 | Merge [`5ea8389c`](https://github.com/debpalash/VoiceStudio/commit/5ea8389cd42c64cbf78b39f1628723d342d3791d); se conservó texto parcial y se añadió logging |
| [#1160](https://github.com/debpalash/VoiceStudio/pull/1160) | **Fusionado** | 2026-07-16 03:01 → 10:31 | 1 archivo, +2/−2, 1 commit | 16/16 checks; Greptile 4/5 | Merge [`7da418bd`](https://github.com/debpalash/VoiceStudio/commit/7da418bd8854f155475bc9f2633ddb89f17bb3c4) |
| [#1159](https://github.com/debpalash/VoiceStudio/pull/1159) | **Fusionado** | 2026-07-16 03:00 → 10:31 | 1 archivo, +1/−1, 1 commit | 16/16 checks; Greptile 5/5; sin hilos | Merge [`91e960fb`](https://github.com/debpalash/VoiceStudio/commit/91e960fb3fdb4dfff0a53619586801d9442babf8) |
| [#1158](https://github.com/debpalash/VoiceStudio/pull/1158) | **Cerrado; absorbido parcialmente** | 2026-07-16 02:42 → 10:33 | 14 archivos, +29/−29, 2 commits | Sin CI completo; 14 hilos quedaron abiertos; Greptile 2/5 | El núcleo de `useAppData` entró a `main` en [`b9c677db`](https://github.com/debpalash/VoiceStudio/commit/b9c677db2c0de5b50be003e1550d617808486768) con crédito |

Los campos `CHANGES_REQUESTED` y los hilos que GitHub aún muestra en #1161/#1162 son metadatos históricos sin acción operativa: ambos PR fueron corregidos y fusionados después. No deben confundirse con bloqueos actuales.

## Detalle de decisiones y respuestas

### #1528 — `fix(security): replace persistent admin keys with scoped sessions`

- **Objetivo:** sustituir claves administrativas persistentes en el UI por sesiones revocables y tickets WebSocket de un solo uso, manteniendo compatibilidad de clientes directos.
- **Head actual:** [`c1f0f9ba`](https://github.com/debpalash/VoiceStudio/commit/c1f0f9bafe5fa578b9aed4a85ff35c762847b0d7).
- **Respuesta nuestra:** se corrigieron y contestaron hallazgos de CodeQL, precedencia Bearer, Unicode, `root_path`, i18n y detección de almacenamiento opcional. La verificación de notas no accionables quedó [documentada](https://github.com/debpalash/VoiceStudio/pull/1528#issuecomment-5281916204).
- **Respuesta upstream:** `debpalash` incorporó tres correcciones de integración: store estable ante recargas de módulos, `X-Forwarded-Proto` seguro y eliminación de la clave solo después de un intercambio exitoso ([detalle](https://github.com/debpalash/VoiceStudio/pull/1528#issuecomment-5282085581)).
- **Control vigente:** CI, seguridad, CodeRabbit y Greptile están verdes; los 16 hilos están resueltos; no existe aprobación formal en `reviewDecision`. Queda la verificación manual/merge del maintainer.

### #1525 — `fix(security): close server-mode admin bypasses`

- **Objetivo:** exigir autenticación para acciones administrativas remotas, normalizar extracción y precedencia de credenciales, y conservar el comportamiento loopback.
- **Revisión:** 6/6 hilos resueltos; CodeRabbit terminó sin comentarios accionables; 17/17 checks verdes.
- **Respuesta upstream:** no hubo respuesta escrita del maintainer; `debpalash` lo fusionó 1 h 26 min después de abrirlo.
- **Resultado:** aceptado íntegramente en [`cd541131`](https://github.com/debpalash/VoiceStudio/commit/cd541131734c5f584d38c42d398e41314e94b1a2).

### #1163 — `fix: prevent healthy WebSocket queues from being killed by race condition`

- **Propuesta:** manejar un supuesto `QueueEmpty` entre `put_nowait()` y `get_nowait()`.
- **Respuesta upstream:** el maintainer lo declinó tras tres análisis de concurrencia: no existe `await` en esa sección, por lo que asyncio no puede cambiar de tarea dentro de la ventana propuesta ([respuesta completa](https://github.com/debpalash/VoiceStudio/pull/1163#issuecomment-4990847302)).
- **Resultado:** el código no se incorporó. Sí se añadió a `main` el comentario que documenta el invariante single-loop/no-await en [`025a358a`](https://github.com/debpalash/VoiceStudio/commit/025a358a582313e652b1b8f87b13e191b5f4f673).
- **Control vigente:** cerrado definitivamente. Solo reabrir la investigación con una excepción real o evidencia de desconexión que contradiga el invariante.

### #1162 — `fix: prevent probeAudioDuration from hanging on unresolved Promise`

- **Propuesta:** añadir timeout al probe de duración de audio.
- **Respuesta upstream:** una prueba conductual confirmó el hang, pero también mostró que rechazar la Promise rompía `ingestRefAudio`; se pidió conservar el timeout y resolver `null` en error/timeout ([respuesta](https://github.com/debpalash/VoiceStudio/pull/1162#issuecomment-4991608293)).
- **Resultado:** se aplicó el ajuste en `138ed091`, Greptile quedó 5/5, CI pasó y el PR se fusionó en [`b1bf00a2`](https://github.com/debpalash/VoiceStudio/commit/b1bf00a25786d2908e643163a6ed8dc05f80876b).

### #1161 — `fix: return empty text instead of partial garbage when EPUB HTML parse fails`

- **Propuesta inicial:** registrar el error y devolver capítulo vacío al fallar el parseo.
- **Respuesta upstream:** la prueba con EPUB de tres capítulos demostró que devolver vacío eliminaba silenciosamente el capítulo; se pidió registrar el traceback y conservar el texto parcial ([respuesta](https://github.com/debpalash/VoiceStudio/pull/1161#issuecomment-4991608479)).
- **Resultado:** el commit `68c3a11f` cambió la semántica final; el título del PR quedó desactualizado, pero el merge [`5ea8389c`](https://github.com/debpalash/VoiceStudio/commit/5ea8389cd42c64cbf78b39f1628723d342d3791d) contiene logging más conservación parcial.

### #1160 — `fix: log full traceback when dub job persistence fails`

- **Objetivo:** usar `logger.exception()` para conservar el traceback de fallos SQLite al persistir jobs de dubbing.
- **Revisión:** CodeRabbit no generó comentarios accionables; Greptile 4/5 indicó que el cambio mejoraba observabilidad sin cambiar el control de flujo.
- **Respuesta upstream:** no hubo comentario escrito; `debpalash` lo fusionó en [`7da418bd`](https://github.com/debpalash/VoiceStudio/commit/7da418bd8854f155475bc9f2633ddb89f17bb3c4).
- **Nota:** el PR no pretendía hacer fallar al caller cuando la persistencia falla; ese riesgo quedó fuera de su alcance.

### #1159 — `fix: prevent TDZ ReferenceError crash when bootstrap fails`

- **Objetivo:** declarar el estado `logs` antes de usarlo en el cálculo de `isUnrecoverable`.
- **Revisión:** sin hilos, CodeRabbit sin hallazgos accionables, Greptile 5/5 y 16/16 checks verdes.
- **Respuesta upstream:** no hubo comentario escrito; `debpalash` lo fusionó en [`91e960fb`](https://github.com/debpalash/VoiceStudio/commit/91e960fb3fdb4dfff0a53619586801d9442babf8).

### #1158 — `fix: add error logging to data-loading catch blocks`

- **Propuesta inicial:** reemplazar catches silenciosos por diagnósticos `console.warn`; el alcance creció de 5 catches en un archivo a 14 archivos.
- **Respuesta upstream:** se encontró un `.` que rompía el parseo, mensajes `resume`/`suspend` invertidos, ruido en errores esperados y deriva de alcance. El maintainer cerró el PR y decidió absorber solo los catches válidos de `useAppData` ([respuesta completa](https://github.com/debpalash/VoiceStudio/pull/1158#issuecomment-4990847694)).
- **Resultado:** el PR no se fusionó; el núcleo válido entró con crédito en [`b9c677db`](https://github.com/debpalash/VoiceStudio/commit/b9c677db2c0de5b50be003e1550d617808486768).
- **Lección de control:** un concern por PR, build verificado y distinguir fallos esperados de errores que sí requieren diagnóstico.

## Protocolo para mantener este control

Al crear o actualizar un PR:

1. Añadirlo al tablero y al inventario con fecha, rama, alcance y enlace.
2. Registrar `state`, `mergeable`, `mergeStateStatus`, `reviewDecision`, checks y hilos resueltos/no resueltos.
3. Resumir toda respuesta humana del maintainer y enlazar el comentario, sin copiar conversaciones completas.
4. Registrar cada hallazgo accionable y su resolución; si se descarta, anotar la justificación verificable.
5. Al cerrar, enlazar el merge commit o explicar exactamente qué fue absorbido/declinado.

Comandos base de actualización:

```powershell
gh search prs --repo debpalash/VoiceStudio --author bultodepapas --limit 1000 `
  --json number,title,state,url,createdAt,updatedAt,closedAt,isDraft,commentsCount

gh pr view <N> --repo debpalash/VoiceStudio `
  --json state,mergeable,mergeStateStatus,reviewDecision,statusCheckRollup,comments,reviews,commits

gh pr checks <N> --repo debpalash/VoiceStudio
```

Para los hilos inline, `gh pr view --comments` no basta. Consultar `pullRequest.reviewThreads` por GraphQL y comprobar `isResolved`; antes de cualquier merge, volver a leer CodeRabbit, Greptile y cualquier hallazgo Critical/P1.
