from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from ..utils.database import get_db
from ..routers.user import get_current_user
from ..services.hexaco_service import HexacoService
from ..services.hexaco_scoring_service import HexacoScoringService
from ..services.LLMhexaco_service import LLMHexacoService
import logging

# Configuration du logging
logger = logging.getLogger(__name__)

# Configuration du router
router = APIRouter(prefix="/api/tests/hexaco", tags=["hexaco_test"])

# Initialisation des services
hexaco_service = HexacoService()
scoring_service = HexacoScoringService()
llm_service = LLMHexacoService()

# Modèles Pydantic pour les requêtes/réponses
class HexacoMetadata(BaseModel):
    versions: Dict[str, Any]
    languages: Dict[str, Any]
    domains: Dict[str, Any]

class HexacoVersion(BaseModel):
    id: str
    title: str
    description: str
    item_count: int
    estimated_duration: int
    language: str
    active: bool

class HexacoQuestion(BaseModel):
    item_id: int
    item_text: str
    response_min: int
    response_max: int
    version: str
    language: str
    reverse_keyed: bool
    facet: str

class HexacoAnswerRequest(BaseModel):
    session_id: str
    item_id: int
    response_value: int
    response_time_ms: Optional[int] = None

class HexacoScoreResponse(BaseModel):
    domains: Dict[str, float]
    facets: Dict[str, float]
    percentiles: Dict[str, float]
    reliability: Dict[str, float]
    total_responses: int
    completion_rate: float
    narrative_description: Optional[str] = None

class SessionResponse(BaseModel):
    session_id: str
    message: str

class ProgressResponse(BaseModel):
    total_items: int
    completed_items: int
    progress_percentage: float
    status: str
    assessment_version: str

class StartTestRequest(BaseModel):
    version_id: str

@router.get("/", response_model=HexacoMetadata)
async def get_hexaco_metadata():
    """
    Retourne les métadonnées générales du test HEXACO-PI-R.
    """
    try:
        versions = hexaco_service.get_available_versions()
        languages = hexaco_service.get_available_languages()
        domains = hexaco_service.get_domains_config()
        
        return HexacoMetadata(
            versions=versions,
            languages=languages,
            domains=domains
        )
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des métadonnées HEXACO: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des métadonnées: {str(e)}"
        )

@router.get("/languages", response_model=Dict[str, Any])
async def get_available_languages():
    """
    Retourne les langues disponibles pour le test HEXACO.
    """
    try:
        return hexaco_service.get_available_languages()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des langues: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des langues: {str(e)}"
        )

@router.get("/versions", response_model=Dict[str, Any])
async def get_available_versions(language: Optional[str] = Query(None)):
    """
    Retourne les versions disponibles du test HEXACO, optionnellement filtrées par langue.
    """
    try:
        all_versions = hexaco_service.get_available_versions()
        
        if language:
            filtered_versions = {
                version_id: version_data 
                for version_id, version_data in all_versions.items()
                if version_data.get("language") == language and version_data.get("active", False)
            }
            return filtered_versions
        
        return all_versions
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des versions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des versions: {str(e)}"
        )

@router.post("/start", response_model=SessionResponse)
async def start_hexaco_test(
    request: StartTestRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Démarre une nouvelle session de test HEXACO.
    """
    try:
        # Vérifier que la version existe
        version_metadata = hexaco_service.get_version_metadata(request.version_id)
        if not version_metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Version de test non trouvée: {request.version_id}"
            )
        
        if not version_metadata.get("active", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Version de test inactive: {request.version_id}"
            )
        
        # Créer la session d'évaluation
        session_id = hexaco_service.create_assessment_session(
            db, current_user.id, request.version_id
        )
        
        logger.info(f"Session HEXACO démarrée: {session_id} pour utilisateur {current_user.id}")
        return SessionResponse(
            session_id=session_id,
            message="Session de test HEXACO créée avec succès"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors du démarrage du test HEXACO: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du démarrage du test: {str(e)}"
        )

@router.get("/questions", response_model=List[HexacoQuestion])
async def get_hexaco_questions(
    version_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Retourne les questions pour une version spécifique du test HEXACO.
    """
    try:
        # Vérifier que la version existe
        version_metadata = hexaco_service.get_version_metadata(version_id)
        if not version_metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Version de test non trouvée: {version_id}"
            )
        
        # Récupérer les questions
        questions = hexaco_service.get_questions_for_version(version_id)
        
        logger.info(f"Questions HEXACO récupérées: {len(questions)} pour version {version_id}")
        return [HexacoQuestion(**question) for question in questions]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des questions HEXACO: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des questions: {str(e)}"
        )

