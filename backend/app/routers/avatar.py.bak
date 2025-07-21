from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import logging

from ..utils.database import get_db
from ..models.user import User
from ..models.user_representation import UserRepresentation
from ..services.avatar_service import AvatarService
from ..routers.user import get_current_user

# Configuration du logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/avatar", tags=["avatar"])

@router.post("/generate-avatar/me")
async def generate_avatar(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Génère un avatar personnalisé pour l'utilisateur authentifié.
    
    Args:
        db: Session de base de données
        current_user: Utilisateur authentifié
        
    Returns:
        Dict contenant les informations de l'avatar généré
    """
    try:
        user_id = current_user.id
        
        logger.info(f"Début de la génération d'avatar pour l'utilisateur {user_id}")
        
        # Collecter les données utilisateur pour la génération d'avatar
        user_data = await _collect_user_data(db, user_id)
        
        # Étape 1: Générer la description d'avatar
        logger.info("Génération de la description d'avatar...")
        avatar_description = await AvatarService.generate_avatar_description(
            user_data=user_data,
            language="fr"
        )
        
        if not avatar_description:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la génération de la description d'avatar"
            )
        
        # Générer un nom d'avatar basé sur les données utilisateur
        avatar_name = _generate_avatar_name(user_data)
        
        # Étape 2: Générer l'image avec DALL-E
        logger.info("Génération de l'image d'avatar...")
        image_url = await AvatarService.generate_avatar_image(avatar_description)
        
        local_image_url = None
        if image_url:
            # Étape 3: Télécharger et sauvegarder l'image localement
            logger.info("Téléchargement et sauvegarde de l'image...")
            local_image_url = await AvatarService.download_and_save_image(
                image_url, user_id
            )
        
        # Étape 4: Mettre à jour la base de données
        logger.info("Mise à jour de la base de données...")
        user_representation = await AvatarService.update_user_avatar(
            db=db,
            user_id=user_id,
            avatar_name=avatar_name,
            avatar_description=avatar_description,
            avatar_image_url=local_image_url
        )
        
        logger.info(f"Avatar généré avec succès pour l'utilisateur {user_id}")
        
        # Retourner les informations de l'avatar
        return {
            "success": True,
            "message": "Avatar généré avec succès",
            "avatar_name": avatar_name,
            "avatar_description": avatar_description,
            "avatar_image_url": local_image_url,
            "generated_at": user_representation.generated_at.isoformat()
        }
        
    except HTTPException:
        # Re-lever les HTTPException sans les modifier
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la génération d'avatar pour l'utilisateur {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne lors de la génération d'avatar: {str(e)}"
        )

@router.get("/me")
async def get_user_avatar(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère l'avatar de l'utilisateur authentifié.
    
    Args:
        db: Session de base de données
        current_user: Utilisateur authentifié
        
    Returns:
        Dict contenant les informations de l'avatar
    """
    try:
        user_id = current_user.id
        
        # Récupérer la représentation utilisateur avec avatar
        user_repr = db.query(UserRepresentation).filter(
            UserRepresentation.user_id == user_id,
            UserRepresentation.source == "avatar_generation"
        ).first()
        
        if not user_repr or not user_repr.avatar_name:
            return {
                "success": False,
                "message": "Aucun avatar trouvé pour cet utilisateur",
                "avatar_name": None,
                "avatar_description": None,
                "avatar_image_url": None
            }
        
        return {
            "success": True,
            "avatar_name": user_repr.avatar_name,
            "avatar_description": user_repr.avatar_description,
            "avatar_image_url": user_repr.avatar_image_url,
            "generated_at": user_repr.generated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération d'avatar pour l'utilisateur {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne lors de la récupération d'avatar: {str(e)}"
        )

async def _collect_user_data(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Collecte les données utilisateur pour la génération d'avatar.
    
    Args:
        db: Session de base de données
        user_id: ID de l'utilisateur
        
    Returns:
        Dict contenant les données utilisateur
    """
    user_data = {"user_id": user_id}
    
    try:
        # Récupérer l'utilisateur
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user_data["email"] = user.email
            
            # Récupérer le profil utilisateur s'il existe
            if hasattr(user, 'profile') and user.profile:
                profile = user.profile
                user_data["profile"] = {
                    "first_name": getattr(profile, 'first_name', None),
                    "last_name": getattr(profile, 'last_name', None),
                    "age": getattr(profile, 'age', None),
                    "location": getattr(profile, 'location', None),
                    "bio": getattr(profile, 'bio', None)
                }
            
            # Récupérer les compétences utilisateur
            if hasattr(user, 'skills') and user.skills:
                user_data["skills"] = user.skills
            
            # Récupérer les représentations existantes
            representations = db.query(UserRepresentation).filter(
                UserRepresentation.user_id == user_id
            ).all()
            
            if representations:
                user_data["representations"] = [
                    {
                        "source": repr.source,
                        "summary": repr.summary,
                        "data": repr.data
                    }
                    for repr in representations
                ]
        
    except Exception as e:
        logger.warning(f"Erreur lors de la collecte des données utilisateur {user_id}: {str(e)}")
    
    return user_data

def _generate_avatar_name(user_data: Dict[str, Any]) -> str:
    """
    Génère un nom d'avatar basé sur les données utilisateur.
    
    Args:
        user_data: Données de l'utilisateur
        
    Returns:
        str: Nom de l'avatar
    """
    try:
        # Essayer d'utiliser le prénom si disponible
        if "profile" in user_data and user_data["profile"].get("first_name"):
            first_name = user_data["profile"]["first_name"]
            return f"Avatar de {first_name}"
        
        # Sinon, utiliser l'email
        if "email" in user_data:
            email_prefix = user_data["email"].split("@")[0]
            return f"Avatar de {email_prefix}"
        
        # Par défaut
        return f"Avatar Utilisateur {user_data.get('user_id', 'Inconnu')}"
        
    except Exception:
        return f"Avatar Utilisateur {user_data.get('user_id', 'Inconnu')}"

@router.post("/generate-avatar-test/{user_id}")
async def generate_avatar_test(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Version de test pour générer un avatar sans authentification.
    À utiliser uniquement en développement.
    """
    try:
        # Vérifier que l'utilisateur existe
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )

        logger.info(f"Début de la génération d'avatar pour l'utilisateur {user_id} (mode test)")

        # Collecter les données utilisateur pour la génération d'avatar
        user_data = await _collect_user_data(db, user_id)

        # Étape 1: Générer la description d'avatar
        logger.info("Génération de la description d'avatar...")
        avatar_description = await AvatarService.generate_avatar_description(
            user_data=user_data,
            language="fr"
        )

        if not avatar_description:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la génération de la description d'avatar"
            )

        # Générer un nom d'avatar basé sur les données utilisateur
        avatar_name = _generate_avatar_name(user_data)

        # Étape 2: Générer l'image avec DALL-E
        logger.info("Génération de l'image d'avatar...")
        image_url = await AvatarService.generate_avatar_image(avatar_description)

        # Étape 3: Télécharger et sauvegarder l'image localement (si générée)
        local_image_url = None
        if image_url:
            logger.info("Téléchargement et sauvegarde de l'image...")
            local_image_url = await AvatarService.save_avatar_image(image_url, user_id)

        # Étape 4: Mettre à jour la base de données
        logger.info("Mise à jour de la base de données...")
        user_representation = await AvatarService.update_user_avatar(
            db=db,
            user_id=user_id,
            avatar_name=avatar_name,
            avatar_description=avatar_description,
            avatar_image_url=local_image_url
        )

        logger.info(f"Avatar généré avec succès pour l'utilisateur {user_id}")

        # Retourner les informations de l'avatar
        return {
            "success": True,
            "message": "Avatar généré avec succès",
            "avatar_name": avatar_name,
            "avatar_description": avatar_description,
            "avatar_image_url": local_image_url,
            "generated_at": user_representation.generated_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la génération d'avatar pour l'utilisateur {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne lors de la génération d'avatar: {str(e)}"
        )