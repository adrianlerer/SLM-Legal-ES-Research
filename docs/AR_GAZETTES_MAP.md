# Mapa de Boletines Oficiales (Argentina)

## Archivo Fuente
- **Ubicación**: `schema/ar_boletines_map.json`
- **Formato**: JSON Schema con validación automática
- **Propósito**: Configuración centralizada de fuentes oficiales

## Regla Crítica
**⚠️ VERIFICAR MANUALMENTE** cada `url_base` antes de habilitar *fetchers* reales.

## Estructura por Jurisdicción

### Nacional (AR)
- **BORA**: Boletín Oficial de la República Argentina
- **URL**: https://www.boletinoficial.gob.ar/ *(VERIFICAR)*
- **Estado**: Pendiente verificación manual

### Provincias Principales

#### Ciudad Autónoma de Buenos Aires (AR-C)
- **BOCBA**: Boletín Oficial CABA
- **URL**: https://boletinoficial.buenosaires.gob.ar/ *(VERIFICAR)*
- **Estado**: Pendiente verificación manual

#### Buenos Aires (AR-B)
- **PBA**: Boletín Oficial Provincia de Buenos Aires
- **URL**: https://boletinoficial.gba.gob.ar/ *(VERIFICAR)*
- **Estado**: Pendiente verificación manual

#### Córdoba (AR-X)
- **CORDOBA**: Boletín Oficial Provincia de Córdoba
- **URL**: TODO - Pendiente investigación
- **Estado**: Requiere identificación de portal oficial

#### Mendoza (AR-M)
- **MENDOZA**: Boletín Oficial Provincia de Mendoza
- **URL**: TODO - Pendiente investigación
- **Estado**: Requiere identificación de portal oficial

#### Santa Fe (AR-S)
- **SANTAFE**: Boletín Oficial Provincia de Santa Fe
- **URL**: https://www.santafe.gob.ar/boletinoficial/ *(VERIFICAR)*
- **Estado**: Pendiente verificación manual

#### Neuquén (AR-Q)
- **NEUQUEN**: Boletín Oficial Provincia de Neuquén
- **URL**: TODO - Pendiente investigación
- **Estado**: Requiere identificación de portal oficial

#### Río Negro (AR-R)
- **RIONEGRO**: Boletín Oficial Provincia de Río Negro
- **URL**: TODO - Pendiente investigación
- **Estado**: Requiere identificación de portal oficial

## Campos por Boletín

### Obligatorios
- **`name`**: Nombre oficial completo del boletín
- **`url_base`**: URL base del sitio oficial

### Opcionales (para implementación futura)
- **`search_endpoint`**: Endpoint específico de búsqueda
- **`rate_limit_ms`**: Intervalo entre requests (default: 1000ms)

## Uso en Fetchers

### Carga del Mapa
```typescript
import boletinesMap from "../schema/ar_boletines_map.json";

function getBulletinConfig(jurisdiction: string): BulletinConfig {
  return boletinesMap[jurisdiction];
}
```

### Construcción de URLs
```typescript
const config = getBulletinConfig("AR-C");
const searchUrl = `${config.BOCBA.url_base}${config.BOCBA.search_endpoint}`;
```

### Respeto de Rate Limits
```typescript
const rateLimitMs = config.BOCBA.rate_limit_ms || 1000;
await sleep(rateLimitMs);
```

## Normalización ELI

### Integración con Fuentes
Los ingestors provinciales y nacionales deben:

1. **Leer este mapa** para construir URLs dinámicamente
2. **Normalizar fuentes** usando campos `name` como fuente ELI
3. **Aplicar rate limiting** según configuración por boletín

### Ejemplo de Normalización
```typescript
// Del fetcher
const docData = {
  jurisdiction: "AR-C",
  source: boletinesMap["AR-C"].BOCBA.name,
  url_base: boletinesMap["AR-C"].BOCBA.url_base
};

// Normalización ELI
const eliDoc = normalizeToELI(docData);
```

## Consideraciones de Implementación

### Verificación Manual Requerida
**Antes de habilitar fetchers**, verificar cada URL:

1. **Acceso público**: ¿El sitio es de acceso libre?
2. **Robots.txt**: ¿Permite web scraping?
3. **ToS**: ¿Los términos permiten uso académico/investigación?
4. **Estructura**: ¿Es estable la estructura HTML/API?
5. **Rate limits**: ¿Hay límites implícitos o explícitos?

### Extensión a Nuevas Provincias
```json
"AR-K": {
  "type": "object",
  "properties": {
    "CATAMARCA": {
      "name": "Boletín Oficial de la Provincia de Catamarca",
      "url_base": "TODO (VERIFICAR URL OFICIAL)"
    }
  }
}
```

## Mantenimiento y Actualizaciones

### Monitoreo Requerido
- **URLs activas**: Verificación periódica de disponibilidad
- **Cambios estructurales**: Detección de modificaciones en sitios
- **Nuevos endpoints**: Identificación de APIs oficiales

### Control de Versiones
- **Cambios en URLs**: Commit separado con justificación
- **Nuevas provincias**: PR independiente con verificación
- **Rate limit updates**: Basado en testing real de sitios

## Próximos Pasos

### Fase 1: Verificación
1. Revisar manualmente cada URL listada
2. Confirmar accesibilidad y términos de servicio
3. Actualizar status de "VERIFICAR" → "CONFIRMED" o "BLOCKED"

### Fase 2: Implementación
1. Conectar fetchers con configuración verificada
2. Implementar respeto automático de rate limits
3. Establecer monitoreo de cambios en sitios

### Fase 3: Extensión
1. Agregar provincias faltantes
2. Identificar APIs oficiales donde existan
3. Optimizar performance y reliability