@router.post("/answer", status_code=status.HTTP_201_CREATED)
async def save_hexaco_answer(
    answer: HexacoAnswerRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Sauvegarde une réponse individuelle au test HEXACO.
    """
    try:
        # Valider la valeur de réponse (échelle 1-5 pour HEXACO)
        if not (1 <= answer.response_value <= 5):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La valeur de réponse doit être entre 1 et 5"
            )
        
        # Sauvegarder la réponse
        success = hexaco_service.save_response(
            db, answer.session_id, answer.item_id, 
            answer.response_value, answer.response_time_ms
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Impossible de sauvegarder la réponse"
            )
        
        logger.info(f"Réponse HEXACO sauvegardée: session={answer.session_id}, item={answer.item_id}")
        return {"message": "Réponse sauvegardée avec succès"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde de la réponse HEXACO: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la sauvegarde de la réponse: {str(e)}"
        )

@router.get("/progress/{session_id}", response_model=ProgressResponse)
async def get_test_progress(
    session_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Retourne le progrès d'une session de test HEXACO.
    """
    try:
        progress = hexaco_service.get_assessment_progress(db, session_id)
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session de test non trouvée"
            )
        
        return ProgressResponse(**progress)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du progrès: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération du progrès: {str(e)}"
        )

@router.get("/score/{session_id}", response_model=HexacoScoreResponse)
async def get_hexaco_score(
    session_id: str,
    include_description: bool = Query(False),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Calcule et retourne les scores HEXACO pour une session de test.
    """
    try:
        # Récupérer les réponses de l'utilisateur
        responses = hexaco_service.get_user_responses(db, session_id)
        if not responses:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aucune réponse trouvée pour cette session"
            )
        
        # Récupérer les informations de la session
        progress = hexaco_service.get_assessment_progress(db, session_id)
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session de test non trouvée"
            )
        
        assessment_version = progress["assessment_version"]
        
        # Récupérer les questions pour cette version
        questions = hexaco_service.get_questions_for_version(assessment_version)
        
        # Calculer les scores HEXACO
        scores = scoring_service.calculate_hexaco_scores(responses, questions)
        
        # Récupérer les métadonnées de version et langue
        version_metadata = hexaco_service.get_version_metadata(assessment_version)
        language = version_metadata.get("language", "fr") if version_metadata else "fr"
        
        # Générer l'analyse LLM (toujours, pas seulement si demandée)
        narrative_description = None
        try:
            # Récupérer le contexte utilisateur pour une description plus personnalisée
            user_context = {
                "user_id": current_user.id,
                "assessment_version": assessment_version
            }
            
            narrative_description = await llm_service.generate_hexaco_profile_description(
                hexaco_scores=scores,
                user_profile=user_context,
                language=language
            )
            logger.info(f"Analyse LLM HEXACO générée avec succès pour utilisateur {current_user.id}")
        except Exception as e:
            logger.warning(f"Erreur lors de la génération de la description LLM: {e}")
            narrative_description = "Description personnalisée temporairement indisponible"
        
        # Sauvegarder le profil calculé avec l'analyse LLM
        scoring_service.save_hexaco_profile(
            db, current_user.id, session_id, scores,
            assessment_version, language, narrative_description
        )
        
        # Marquer l'évaluation comme complétée
        hexaco_service.complete_assessment(db, session_id)
        
        result = HexacoScoreResponse(
            domains=scores["domains"],
            facets=scores["facets"],
            percentiles=scores["percentiles"],
            reliability=scores["reliability"],
            total_responses=scores["total_responses"],
            completion_rate=scores["completion_rate"],
            narrative_description=narrative_description if include_description else None
        )
        
        logger.info(f"Scores HEXACO calculés pour session {session_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors du calcul des scores HEXACO: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du calcul des scores: {str(e)}"
        )

@router.get("/profile/{user_id}", response_model=Optional[HexacoScoreResponse])
async def get_user_hexaco_profile(
    user_id: int,
    assessment_version: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Retourne le profil HEXACO d'un utilisateur.
    """
    try:
        # Vérifier que l'utilisateur peut accéder à ce profil
        if current_user.id != user_id:
            # TODO: Ajouter une vérification des permissions pour les administrateurs
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé à ce profil"
            )
        
        # Récupérer le profil
        profile = scoring_service.get_user_hexaco_profile(db, user_id, assessment_version)
        if not profile:
            return None
        
        scores_data = profile["scores"]
        result = HexacoScoreResponse(
            domains=scores_data.get("domains", {}),
            facets=scores_data.get("facets", {}),
            percentiles=profile.get("percentiles", {}),
            reliability=profile.get("reliability", {}),
            total_responses=scores_data.get("total_responses", 0),
            completion_rate=scores_data.get("completion_rate", 0.0),
            narrative_description=profile.get("narrative_description")
        )
        
        logger.info(f"Profil HEXACO récupéré pour utilisateur {user_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du profil HEXACO: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération du profil: {str(e)}"
        )

