"""
Modèles Pydantic pour Structured Outputs OpenAI
Garantit une structure JSON stricte et des catégories prédéfinies
"""
from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional, Any


# ==================== ENUMS STRICTS ====================

class ElementCategory(str, Enum):
    """Types d'éléments sources - LISTE FERMÉE"""
    EXCEL = "Excel"
    PDF = "PDF"
    EMAIL = "Email"
    PAPIER = "Papier"
    BDD = "BDD"
    IMAGE = "Image"
    WORD = "Word"
    FORMULAIRE = "Formulaire"
    ERP_CRM = "ERP_CRM"
    AUDIO = "Audio"
    AUTRE = "Autre"


class ComplexityLevel(str, Enum):
    """Catégorie de sources - LISTE FERMÉE"""
    STANDARD = "Standard"
    INTERMEDIAIRE = "Intermédiaire"
    COMPLEXE = "Complexe"
    NON_STANDARDISEE = "Non standardisée"


class PainPoint(str, Enum):
    """Pain points identifiés - LISTE FERMÉE"""
    REPETITIVITE = "Répétitivité"
    ERREURS = "Erreurs fréquentes"
    LENTEUR = "Lenteur"
    COMPLEXITE = "Complexité"
    COORDINATION = "Coordination difficile"
    CONFORMITE = "Risque conformité"
    VISIBILITE = "Manque visibilité"
    VOLUME = "Volume élevé"


class Benefit(str, Enum):
    """Bénéfices attendus - LISTE FERMÉE"""
    TEMPS = "Gain de temps"
    QUALITE = "Amélioration qualité"
    COUTS = "Réduction coûts"
    SATISFACTION = "Satisfaction utilisateurs"
    CONFORMITE = "Conformité"
    TRACABILITE = "Traçabilité"
    COLLABORATION = "Meilleure collaboration"


class Priority(str, Enum):
    """Priorité - LISTE FERMÉE"""
    QUICK_WIN = "Quick win"
    CHALLENGER = "À challenger"
    LONG_SHOT = "Long shot"


class DevTime(str, Enum):
    """Temps de développement estimé - LISTE FERMÉE"""
    TRES_RAPIDE = "1-2 semaines"
    RAPIDE = "3-4 semaines"
    MOYEN = "1-2 mois"
    LONG = "3-4 mois"
    TRES_LONG = "6+ mois"


# ==================== MODÈLES IMBRIQUÉS ====================

class UserStory(BaseModel):
    """User story générée - Format: En tant que X, j'ai besoin de Y afin de Z (max 100 mots)"""
    model_config = {"extra": "forbid"}
    
    project_name: str
    html: str
    word_count: int = Field(ge=0, le=100)


class ExecutionStep(BaseModel):
    """Une étape d'exécution"""
    model_config = {"extra": "forbid"}
    
    step: int = Field(ge=1)
    description: str


class ExecutionSchema(BaseModel):
    """Schéma d'exécution - Diagramme ASCII uniquement"""
    model_config = {"extra": "forbid"}
    
    ascii_diagram: str


class ElementSource(BaseModel):
    """Un type d'élément source"""
    model_config = {"extra": "forbid"}
    
    category: ElementCategory
    description: str


class ElementsSources(BaseModel):
    """Éléments sources de la tâche"""
    model_config = {"extra": "forbid"}
    
    types: List[ElementSource]
    count: int = Field(ge=0)  # Nombre de types uniques
    total_sources: int = Field(ge=0)  # Nombre total de sources
    complexity_level: ComplexityLevel


class DeliveryPhase(BaseModel):
    """Une phase de delivery"""
    model_config = {"extra": "forbid"}
    
    phase: int = Field(ge=1)
    name: str
    feature_principale: str
    risque_principal: str
    duration: str


class QuickWin(BaseModel):
    """Action en attendant l'automatisation - côté utilisateur"""
    model_config = {"extra": "forbid"}
    
    action: str
    impact: str


class Delivery(BaseModel):
    """Plan de delivery"""
    model_config = {"extra": "forbid"}
    
    dev_time: DevTime
    phases: List[DeliveryPhase]
    quick_wins: List[QuickWin]


class ProConArgument(BaseModel):
    """Un argument pro ou con"""
    model_config = {"extra": "forbid"}
    
    argument: str
    weight: str


class ProCon(BaseModel):
    """Arguments pour et contre le projet"""
    model_config = {"extra": "forbid"}
    
    pros: List[ProConArgument]
    cons: List[ProConArgument]


class Scoring(BaseModel):
    """Scoring détaillé sur 100"""
    model_config = {"extra": "forbid"}
    
    impact_business_score: str  # Format: "17/40"
    faisabilite_technique_score: str  # Format: "27/30"
    urgence_score: str  # Format: "24/30"
    total: int = Field(ge=0, le=100)
    formula: str
    justification: str
    gain_temps_mensuel_heures: int = Field(ge=0)


class Analysis(BaseModel):
    """Analyse qualitative"""
    model_config = {"extra": "forbid"}
    
    pain_points: List[PainPoint]
    benefits: List[Benefit]
    feasibility_score: int = Field(ge=0, le=100)
    priority: Priority


# ==================== SCHÉMA PRINCIPAL ====================

class FormAnalysisResponseWithoutScoring(BaseModel):
    """
    Réponse structurée de l'analyse du formulaire SANS le scoring.
    Le scoring sera calculé côté backend Python.
    """
    model_config = {"extra": "forbid"}
    
    user_story: UserStory
    execution_schema: ExecutionSchema
    elements_sources: ElementsSources
    analysis: Analysis
    pro_con: ProCon
    delivery: Delivery


class FormAnalysisResponse(BaseModel):
    """
    Réponse structurée complète de l'analyse du formulaire.
    STRUCTURE FIXE - Toujours les mêmes champs.
    """
    model_config = {"extra": "forbid"}
    
    user_story: UserStory
    execution_schema: ExecutionSchema
    elements_sources: ElementsSources
    analysis: Analysis
    pro_con: ProCon
    scoring: Scoring
    delivery: Delivery


# ==================== REQUÊTE ====================

class FormData(BaseModel):
    """Données du formulaire soumises pour analyse"""
    q1: Optional[str] = None  # Nom
    q2: Optional[str] = None  # Prénom
    q3: Optional[str] = None  # Rôle
    q4: Optional[str] = None  # Département
    q5: Optional[str] = None  # Brief utilisateur
    q6: Optional[str] = None  # Exécution actuelle
    q7: Optional[str] = None  # Fréquence
    q8: Optional[str] = None  # Nb exécutions
    q9: Optional[str] = None  # Temps unitaire
    q10: Optional[str] = None  # Nb personnes
    q11: Optional[str] = None  # Niveau irritant
    q12: Optional[str] = None  # Pourquoi irritant
    q13: Optional[str] = None  # Pourquoi urgent
    q14: Optional[str] = None  # Éléments sources
    q15: Optional[str] = None  # Action manuelle
    q16: Optional[str] = None  # Exemple action manuelle
    q17: Optional[str] = None  # Règles simples
    q18: Optional[str] = None  # Points complexes
    q19: Optional[str] = None  # Complexité orga
    q20: Optional[str] = None  # Outils


class AnalyzeRequest(BaseModel):
    """Requête d'analyse"""
    form_data: FormData

