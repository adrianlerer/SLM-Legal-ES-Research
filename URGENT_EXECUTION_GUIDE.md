# 🚨 SCM Legal - Guía de Ejecución Urgente
## Respuesta a Crisis de Abstracts Abiertos

> **TIEMPO CRÍTICO**: Ejecutar dentro de las próximas 48-72 horas para máximo aprovechamiento de la ventana de oportunidad

---

## ⚡ Ejecución Inmediata (Ahora)

### **1. Preparación del Entorno (5 minutos)**
```bash
cd /home/user/SLM-Legal-Spanish

# Verificar estructura del proyecto
ls -la scripts/
ls -la data/ 2>/dev/null || mkdir -p data

# Hacer ejecutable el script principal
chmod +x scripts/execute-urgent-harvesting.sh
```

### **2. Ejecutar Harvesting Urgente (30-60 minutos)**
```bash
# EJECUTAR AHORA - Ventana crítica
./scripts/execute-urgent-harvesting.sh
```

**Este script ejecutará:**
- ✅ Extracción masiva de OpenAlex (antes de más restricciones)
- ✅ Harvesting de Semantic Scholar (papers legales)
- ✅ Fuentes OA hispanoamericanas (SciELO, repositorios)
- ✅ Procesamiento y combinación de corpus
- ✅ Backup de emergencia

### **3. Monitorear Progreso**
```bash
# En otra terminal, monitorear logs
tail -f data/logs/urgent_harvesting_*.log

# Verificar archivos generados
watch "ls -la data/harvested/ data/hispano_legal/ 2>/dev/null"
```

---

## 📊 Qué Esperar

### **Resultados Esperados**
- **50K+ papers académicos** con abstracts (OpenAlex/Semantic Scholar)
- **30K+ documentos legales** hispanoamericanos (SciELO, repositorios)
- **Bases de datos SQLite** con metadata estructurada
- **Corpus combinado** listo para entrenamiento LoRA
- **Backup comprimido** de todo el contenido

### **Archivos Generados**
```
data/
├── harvested/
│   ├── legal_corpus_20241201_1430.json.gz     # Academic papers
│   └── corpus_stats_20241201_1430.json        # Statistics
├── hispano_legal/
│   ├── hispano_legal_corpus_20241201_1445.json.gz
│   └── hispano_stats_20241201_1445.json
├── *.db                                        # SQLite databases
├── combined_corpus/
│   └── harvesting_metadata.json               # Session info
└── emergency_legal_corpus_20241201_1430.tar.gz  # Backup
```

### **Métricas de Éxito**
- **Total documents**: >80K
- **With abstracts**: >40K (50%+)
- **Hispanic content**: >30K (40%+)
- **Legal relevance**: >80% confidence
- **Processing time**: <2 hours

---

## 🎯 Próximos Pasos Después del Harvesting

### **Inmediato (Mismo día)**
```bash
# 1. Verificar corpus generado
cd data
python3 prepare_training_data.py

# 2. Verificar calidad de datos
python3 -c "
import json, gzip
with gzip.open('harvested/legal_corpus_*.json.gz', 'rt') as f:
    data = json.load(f)
    print(f'Academic papers: {len(data)}')
    with_abstracts = sum(1 for item in data if item.get('abstract'))
    print(f'With abstracts: {with_abstracts} ({with_abstracts/len(data)*100:.1f}%)')
"

# 3. Crear backup adicional
cp -r data/ ~/scm-legal-backup-$(date +%Y%m%d)
```

### **Esta Semana**
1. **Procesar corpus combinado** para entrenamiento LoRA
2. **Configurar training pipeline** con datos extraídos
3. **Implementar disclaimers** de cobertura en aplicación web
4. **Documentar lessons learned** del proceso de crisis

### **Próximo Mes** 
1. **Entrenar modelo SCM** con corpus de emergencia
2. **Deploy modelo actualizado** con transparency reports
3. **Establecer monitoring** de fuentes alternativas
4. **Publicar research paper** sobre crisis response methodology

---

## 🔍 Solución de Problemas

### **Errores Comunes y Soluciones**

#### **Error: Python dependencies**
```bash
# Solución
python3 -m pip install --user aiohttp requests beautifulsoup4 lxml pandas sqlite3
```

#### **Error: Permisos de escritura**
```bash
# Solución  
chmod -R 755 data/
mkdir -p data/{harvested,hispano_legal,logs,corpus}
```

#### **Error: Rate limiting**
```bash
# El script incluye rate limiting automático
# Si persiste: modificar requests_per_second en configs
```

#### **Error: Memoria insuficiente**
```bash
# Monitorear uso de memoria
free -h

# Si es necesario, reducir batch_size en configs
```

### **Verificaciones de Sanidad**
```bash
# 1. Verificar conectividad APIs
curl -s "https://api.openalex.org/works?per_page=1" | jq .
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=legal&limit=1" | jq .

# 2. Verificar espacio en disco
df -h

# 3. Verificar procesos activos
ps aux | grep python3
```

---

## 💡 Optimizaciones Durante Ejecución

### **Si el Harvesting es Lento**
```python
# Modificar en scripts/urgent-data-harvesting.py
requests_per_second: int = 15  # Aumentar de 10 a 15
batch_size: int = 300          # Aumentar de 200 a 300
```

### **Si Necesitas más Datos**
```python
# Modificar max_papers_per_source
max_papers_per_source: int = 100000  # Aumentar de 50000
```

### **Ejecución Paralela Avanzada**
```bash
# Ejecutar harvesting en background
nohup ./scripts/execute-urgent-harvesting.sh > harvesting.log 2>&1 &

# Monitorear progreso
tail -f harvesting.log
```

---

## 📋 Checklist de Ejecución

### **Pre-Ejecución**
- [ ] Proyecto en `/home/user/SLM-Legal-Spanish/`
- [ ] Scripts tienen permisos de ejecución
- [ ] Conexión a internet estable
- [ ] Suficiente espacio en disco (>5GB)
- [ ] Python 3.8+ instalado con dependencias

### **Durante Ejecución**
- [ ] Script ejecutándose sin errores críticos
- [ ] Archivos siendo generados en `data/`
- [ ] Logs mostrando progreso de harvesting
- [ ] Uso de memoria y CPU en niveles normales

### **Post-Ejecución**
- [ ] Corpus académico generado (>40K papers)
- [ ] Corpus hispano generado (>20K docs)
- [ ] Bases de datos SQLite creadas
- [ ] Backup de emergencia completado
- [ ] Metadata de sesión documentada

### **Validación de Calidad**
- [ ] >50% papers con abstracts disponibles
- [ ] Diversidad de fuentes (>5 diferentes)
- [ ] Balance jurisdiccional razonable
- [ ] Relevancia legal >80% en muestreo
- [ ] Sin duplicados masivos detectados

---

## 🎯 Mensaje Final

**Esta es una ventana de oportunidad crítica y limitada**. La industria académica está cerrando el acceso a abstracts, pero tenemos una implementación lista para extraer datos masivos **antes de que las restricciones se endurezcan**.

**Ejecutar AHORA**:
```bash
cd /home/user/SLM-Legal-Spanish
./scripts/execute-urgent-harvesting.sh
```

Una vez completado este harvesting urgente, tendrás:
- Un **corpus único** de contenido legal extraído antes de las restricciones
- **Ventaja competitiva** sobre proyectos que inicien después
- **Base sólida** para entrenar el modelo SCM Legal
- **Caso de uso académico** para publicación sobre crisis response

**El tiempo es crítico - ejecutar inmediatamente para máximo beneficio.**