# SCM v2 — Especificación Técnica Pública

> Este documento describe la interfaz y el comportamiento del SCM v2.  
> La implementación del engine (omlx_client, supabase_client, modelos) es propietaria y no se publica.

## Endpoint

```
POST /v1/scm
Authorization: Bearer sk_live_<token>
Content-Type: application/json
```

## Request

```json
{
  "text": "Texto jurídico en español a analizar",
  "principles": ["Legalidad", "Buena fe", "..."],
  "context": "Tipo de caso / rama del derecho (opcional)",
  "jurisdiction": "Argentina/CCyC-2015"
}
```

**Principios por defecto (24 Universales):**

| # | Principio | Rama primaria |
|---|---|---|
| 1 | Legalidad | Derecho Público |
| 2 | Igualdad ante la ley | Constitucional |
| 3 | Proporcionalidad | Administrativo / Penal |
| 4 | Razonabilidad | Constitucional |
| 5 | Debido proceso | Procesal |
| 6 | Defensa en juicio | Procesal |
| 7 | Presunción de inocencia | Penal |
| 8 | Non bis in idem | Penal |
| 9 | Irretroactividad | Civil / Penal |
| 10 | Buena fe | Civil / Comercial |
| 11 | Autonomía de la voluntad | Contractual |
| 12 | Pacta sunt servanda | Contractual |
| 13 | Rebus sic stantibus | Contractual |
| 14 | Enriquecimiento sin causa | Civil |
| 15 | Responsabilidad | Civil / Penal |
| 16 | Causalidad | Civil / Penal |
| 17 | Solidaridad | Laboral / Social |
| 18 | Subsidiariedad | Administrativo |
| 19 | Cosa juzgada | Procesal |
| 20 | Seguridad jurídica | Transversal |
| 21 | Congruencia | Procesal |
| 22 | Motivación del acto | Administrativo |
| 23 | Control judicial | Constitucional |
| 24 | Transparencia | Administrativo |

## Response

```json
{
  "scores": {
    "Motivación del acto": 1.0,
    "Defensa en juicio": 0.7
  },
  "top_principles": ["Motivación del acto", "Defensa en juicio", "..."],
  "details": {
    "Motivación del acto": {
      "score": 1.0,
      "confidence": 1.0,
      "evidence": "fragmento textual exacto que activa este principio"
    }
  },
  "tensions": [
    {
      "principles": ["Pacta sunt servanda", "Rebus sic stantibus"],
      "message": "Tensión dialéctica detectada — requiere ponderación profesional."
    }
  ],
  "low_confidence_flags": ["Buena fe"],
  "jurisdiction": "Argentina/CCyC-2015",
  "backend": "oMLX:Qwen2.5-7B-Instruct-4bit",
  "client_id": "estudio_xxx",
  "limitations": [
    "Jurisdicción configurada: Argentina/CCyC-2015. Para otras jurisdicciones, los scores variarán.",
    "Las 24 dimensiones priorizan interpretabilidad sobre exhaustividad.",
    "No sustituye el criterio profesional.",
    "..."
  ]
}
```

## Escala de Scores

| Valor | Interpretación |
|---|---|
| 0.0 | No relevante |
| 0.3 | Tangencialmente relacionado |
| 0.7 | Claramente aplicable |
| 1.0 | Principio central del caso |

## Escala de Confidence

| Valor | Interpretación |
|---|---|
| 0.0 | Muy incierto (texto ambiguo o insuficiente) |
| 0.5 | Certeza moderada |
| 1.0 | Completamente claro en el texto |

## Detección de Tensiones Dialécticas

El sistema monitorea 8 pares de principios que pueden operar en tensión:

- Autonomía de la voluntad ↔ Buena fe
- Autonomía de la voluntad ↔ Rebus sic stantibus  
- Pacta sunt servanda ↔ Rebus sic stantibus
- Seguridad jurídica ↔ Razonabilidad
- Debido proceso ↔ Congruencia
- Legalidad ↔ Razonabilidad
- Cosa juzgada ↔ Control judicial
- Subsidiariedad ↔ Control judicial

Cuando ambos principios de un par superan 0.55 de score, se emite un `TensionAlert`.

## Diseño de Temperatura

El SCM usa temperatura **0.1** (determinismo intencional):

- **Por qué determinismo:** el mismo texto debe dar el mismo vector de principios  
  entre distintos analistas y en distintos momentos → reproducibilidad y auditabilidad.
- **Contraste con LLMs genéricos:** asistentes de propósito general usan temperatura 0.7-1.0 
  para "creatividad". En clasificación jurídica, la variabilidad es un bug, no una feature.
- **La interpretación es humana:** el SCM orienta; el abogado decide.

## Limitaciones Conocidas y Transparencia

Cada respuesta incluye un array `limitations` generado automáticamente. Las limitaciones estructurales son:

1. **Sesgo jurisdiccional:** corpus primario en Argentina (CCyC 2015, Ley 19.550, CSJN). Otras jurisdicciones tienen menor representatividad.
2. **Reducción dimensional:** 24 principios capturan estructura, no matices.  Casos con alta especificidad doctrinaria pueden requerir análisis complementario.
3. **No sustituye criterio profesional:** outputs son indicativos para orientar la investigación.
4. **Tensiones sin resolver:** cuando se detectan tensiones dialécticas, el sistema alerta pero no toma partido — esa ponderación es casuística y queda en el profesional.

## Ejemplo Real

**Input (caso AySA vs Accell, 2024):**
> "La Resolución 3-2024 de AySA rescinde unilateralmente el contrato con Accell S.A. invocando fuerza mayor sin haber dado audiencia previa al contratista ni motivado debidamente el acto administrativo."

**Output verificado:**

| Principio | Score | Confidence | Evidencia |
|---|---|---|---|
| Motivación del acto | **1.00** | 1.00 | "rescinde... sin motivar debidamente el acto" |
| Defensa en juicio | **0.70** | 1.00 | "sin haber dado audiencia previa al contratista" |
| Pacta sunt servanda | **0.70** | 1.00 | "rescinde unilateralmente el contrato" |
| Buena fe | 0.30 | 0.00 | (baja confianza — texto ambiguo) |

**Backend:** Qwen2.5-7B-Instruct-4bit via oMLX (Apple Silicon) — inferencia local, costo marginal cero.
