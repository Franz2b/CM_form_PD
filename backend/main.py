import os
import json
import logging
import time
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None  # will error at runtime if missing

from models import (
    FormAnalysisResponse, AnalyzeRequest, FormData,
    ElementCategory, ComplexityLevel, PainPoint, Benefit, Priority, DevTime
)

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")

app = FastAPI(title="CM Form PD – AI Proxy", version="1.0.0")

# Log au démarrage
@app.on_event("startup")
async def startup_event():
    logger.info("=" * 80)
    logger.info("🚀 BACKEND DÉMARRÉ")
    logger.info("=" * 80)
    logger.info(f"Modèle OpenAI: {MODEL}")
    logger.info(f"API Key présente: {'✅' if os.environ.get('OPENAI_API_KEY') else '❌'}")
    logger.info("Endpoints disponibles:")
    logger.info("  - GET  /health")
    logger.info("  - POST /ai")
    logger.info("  - POST /analyze (Structured Outputs)")
    logger.info("=" * 80 + "\n")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AiRequest(BaseModel):
    prompt: str


class AiResponse(BaseModel):
    text: str


@app.get("/health")
def health():
    return {"ok": True, "model": MODEL}


@app.post("/ai", response_model=AiResponse)
async def ai(req: AiRequest):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY manquant dans l'environnement")
    if OpenAI is None:
        raise HTTPException(status_code=500, detail="Package openai manquant. Installez-le via requirements.txt")

    try:
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Tu es un assistant expert en design de processus et delivery produit."},
                {"role": "user", "content": req.prompt},
            ],
            temperature=0.2,
            max_tokens=900,
        )
        text = (resp.choices[0].message.content or "").strip()
        return AiResponse(text=text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/analyze", response_model=FormAnalysisResponse)
async def analyze_form(req: AnalyzeRequest):
    """
    Analyse structurée du formulaire avec Structured Outputs.
    Garantit une structure JSON fixe et des catégories strictes.
    """
    logger.info("=" * 80)
    logger.info("📥 NOUVELLE REQUÊTE D'ANALYSE")
    logger.info("=" * 80)
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY manquant")
    if OpenAI is None:
        raise HTTPException(status_code=500, detail="Package openai manquant")

    # Construire le prompt contextuel
    d = req.form_data
    logger.info(f"📋 Données formulaire reçues:")
    logger.info(f"   - Persona: {d.q1} {d.q2} ({d.q3} - {d.q4})")
    logger.info(f"   - Brief: {(d.q5 or '')[:100]}...")
    logger.info(f"   - Volumétrie: {d.q7} / {d.q8} exec / {d.q9} unitaire")
    
    # Construire le contexte (éviter les {} dans f-string)
    context = """
CONTEXTE FORMULAIRE - ANALYSE PROCESS DESIGNER

=== PERSONA ===
Nom: """ + (d.q1 or '-') + " " + (d.q2 or '-') + """
Rôle: """ + (d.q3 or '-') + """
Département: """ + (d.q4 or '-') + """

=== BESOIN ===
Brief utilisateur:
""" + (d.q5 or '-') + """

Exécution actuelle:
""" + (d.q6 or '-') + """

=== VOLUMÉTRIE ===
Fréquence: """ + (d.q7 or '-') + """
Nb exécutions/occurrence: """ + (d.q8 or '-') + """
Temps unitaire: """ + (d.q9 or '-') + """
Nb personnes: """ + (d.q10 or '-') + """
Irritant: """ + (d.q11 or '3') + """/5
Pourquoi irritant: """ + (d.q11a or '-') + """
Pourquoi urgent: """ + (d.q11b or '-') + """

=== NATURE TÂCHE ===
Éléments sources: """ + (d.q12 or '-') + """
Action manuelle: """ + (d.q13 or '-') + """
Exemple action: """ + (d.q13a or '-') + """
Règles simples: """ + (d.q14 or '-') + """
Exemple complexité: """ + (d.q14a or '-') + """
Complexité orga: """ + (d.q15 or '-') + """
Outils: """ + (d.q16 or '-') + """

=== INSTRUCTIONS ===
1. USER STORY: Génère une user story HTML (max 100 mots) AVEC CONTEXTE.
   Format: <p><strong>En tant que</strong> [rôle + contexte département/volumétrie],</p>
           <p><strong>j'ai besoin de</strong> [besoin détaillé]</p>
           <p><strong>afin de</strong> [bénéfice concret et mesurable].</p>
   Exemple: "En tant que comptable du service Finance traitant 50 factures quotidiennes..."

2. EXECUTION SCHEMA: Diagramme ASCII vertical + liste étapes

3. ELEMENTS SOURCES:
   - types: Catégorise STRICTEMENT chaque source/document mentionné avec UNE catégorie
   - count: Nombre de TYPES UNIQUES différents (ex: si "Excel GL" + "Excel OSB" = 1 seul type "Excel", donc count=1)
     IMPORTANT: Compte les types UNIQUES, pas le nombre total de sources!
     Exemple: "Factures PDF + Excel suivi + SAP" = 3 types (PDF, Excel, ERP_CRM)
     Exemple: "Excel GL + Excel OSB + SAP" = 2 types (Excel, ERP_CRM)
   - complexity_level: Structuré/Semi-structuré/Non-structuré

4. ANALYSIS: Pain points, bénéfices (LISTES STRICTES), score faisabilité, priorité

5. PRO/CON:
   - pros: 3-5 arguments POUR (volumétrie, ROI, urgence). Chaque: argument + weight (Faible/Moyen/Fort)
   - cons: 2-4 arguments CONTRE/risques. Chaque: argument + weight (Faible/Moyen/Fort)

6. SCORING sur 100:
   - impact_business_level: "Low" (<15/40) ou "Mid" (15-28/40) ou "High" (>28/40)
   - impact_business_score: Score 0-40
   - faisabilite_technique_level: "Low" / "Mid" / "High"
   - faisabilite_technique_score: Score 0-30
   - urgence_level: "Low" / "Mid" / "High"
   - urgence_score: Score 0-30
   - total: Somme des 3 scores
   - formula: Formule de calcul détaillée (ex: "Impact(35) + Faisabilité(22) + Urgence(25) = 82/100")

7. DELIVERY:
   - dev_time: Temps total
   - phases (2-3): Phases SIMPLES et ACTIONNABLES
     Chaque phase: 
     * name: Nom simple (ex: "POC", "MVP", "Production")
     * actions: Description courte et actionnable de ce qui sera fait
     * duration: Durée estimée
     * main_difficulty: UNE phrase très succincte sur la difficulté principale qui porte le délai
   - quick_wins (3-5): "En attendant, essaye de..." (UNIQUEMENT utilisateur)
"""

    try:
        client = OpenAI(api_key=api_key)
        
        # Vérifier que le modèle supporte Structured Outputs
        if MODEL not in ["gpt-4o", "gpt-4o-mini", "gpt-4o-2024-08-06"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Modèle {MODEL} ne supporte pas Structured Outputs. Utilisez gpt-4o ou gpt-4o-mini"
            )
        
        # Générer le schéma JSON
        schema = FormAnalysisResponse.model_json_schema()
        
        logger.info("\n" + "=" * 80)
        logger.info("🤖 APPEL OPENAI")
        logger.info("=" * 80)
        logger.info(f"Modèle: {MODEL}")
        system_prompt = "Tu es un expert en analyse de processus métier et automatisation. Tu dois analyser un formulaire et produire une réponse JSON STRICTEMENT conforme au schéma fourni. Utilise UNIQUEMENT les catégories prédéfinies dans les enums."
        
        logger.info(f"\n📤 MESSAGES ENVOYÉS À OPENAI:")
        logger.info("-" * 80)
        logger.info(f"SYSTEM: {system_prompt}")
        logger.info("")
        logger.info(f"USER:\n{context}")
        logger.info("-" * 80)
        logger.info("\n⏳ Appel OpenAI en cours...")
        
        # Chronomètre
        start_time = time.time()
        
        # Appel avec Structured Outputs
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": context
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "form_analysis_response",
                    "strict": True,
                    "schema": schema
                }
            },
            temperature=0.3,
            max_tokens=2000
        )
        
        # Temps écoulé
        elapsed = time.time() - start_time
        logger.info(f"✅ Réponse OpenAI reçue en {elapsed:.2f}s")
        
        # Tokens utilisés
        if hasattr(response, 'usage') and response.usage:
            logger.info(f"📊 Tokens utilisés:")
            logger.info(f"   - Prompt: {response.usage.prompt_tokens}")
            logger.info(f"   - Completion: {response.usage.completion_tokens}")
            logger.info(f"   - Total: {response.usage.total_tokens}")
        
        # Parse et valide avec Pydantic
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Réponse OpenAI vide")
        
        logger.info("\n📥 RÉPONSE OPENAI (JSON):")
        logger.info("-" * 80)
        # Pretty print du JSON
        try:
            formatted_json = json.dumps(json.loads(content), indent=2, ensure_ascii=False)
            logger.info(formatted_json)
        except:
            logger.info(content)
        logger.info("-" * 80)
        
        # Parse JSON
        result_json = json.loads(content)
        logger.info("\n✅ JSON parsé avec succès")
        logger.info(f"📊 Aperçu:")
        logger.info(f"   - User story: {result_json.get('user_story', {}).get('word_count', 0)} mots")
        logger.info(f"   - Étapes: {len(result_json.get('execution_schema', {}).get('steps', []))}")
        logger.info(f"   - Éléments sources: {result_json.get('elements_sources', {}).get('count', 0)} types")
        logger.info(f"   - Complexité: {result_json.get('elements_sources', {}).get('complexity_level', '?')}")
        logger.info(f"   - Faisabilité: {result_json.get('analysis', {}).get('feasibility_score', 0)}/100")
        logger.info(f"   - Priorité: {result_json.get('analysis', {}).get('priority', '?')}")
        logger.info(f"   - Scoring: Impact={result_json.get('scoring', {}).get('impact_business_level', '?')}, Faisabilité={result_json.get('scoring', {}).get('faisabilite_technique_level', '?')}, Urgence={result_json.get('scoring', {}).get('urgence_level', '?')}")
        logger.info(f"   - Score total: {result_json.get('scoring', {}).get('total', '?')}/100")
        logger.info(f"   - Pro/Con: {len(result_json.get('pro_con', {}).get('pros', []))} pros / {len(result_json.get('pro_con', {}).get('cons', []))} cons")
        logger.info(f"   - Temps dev: {result_json.get('delivery', {}).get('dev_time', '?')}")
        logger.info(f"   - Phases: {len(result_json.get('delivery', {}).get('phases', []))}")
        logger.info(f"   - Quick wins: {len(result_json.get('delivery', {}).get('quick_wins', []))}")
        
        # Validation Pydantic
        validated_result = FormAnalysisResponse(**result_json)
        logger.info("\n✅ Validation Pydantic OK")
        logger.info("=" * 80 + "\n")
        
        return validated_result
        
    except HTTPException:
        raise
    except json.JSONDecodeError as e:
        logger.error(f"❌ Erreur parsing JSON: {str(e)}")
        raise HTTPException(status_code=502, detail=f"Erreur parsing JSON: {str(e)}")
    except Exception as e:
        # Log détaillé de l'erreur
        import traceback
        logger.error("❌ ERREUR OPENAI:")
        logger.error(traceback.format_exc())
        error_detail = f"Erreur OpenAI: {str(e)}"
        raise HTTPException(status_code=502, detail=error_detail)


