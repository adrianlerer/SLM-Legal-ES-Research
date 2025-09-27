#!/usr/bin/env python3
"""
Legal Corpus Builder for SCM Training
=====================================

Script para construir corpus legal especializado desde fuentes argentinas y españolas.
Diseñado para crear datasets de entrenamiento clase mundial para publicación académica.

Sources:
- Argentine legal texts: InfoLEG, Boletín Oficial, Jurisprudencia
- Spanish legal texts: BOE, CENDOJ, Westlaw
- Multi-jurisdictional: Chile (BCN), Uruguay (IMPO)

Autor: Ignacio Adrian Lerer
Proyecto: SCM-Legal-Spanish
"""

import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple
import json
import time
import re
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
import logging
from rich.console import Console
from rich.progress import Progress, track
import asyncio
import aiohttp
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()

@dataclass
class LegalDocument:
    """Estructura de documento legal"""
    title: str
    content: str
    source: str
    jurisdiction: str
    category: str
    date: str
    url: str
    concepts: List[str]

class LegalCorpusBuilder:
    """Constructor de corpus legal para entrenamiento SCM"""
    
    def __init__(self, output_dir: str = "data/legal_corpus"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Legal concept taxonomy for classification
        self.legal_concepts = {
            "constitutional": [
                "constitución", "derechos fundamentales", "amparo", "habeas corpus",
                "control constitucionalidad", "supremacía constitucional"
            ],
            "civil": [
                "código civil", "contratos", "responsabilidad civil", "daños perjuicios",
                "derecho familia", "sucesiones", "propiedad", "obligaciones"
            ],
            "commercial": [
                "código comercio", "sociedades comerciales", "quiebras", "concursos",
                "títulos valores", "contratos comerciales", "derecho empresarial"
            ],
            "administrative": [
                "acto administrativo", "procedimiento administrativo", "servicio público",
                "contratación pública", "responsabilidad estado"
            ],
            "labor": [
                "contrato trabajo", "convenio colectivo", "sindicalismo", "seguridad social",
                "accidentes trabajo", "despido", "salario", "ley contrato trabajo"
            ],
            "compliance": [
                "cumplimiento normativo", "lavado dinero", "anticorrupción",
                "debida diligencia", "programa integridad", "riesgo regulatorio"
            ],
            "criminal": [
                "código penal", "delitos", "proceso penal", "garantías procesales",
                "sistema penal acusatorio"
            ]
        }
    
    def classify_legal_concepts(self, text: str) -> List[str]:
        """Clasifica conceptos legales presentes en el texto"""
        text_lower = text.lower()
        found_concepts = []
        
        for category, keywords in self.legal_concepts.items():
            for keyword in keywords:
                if keyword in text_lower:
                    if category not in found_concepts:
                        found_concepts.append(category)
                    break
        
        return found_concepts if found_concepts else ["general"]
    
    def clean_legal_text(self, text: str) -> str:
        """Limpia y normaliza texto legal"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common legal document artifacts
        text = re.sub(r'\bArt\.\s*\d+º?\.?', 'Artículo', text)
        text = re.sub(r'\binc\.\s*\w+\)', '', text)
        
        # Remove page numbers and headers/footers
        text = re.sub(r'\b\d+\s*\n', '', text)
        text = re.sub(r'Página\s+\d+', '', text)
        
        # Normalize quotes and special characters
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        return text.strip()
    
    def extract_argentina_sources(self) -> List[LegalDocument]:
        """Extrae textos legales de fuentes argentinas"""
        
        console.print("[bold blue]Extracting Argentine legal sources...[/bold blue]")
        
        documents = []
        
        # Sample Argentine legal texts (en producción, usar APIs reales)
        sample_arg_texts = [
            {
                "title": "Constitución Nacional Argentina - Art. 14 bis",
                "content": """
                Artículo 14 bis.- El trabajo en sus diversas formas gozará de la protección de las leyes, las que asegurarán al trabajador: condiciones dignas y equitativas de labor; jornada limitada; descanso y vacaciones pagados; retribución justa; salario mínimo vital móvil; igual remuneración por igual tarea; participación en las ganancias de las empresas, con control de la producción y colaboración en la dirección; protección contra el despido arbitrario; estabilidad del empleado público; organización sindical libre y democrática, reconocida por la simple inscripción en un registro especial.
                
                Queda garantizado a los gremios: concertar convenios colectivos de trabajo; recurrir a la conciliación y al arbitraje; el derecho de huelga. Los representantes gremiales gozarán de las garantías necesarias para el cumplimiento de su gestión sindical y las relacionadas con la estabilidad de su empleo.
                
                El Estado otorgará los beneficios de la seguridad social, que tendrá carácter de integral e irrenunciable. En especial, la ley establecerá: el seguro social obligatorio, que estará a cargo de entidades nacionales o provinciales con autonomía financiera y económica, administradas por los interesados con participación del Estado, sin que pueda existir superposición de aportes; jubilaciones y pensiones móviles; la protección integral de la familia; la defensa del bien de familia; la compensación económica familiar y el acceso a una vivienda digna.
                """,
                "source": "Constitución Nacional",
                "category": "constitutional",
                "date": "1994-08-22"
            },
            {
                "title": "Ley de Sociedades Comerciales - Constitución S.A.",
                "content": """
                Las sociedades anónimas se constituyen por instrumento público o privado. Cuando se constituyan por instrumento privado, las firmas deben ser certificadas por escribano público, quien deberá identificar a los comparecientes.

                El estatuto debe contener las siguientes menciones: la denominación social, que debe incluir la expresión "sociedad anónima", su abreviatura o la sigla S.A.; el domicilio de la sociedad; el objeto social descrito de modo preciso y determinado; el plazo de duración que debe ser determinado; el capital social, que se expresará en moneda argentina y se integrará con aportes de los socios.

                Las acciones pueden ser nominativas o al portador, ordinarias o preferidas, y de una o varias clases. Cuando se autoricen diversas clases, se debe determinar las características de cada una. Las acciones ordinarias siempre confieren derecho de voto. Las preferidas pueden otorgar derechos patrimoniales especiales y carecer de voto para ciertas decisiones.

                El directorio es el órgano de administración de la sociedad. Se compone de uno o más directores designados por la asamblea de accionistas por el término de tres ejercicios. Son reelegibles y revocables por la asamblea. En las sociedades anónimas cuyo capital alcance el importe fijado por el art. 299, debe constituirse una sindicatura.
                """,
                "source": "Ley 19.550",
                "category": "commercial", 
                "date": "1984-04-03"
            },
            {
                "title": "Ley de Contrato de Trabajo - Principios Generales",
                "content": """
                El contrato de trabajo tiene como principal objeto la actividad productiva y creadora del hombre en sí. Solo después ha de entenderse que media entre las partes una relación de intercambio y un fin económico en cuanto se disciplina por esta ley.

                Constituye trabajo, a los fines de esta ley, toda actividad lícita que se preste en favor de quien tiene la facultad de dirigirla, mediante una remuneración. El contrato de trabajo se presume celebrado por tiempo indeterminado, salvo que su término resulte de las siguientes circunstancias: que se haya fijado en forma expresa y por escrito el tiempo de su duración; que las modalidades de las tareas o de la actividad razonablemente apreciadas, así lo justifiquen.

                La falta de pago de la remuneración debida en los plazos y condiciones previstos constituye un incumplimiento resolutorio del contrato por parte del empleador, salvo que el trabajador opte por intimar el pago otorgando un plazo que no podrá ser inferior a dos ni superior a cuatro días hábiles.

                El empleador debe dispensar a todos los trabajadores igual trato en identidad de situaciones. Se considerará que existe trato desigual cuando se produzcan discriminaciones arbitrarias fundadas en razones de sexo, religión, raza, nacionalidad, políticas, gremiales o de edad.
                """,
                "source": "Ley 20.744",
                "category": "labor",
                "date": "1976-05-13"
            },
            {
                "title": "Código Civil y Comercial - Responsabilidad Civil",
                "content": """
                Toda persona tiene el deber, en cuanto de ella dependa, de no causar un daño injustificado a otro y de evitar que se produzca un daño, o de disminuir su magnitud. Si tal deber se incumple, queda obligado a reparar el daño que se cause, conforme con las disposiciones de este Código.

                Son presupuestos de la responsabilidad civil: a) el hecho; b) la antijuridicidad; c) la imputabilidad; d) el nexo causal; e) el daño. La antijuridicidad se configura por la violación del deber, en general, de no causar daño a otro. No son antijurídicos los daños causados en el ejercicio regular de un derecho, en legítima defensa propia o de terceros, o en estado de necesidad.

                El factor de atribución es objetivo cuando la culpabilidad del agente es irrelevante a los efectos de atribuir responsabilidad. En tales casos, el responsable se libera demostrando la causa ajena, excepto disposición legal en contrario. El factor de atribución es subjetivo cuando se atribuye responsabilidad por razón de culpa del agente. La culpa consiste en la omisión de la diligencia debida según la naturaleza de la obligación y las circunstancias de las personas, el tiempo y el lugar.

                La reparación del daño debe ser integral. Comprende el daño emergente, el lucro cesante, la pérdida de chance y el daño moral. Las consecuencias de un hecho que acostumbran a suceder según el curso natural y ordinario de las cosas, se llaman consecuencias inmediatas. Las consecuencias que resultan solamente de la conexión de un hecho con un acontecimiento distinto, se llaman consecuencias mediatas.
                """,
                "source": "Código Civil y Comercial",
                "category": "civil",
                "date": "2015-08-01"
            }
        ]
        
        for doc_data in sample_arg_texts:
            doc = LegalDocument(
                title=doc_data["title"],
                content=self.clean_legal_text(doc_data["content"]),
                source=doc_data["source"],
                jurisdiction="argentina",
                category=doc_data["category"],
                date=doc_data["date"],
                url="",  # En producción, incluir URL real
                concepts=self.classify_legal_concepts(doc_data["content"])
            )
            documents.append(doc)
        
        console.print(f"[green]✓ Extracted {len(documents)} Argentine legal documents[/green]")
        return documents
    
    def extract_spain_sources(self) -> List[LegalDocument]:
        """Extrae textos legales de fuentes españolas"""
        
        console.print("[bold blue]Extracting Spanish legal sources...[/bold blue]")
        
        documents = []
        
        # Sample Spanish legal texts
        sample_es_texts = [
            {
                "title": "Constitución Española - Art. 35",
                "content": """
                Todos los españoles tienen el deber de trabajar y el derecho al trabajo, a la libre elección de profesión u oficio, a la promoción a través del trabajo y a una remuneración suficiente para satisfacer sus necesidades y las de su familia, sin que en ningún caso pueda hacerse discriminación por razón de sexo.
                
                La ley regulará un estatuto de los trabajadores que garantice el cumplimiento de las obligaciones laborales y el ejercicio de los derechos laborales. Se reconoce el derecho a la negociación colectiva laboral entre los representantes de los trabajadores y empresarios, así como la fuerza vinculante de los convenios.
                
                Se reconoce el derecho de los trabajadores y empresarios a adoptar medidas de conflicto colectivo. La ley que regule el ejercicio de este derecho, sin perjuicio de las limitaciones que pueda establecer, incluirá las garantías precisas para asegurar el funcionamiento de los servicios esenciales de la comunidad.
                """,
                "source": "Constitución Española",
                "category": "constitutional",
                "date": "1978-12-29"
            },
            {
                "title": "Ley de Sociedades de Capital - Sociedad Anónima",
                "content": """
                En la sociedad anónima el capital, que estará dividido en acciones, se integrará por las aportaciones de los socios, quienes no responderán personalmente de las deudas sociales.

                La denominación de la sociedad anónima deberá contener necesariamente la indicación «Sociedad Anónima» o su abreviatura «S.A.». La denominación deberá ser distinta de la de cualquier otra sociedad preexistente.

                El capital social no podrá ser inferior a 60.000 euros y deberá estar totalmente suscrito y desembolsado, al menos, en una cuarta parte en el momento de otorgar la escritura de constitución. Las aportaciones dinerarias se depositarán en una entidad de crédito a nombre de la sociedad en formación.

                La administración de la sociedad anónima se puede confiar a un administrador único, a varios administradores que actúen solidariamente o de forma conjunta, o a un consejo de administración. Los administradores ejercerán su cargo durante el plazo que fijen los estatutos, que no podrá exceder de seis años.

                La junta general de accionistas es el órgano supremo de expresión de la voluntad social. Todos los accionistas, incluso los disidentes y los que no hayan participado en la reunión, quedan sometidos a los acuerdos de la junta general.
                """,
                "source": "Real Decreto Legislativo 1/2010",
                "category": "commercial",
                "date": "2010-07-02"
            }
        ]
        
        for doc_data in sample_es_texts:
            doc = LegalDocument(
                title=doc_data["title"],
                content=self.clean_legal_text(doc_data["content"]),
                source=doc_data["source"],
                jurisdiction="españa",
                category=doc_data["category"],
                date=doc_data["date"],
                url="",
                concepts=self.classify_legal_concepts(doc_data["content"])
            )
            documents.append(doc)
        
        console.print(f"[green]✓ Extracted {len(documents)} Spanish legal documents[/green]")
        return documents
    
    def extract_compliance_sources(self) -> List[LegalDocument]:
        """Extrae textos especializados en compliance y gobierno corporativo"""
        
        console.print("[bold blue]Extracting compliance and governance sources...[/bold blue]")
        
        documents = []
        
        # Compliance and corporate governance texts
        compliance_texts = [
            {
                "title": "Programa de Integridad - Elementos Esenciales",
                "content": """
                Un programa de integridad efectivo debe contener, como mínimo, los siguientes elementos: código de ética que establezca estándares de conducta y valores organizacionales; políticas y procedimientos de integridad que contemplen actividades de riesgo; capacitación periódica en materia de integridad para directivos y empleados; sistema de consultas y denuncias que permita efectuar presentaciones relacionadas con incumplimientos del programa.

                También debe incluir evaluación de riesgos regularmente, especialmente cuando se modifiquen las actividades y se incorpore tecnología; investigación de denuncias de violaciones al programa y aplicación de medidas disciplinarias; monitoreo continuo del programa y de los riesgos de la actividad; actualización periódica del programa en base a lecciones aprendidas, cambios normativos y mejores prácticas.

                Los canales de denuncia deben garantizar confidencialidad, anonimato cuando sea posible, y prohibir expresamente toda represalia contra quienes efectúen denuncias de buena fe. Las investigaciones deben ser conducidas por personal capacitado e independiente, documentando adecuadamente el proceso y los resultados.

                La alta dirección debe demostrar compromiso genuino con el programa mediante comunicación consistente, asignación de recursos apropiados, y supervisión efectiva de su implementación y funcionamiento.
                """,
                "source": "Resolución 27/2018 UIF",
                "category": "compliance",
                "date": "2018-05-15"
            },
            {
                "title": "Gobierno Corporativo - Principios Fundamentales",
                "content": """
                El gobierno corporativo comprende las normas, prácticas y procesos por los cuales se dirige y controla una sociedad. Involucra el equilibrio de intereses entre accionistas, directorio, management y otros stakeholders como empleados, proveedores, clientes, comunidad y gobierno.

                Los principios fundamentales incluyen: transparencia en la información proporcionada a stakeholders sobre performance financiera, estructura de propiedad, gobierno corporativo y riesgos; responsabilidad del directorio en la dirección estratégica, supervisión efectiva del management, y rendición de cuentas a la sociedad y accionistas; equidad en el trato a todos los accionistas, incluyendo minoritarios y extranjeros.

                El marco de gobierno corporativo debe proteger y facilitar el ejercicio de derechos de los accionistas, asegurar el trato equitativo de todos los accionistas, reconocer los derechos de stakeholders establecidos por ley o acuerdos mutuos, y garantizar la divulgación oportuna y precisa de información material sobre la corporación.

                El directorio debe ser capaz de ejercer juicio objetivo e independiente sobre los asuntos corporativos, incluyendo aquellos que involucren conflictos de interés entre management, miembros del directorio y accionistas. Debe tener acceso a información precisa, relevante y oportuna.
                """,
                "source": "Principios OCDE",
                "category": "compliance",
                "date": "2015-11-24"
            },
            {
                "title": "Gestión de Riesgos Operacionales", 
                "content": """
                La gestión de riesgos operacionales es el proceso mediante el cual las organizaciones identifican, evalúan, mitigan y monitorean riesgos que puedan afectar el logro de objetivos organizacionales. Debe estar integrada en la planificación estratégica y operativa.

                El proceso incluye identificación sistemática de eventos de riesgo mediante técnicas como análisis de escenarios, revisión de incidentes históricos, auditorías internas y consultas con expertos; evaluación de probabilidad e impacto de eventos identificados; desarrollo de estrategias de tratamiento que pueden incluir evitación, mitigación, transferencia o aceptación del riesgo.

                Los controles internos son actividades realizadas por todos los niveles de personal para proporcionar seguridad razonable sobre el logro de objetivos organizacionales. Incluyen actividades preventivas, detectivas y correctivas. Deben ser apropiados, funcionar consistentemente según lo planeado, y ser costo-efectivos.

                El monitoreo continuo evalúa la calidad del desempeño del sistema de control interno a través del tiempo. Se realiza mediante actividades de monitoreo continuo, evaluaciones separadas, o combinación de ambas. Las deficiencias deben comunicarse oportunamente a quienes puedan tomar acciones correctivas.

                Los reportes de riesgo deben ser proporcionados regularmente a la alta dirección y directorio, incluyendo tendencias de riesgo, efectividad de controles, incidentes significativos y planes de acción para deficiencias identificadas.
                """,
                "source": "Marco COSO",
                "category": "compliance", 
                "date": "2017-06-01"
            }
        ]
        
        for doc_data in compliance_texts:
            doc = LegalDocument(
                title=doc_data["title"],
                content=self.clean_legal_text(doc_data["content"]),
                source=doc_data["source"],
                jurisdiction="multi",
                category=doc_data["category"],
                date=doc_data["date"],
                url="",
                concepts=self.classify_legal_concepts(doc_data["content"])
            )
            documents.append(doc)
        
        console.print(f"[green]✓ Extracted {len(documents)} compliance documents[/green]")
        return documents
    
    def build_training_corpus(self) -> Dict[str, List[LegalDocument]]:
        """Construye corpus completo para entrenamiento"""
        
        console.print("[bold yellow]Building comprehensive legal corpus...[/bold yellow]")
        
        all_documents = []
        
        # Extract from different sources
        all_documents.extend(self.extract_argentina_sources())
        all_documents.extend(self.extract_spain_sources())
        all_documents.extend(self.extract_compliance_sources())
        
        # Organize by categories
        corpus = {}
        for doc in all_documents:
            category = doc.category
            if category not in corpus:
                corpus[category] = []
            corpus[category].append(doc)
        
        # Save individual category files
        for category, docs in corpus.items():
            self.save_category_corpus(category, docs)
        
        # Save complete corpus
        self.save_complete_corpus(all_documents)
        
        # Generate statistics
        self.generate_corpus_statistics(corpus)
        
        console.print(f"[green]✓ Built corpus with {len(all_documents)} documents across {len(corpus)} categories[/green]")
        return corpus
    
    def save_category_corpus(self, category: str, documents: List[LegalDocument]):
        """Guarda corpus por categoría"""
        
        # JSONL format for training
        jsonl_path = self.output_dir / f"{category}_corpus.jsonl"
        with open(jsonl_path, 'w', encoding='utf-8') as f:
            for doc in documents:
                json_doc = {
                    "text": doc.content,
                    "title": doc.title,
                    "source": doc.source,
                    "jurisdiction": doc.jurisdiction,
                    "category": doc.category,
                    "date": doc.date,
                    "concepts": doc.concepts
                }
                f.write(json.dumps(json_doc, ensure_ascii=False) + '\n')
        
        # CSV format for analysis
        csv_path = self.output_dir / f"{category}_corpus.csv"
        df_data = []
        for doc in documents:
            df_data.append({
                "title": doc.title,
                "content": doc.content[:500] + "..." if len(doc.content) > 500 else doc.content,
                "source": doc.source,
                "jurisdiction": doc.jurisdiction,
                "category": doc.category,
                "date": doc.date,
                "concepts": "; ".join(doc.concepts),
                "text_length": len(doc.content)
            })
        
        pd.DataFrame(df_data).to_csv(csv_path, index=False, encoding='utf-8')
    
    def save_complete_corpus(self, documents: List[LegalDocument]):
        """Guarda corpus completo"""
        
        # Complete JSONL
        complete_path = self.output_dir / "complete_legal_corpus.jsonl"
        with open(complete_path, 'w', encoding='utf-8') as f:
            for doc in documents:
                json_doc = {
                    "text": doc.content,
                    "title": doc.title,
                    "source": doc.source,
                    "jurisdiction": doc.jurisdiction,
                    "category": doc.category,
                    "date": doc.date,
                    "concepts": doc.concepts
                }
                f.write(json.dumps(json_doc, ensure_ascii=False) + '\n')
        
        # Metadata JSON
        metadata = {
            "total_documents": len(documents),
            "categories": list(set(doc.category for doc in documents)),
            "jurisdictions": list(set(doc.jurisdiction for doc in documents)),
            "sources": list(set(doc.source for doc in documents)),
            "creation_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "description": "Legal corpus for SCM Legal training - Argentine and Spanish legal texts"
        }
        
        metadata_path = self.output_dir / "corpus_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def generate_corpus_statistics(self, corpus: Dict[str, List[LegalDocument]]):
        """Genera estadísticas del corpus"""
        
        stats = {}
        total_docs = 0
        total_chars = 0
        
        for category, docs in corpus.items():
            category_chars = sum(len(doc.content) for doc in docs)
            stats[category] = {
                "documents": len(docs),
                "total_characters": category_chars,
                "avg_characters": category_chars // len(docs) if docs else 0,
                "jurisdictions": list(set(doc.jurisdiction for doc in docs)),
                "sources": list(set(doc.source for doc in docs))
            }
            total_docs += len(docs)
            total_chars += category_chars
        
        stats["total"] = {
            "documents": total_docs,
            "total_characters": total_chars,
            "avg_characters": total_chars // total_docs if total_docs else 0,
            "categories": len(corpus)
        }
        
        # Save statistics
        stats_path = self.output_dir / "corpus_statistics.json"
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        # Display statistics
        console.print("\n[bold yellow]Corpus Statistics:[/bold yellow]")
        console.print(f"Total documents: {stats['total']['documents']}")
        console.print(f"Total characters: {stats['total']['total_characters']:,}")
        console.print(f"Average document length: {stats['total']['avg_characters']:,} characters")
        console.print(f"Categories: {stats['total']['categories']}")
        
        for category, cat_stats in stats.items():
            if category != "total":
                console.print(f"  {category}: {cat_stats['documents']} docs ({cat_stats['total_characters']:,} chars)")

def main():
    """Función principal para construir corpus legal"""
    
    console.print("[bold green]Legal Corpus Builder for SCM Training[/bold green]")
    console.print("[blue]======================================[/blue]")
    
    # Initialize builder
    builder = LegalCorpusBuilder()
    
    # Build corpus
    corpus = builder.build_training_corpus()
    
    console.print(f"\n[green]✅ Corpus building completed![/green]")
    console.print(f"[blue]Output directory: {builder.output_dir}[/blue]")
    console.print(f"[blue]Files created:[/blue]")
    
    for file in builder.output_dir.glob("*"):
        console.print(f"  - {file.name}")

if __name__ == "__main__":
    main()