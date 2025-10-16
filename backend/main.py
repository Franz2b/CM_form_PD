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
    ElementCategory, ComplexityLevel, PainPoint, Benefit, Priority
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
    
    context = f"""
CONTEXTE FORMULAIRE - ANALYSE PROCESS DESIGNER

=== PERSONA ===
Nom: {d.q1 or '-'} {d.q2 or '-'}
Rôle: {d.q3 or '-'}
Département: {d.q4 or '-'}

=== BESOIN ===
Brief utilisateur:
{d.q5 or '-'}

Exécution actuelle:
{d.q6 or '-'}

=== VOLUMÉTRIE ===
Fréquence: {d.q7 or '-'}
Nb exécutions/occurrence: {d.q8 or '-'}
Temps unitaire: {d.q9 or '-'}
Nb personnes: {d.q10 or '-'}
Irritant: {d.q11 or '3'}/5
Pourquoi irritant: {d.q11a or '-'}
Pourquoi urgent: {d.q11b or '-'}

=== NATURE TÂCHE ===
Éléments sources: {d.q12 or '-'}
Action manuelle: {d.q13 or '-'}
Exemple action: {d.q13a or '-'}
Règles simples: {d.q14 or '-'}
Exemple complexité: {d.q14a or '-'}
Complexité orga: {d.q15 or '-'}
Outils: {d.q16 or '-'}

=== INSTRUCTIONS ===
1. USER STORY: Génère une user story HTML concise (max 100 mots) avec ce format EXACT:
   <p><strong>En tant que</strong> [rôle],</p>
   <p><strong>j'ai besoin de</strong> [besoin détaillé]</p>
   <p><strong>afin de</strong> [bénéfice concret].</p>
   
   IMPORTANT: Utilise des balises <p> pour chaque partie et <strong> uniquement sur "En tant que", "j'ai besoin de", "afin de".

2. EXECUTION SCHEMA: 
   - Crée un diagramme ASCII vertical avec les caractères: ┌─┐│└┘ et ▼
   - Liste les étapes extraites de "Exécution actuelle"
   
3. ELEMENTS SOURCES:
   - Analyse "Éléments sources" et catégorise STRICTEMENT avec les catégories prédéfinies
   - Compte le nombre de types différents
   - Détermine le niveau de complexité (Structuré/Semi-structuré/Non-structuré)

4. ANALYSIS:
   - Extrais les pain points du brief (UNIQUEMENT parmi la liste prédéfinie)
   - Identifie les bénéfices (UNIQUEMENT parmi la liste prédéfinie)
   - Calcule un score de faisabilité 0-100 basé sur: règles simples (+30), données structurées (+30), complexité orga simple (+20), peu d'actions manuelles (+20)
   - Détermine la priorité: >70 = Quick win, 45-70 = À challenger, <45 = Long shot
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