@router.get("/my-profile", response_model=Optional[HexacoScoreResponse])
async def get_my_hexaco_profile(
    assessment_version: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Retourne le profil HEXACO de l'utilisateur connecté.
    """
    return await get_user_hexaco_profile(current_user.id, assessment_version, db, current_user)

@router.get("/analysis/{user_id}", response_model=Dict[str, str])
async def get_hexaco_analysis(
    user_id: int,
    assessment_version: Optional[str] = Query(None),
    force_regenerate: bool = Query(False),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Retourne l'analyse LLM du profil HEXACO d'un utilisateur.
    Récupère l'analyse existante ou en génère une nouvelle si nécessaire.
    """
    try:
        # Vérifier que l'utilisateur peut accéder à cette analyse
        if current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé à cette analyse"
            )
        
        # Récupérer le profil HEXACO
        profile = scoring_service.get_user_hexaco_profile(db, user_id, assessment_version)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aucun profil HEXACO trouvé pour cet utilisateur"
            )
        
        # Récupérer ou générer l'analyse
        analysis = await llm_service.get_or_generate_personality_insights(
            user_id=user_id,
            hexaco_scores=profile["scores"],
            db_session=db,
            language=profile.get("language", "fr"),
            force_regenerate=force_regenerate
        )
        
        # Si une nouvelle analyse a été générée, mettre à jour la base de données
        if force_regenerate or not profile.get("narrative_description"):
            try:
                from sqlalchemy import text
                update_query = text("""
                    UPDATE personality_profiles
                    SET narrative_description = :narrative_description,
                        updated_at = NOW()
                    WHERE user_id = :user_id AND profile_type = 'hexaco'
                    AND (:assessment_version IS NULL OR assessment_version = :assessment_version)
                """)
                
                db.execute(update_query, {
                    "user_id": user_id,
                    "narrative_description": analysis,
                    "assessment_version": assessment_version
                })
                db.commit()
                logger.info(f"Analyse LLM mise à jour pour utilisateur {user_id}")
            except Exception as e:
                logger.warning(f"Erreur lors de la mise à jour de l'analyse: {e}")
                db.rollback()
        
        return {
            "analysis": analysis,
            "assessment_version": profile.get("assessment_version"),
            "language": profile.get("language", "fr"),
            "generated_at": profile.get("computed_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'analyse HEXACO: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération de l'analyse: {str(e)}"
        )

@router.get("/my-analysis", response_model=Dict[str, str])
async def get_my_hexaco_analysis(
    assessment_version: Optional[str] = Query(None),
    force_regenerate: bool = Query(False),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Retourne l'analyse LLM du profil HEXACO de l'utilisateur connecté.
    """
    return await get_hexaco_analysis(current_user.id, assessment_version, force_regenerate, db, current_user)