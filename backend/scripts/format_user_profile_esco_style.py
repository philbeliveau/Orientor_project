import os
import sys
from typing import Dict, Any, List, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Vérifier les dépendances requises
DEPENDENCIES_MET = True
MISSING_DEPENDENCIES = []

try:
    from dotenv import load_dotenv
except ImportError:
    DEPENDENCIES_MET = False
    MISSING_DEPENDENCIES.append("python-dotenv")

try:
    from langchain.prompts import PromptTemplate
    from langchain.schema.runnable import RunnableSequence
except ImportError:
    DEPENDENCIES_MET = False
    MISSING_DEPENDENCIES.append("langchain")

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    DEPENDENCIES_MET = False
    MISSING_DEPENDENCIES.append("langchain-openai")

# Fonction pour vérifier les dépendances
def check_dependencies():
    """Vérifie si toutes les dépendances sont installées et affiche un message d'erreur si ce n'est pas le cas."""
    if not DEPENDENCIES_MET:
        print("Erreur: Certaines dépendances requises ne sont pas installées.")
        print("Veuillez installer les packages suivants:")
        for dep in MISSING_DEPENDENCIES:
            print(f"  - {dep}")
        print("\nVous pouvez les installer avec la commande:")
        print(f"pip install {' '.join(MISSING_DEPENDENCIES)}")
        return False
    return True

# Charger les variables d'environnement si la dépendance est disponible
if "dotenv" not in MISSING_DEPENDENCIES:
    load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Templates de prompts pour les différents formateurs ESCO

# 1. Template pour le formateur d'occupation ESCO
ESCO_OCCUPATION_TEMPLATE = """
You are converting a user's background and career goal into a structured occupation entry, aligned with the ESCO standard. This is for a semantic graph-based career guidance platform.

You must fill in the following three fields using the user's profile data:

- PREFERREDLABEL: A concise, ESCO-style occupation title (1–5 words)
- ALTLABELS: A list of synonyms or variations for the occupation
- DESCRIPTION: A full paragraph explaining what this role involves

Use professional tone. Be objective and consistent with ESCO formatting style (no first person, no emotional tone).

### INPUT

User Story: {story}
User Career Goal: {career_goals}
Academic Background: {education_level} in {major}
Years of Experience: {years_experience}
Job Title: {job_title}
Top Rated Skills: {top_skills}
Top 3 RIASEC Code: {top_riasec}
interests: {interests}

### OUTPUT FORMAT

PREFERREDLABEL: ...
ALTLABELS: ...
DESCRIPTION: ...
"""

# 2. Template pour le formateur de compétence ESCO
ESCO_SKILL_TEMPLATE = """
You are rewriting a user's self-assessed skill into a professional ESCO-style skill description.

Your task is to generate a short, active-voice sentence that shows how this skill is applied in real life — grounded in the user's story and field of study.

Use an action verb. Do NOT say "good at" or "has strong".

### INPUT

Skill Name: {skill_name}
Skill Score (1.0–5.0): {skill_score}
User Story: {story}
Academic Background: {education_level} in {major}
Job Title: {job_title}
Years of Experience: {years_experience}
Career Goal: {career_goals}

### OUTPUT FORMAT

{skill_name}: [single active-voice sentence about how it is used]
"""

# 3. Template pour le formateur de groupe de compétences ESCO
ESCO_SKILLGROUP_TEMPLATE = """
You are summarizing a cluster of user skills into an ESCO-style skill group descriptor.

These are not actions. Your goal is to define the **theme** or **domain** covered by these skills in one clear sentence.

DO NOT describe what the user does.
DO NOT list individual skills.
Just summarize the type of thinking or work this skill group supports.

### INPUT

Skill Cluster Label: {group_label}
Included Skills: {skill_names}
Academic Background: {education_level} in {major}
User Story: {story}
Top 3 RIASEC Code: {top_riasec}

### OUTPUT FORMAT

{group_label}: [summary of what this group enables or involves]
"""

# 4. Template pour le formateur de profil complet ESCO
ESCO_FULL_PROFILE_TEMPLATE = """
You are writing a full structured profile for a user based on the ESCO classification tone and format.  
This profile is used to map the user into a graph of occupations, skills, and competencies.  
It must be dense, formal, and follow ESCO-style tone — suitable for embedding.

Build this full profile by combining:
- One ESCO-style occupation description
- One ESCO-style skill group summary
- 3 to 5 ESCO-style skill application sentences
- One academic/career background paragraph

Keep the format structured and markdown-friendly.

### INPUT

PREFERREDLABEL: {preferred_label}
ALTLABELS: {altlabels}
DESCRIPTION: {occupation_description}

SKILL GROUP:
{skill_group_label}: {skill_group_description}

KEY SKILLS:
- {skill_1}
- {skill_2}
- {skill_3}
- {skill_4} (if available)
- {skill_5} (if available)

BACKGROUND:
Name: {name}, Age: {age}, Gender: {sex}  
Education: {education_level} in {major}  
Experience: {years_experience} years in {job_title}  
Story: {story}  
Career Goal: {career_goals}  
RIASEC: {top_riasec}  
interests: {interests}

### OUTPUT

All sections above rewritten into one coherent, formal, ESCO-style user profile block suitable for semantic embedding.
"""

def format_esco_occupation(profile: Dict[str, Any], skills: Dict[str, float], riasec: Dict[str, str]) -> Optional[str]:
    """
    Formate un profil utilisateur selon le style d'occupation ESCO.
    
    Args:
        profile: Dictionnaire contenant les informations de base du profil utilisateur
        skills: Dictionnaire contenant les scores de compétences de l'utilisateur
        riasec: Dictionnaire contenant les résultats du test RIASEC
        
    Returns:
        Une chaîne formatée selon le style d'occupation ESCO
    """
    # Vérifier que toutes les dépendances sont installées
    if not check_dependencies():
        print("Impossible de formater le profil utilisateur: dépendances manquantes.")
        return None
        
    # Vérifier que la clé API OpenAI est disponible
    if not OPENAI_API_KEY:
        print("Erreur: La clé API OpenAI n'est pas définie dans les variables d'environnement.")
        print("Veuillez définir la variable d'environnement OPENAI_API_KEY.")
        return None
    
    # Extraire les compétences les mieux notées
    sorted_skills = sorted(skills.items(), key=lambda x: x[1], reverse=True)
    top_skills = ", ".join([skill for skill, _ in sorted_skills[:5]])
    
    # Extraire le code RIASEC
    top_riasec = riasec.get("top_3_code", "RCI")  # Valeur par défaut si manquante
    
    # Extraire les intérêts (ou utiliser une valeur par défaut)
    interests = profile.get("interests", "")
    
    # Créer un dictionnaire pour le prompt
    prompt_data = {
        "story": profile.get("story", ""),
        "career_goals": profile.get("career_goals", ""),
        "education_level": profile.get("education_level", ""),
        "major": profile.get("major", ""),
        "years_experience": profile.get("years_experience", 0),
        "job_title": profile.get("job_title", ""),
        "top_skills": top_skills,
        "top_riasec": top_riasec,
        "interests": interests
    }
    
    try:
        # Initialiser le modèle LLM
        llm = ChatOpenAI(
            model_name="gpt-4o",
            temperature=0.2,
            api_key=OPENAI_API_KEY
        )
        
        # Créer le template de prompt
        prompt = PromptTemplate(
            input_variables=list(prompt_data.keys()),
            template=ESCO_OCCUPATION_TEMPLATE
        )
        
        # Créer la séquence exécutable (nouvelle API recommandée)
        chain = prompt | llm
        
        # Exécuter la chaîne pour obtenir le profil formaté
        response = chain.invoke(prompt_data)
        formatted_profile = response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        print(f"Erreur lors du formatage du profil d'occupation ESCO: {str(e)}")
        return None
    
    # Nettoyer le résultat
    formatted_profile = formatted_profile.strip()
    
    return formatted_profile

def format_esco_skill(skill_name: str, skill_score: float, profile: Dict[str, Any]) -> Optional[str]:
    """
    Formate une compétence individuelle selon le style ESCO.
    
    Args:
        skill_name: Nom de la compétence
        skill_score: Score de la compétence (1.0-5.0)
        profile: Dictionnaire contenant les informations de base du profil utilisateur
        
    Returns:
        Une chaîne formatée selon le style de compétence ESCO
    """
    # Vérifier que toutes les dépendances sont installées
    if not check_dependencies():
        print("Impossible de formater la compétence: dépendances manquantes.")
        return None
        
    # Vérifier que la clé API OpenAI est disponible
    if not OPENAI_API_KEY:
        print("Erreur: La clé API OpenAI n'est pas définie dans les variables d'environnement.")
        print("Veuillez définir la variable d'environnement OPENAI_API_KEY.")
        return None
    
    # Créer un dictionnaire pour le prompt
    prompt_data = {
        "skill_name": skill_name,
        "skill_score": skill_score,
        "story": profile.get("story", ""),
        "education_level": profile.get("education_level", ""),
        "major": profile.get("major", ""),
        "job_title": profile.get("job_title", ""),
        "years_experience": profile.get("years_experience", 0),
        "career_goals": profile.get("career_goals", "")
    }
    
    try:
        # Initialiser le modèle LLM
        llm = ChatOpenAI(
            model_name="gpt-4o",
            temperature=0.2,
            api_key=OPENAI_API_KEY
        )
        
        # Créer le template de prompt
        prompt = PromptTemplate(
            input_variables=list(prompt_data.keys()),
            template=ESCO_SKILL_TEMPLATE
        )
        
        # Créer la séquence exécutable (nouvelle API recommandée)
        chain = prompt | llm
        
        # Exécuter la chaîne pour obtenir la compétence formatée
        response = chain.invoke(prompt_data)
        formatted_skill = response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        print(f"Erreur lors du formatage de la compétence ESCO: {str(e)}")
        return None
    
    # Nettoyer le résultat
    formatted_skill = formatted_skill.strip()
    
    return formatted_skill

def format_esco_skillgroup(group_label: str, skill_names: List[str], profile: Dict[str, Any], riasec: Dict[str, str]) -> Optional[str]:
    """
    Formate un groupe de compétences selon le style ESCO.
    
    Args:
        group_label: Étiquette du groupe de compétences
        skill_names: Liste des noms de compétences dans ce groupe
        profile: Dictionnaire contenant les informations de base du profil utilisateur
        riasec: Dictionnaire contenant les résultats du test RIASEC
        
    Returns:
        Une chaîne formatée selon le style de groupe de compétences ESCO
    """
    # Vérifier que toutes les dépendances sont installées
    if not check_dependencies():
        print("Impossible de formater le groupe de compétences: dépendances manquantes.")
        return None
        
    # Vérifier que la clé API OpenAI est disponible
    if not OPENAI_API_KEY:
        print("Erreur: La clé API OpenAI n'est pas définie dans les variables d'environnement.")
        print("Veuillez définir la variable d'environnement OPENAI_API_KEY.")
        return None
    
    # Extraire le code RIASEC
    top_riasec = riasec.get("top_3_code", "RCI")  # Valeur par défaut si manquante
    
    # Créer un dictionnaire pour le prompt
    prompt_data = {
        "group_label": group_label,
        "skill_names": ", ".join(skill_names),
        "education_level": profile.get("education_level", ""),
        "major": profile.get("major", ""),
        "story": profile.get("story", ""),
        "top_riasec": top_riasec
    }
    
    try:
        # Initialiser le modèle LLM
        llm = ChatOpenAI(
            model_name="gpt-4o",
            temperature=0.2,
            api_key=OPENAI_API_KEY
        )
        
        # Créer le template de prompt
        prompt = PromptTemplate(
            input_variables=list(prompt_data.keys()),
            template=ESCO_SKILLGROUP_TEMPLATE
        )
        
        # Créer la séquence exécutable (nouvelle API recommandée)
        chain = prompt | llm
        
        # Exécuter la chaîne pour obtenir le groupe de compétences formaté
        response = chain.invoke(prompt_data)
        formatted_skillgroup = response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        print(f"Erreur lors du formatage du groupe de compétences ESCO: {str(e)}")
        return None
    
    # Nettoyer le résultat
    formatted_skillgroup = formatted_skillgroup.strip()
    
    return formatted_skillgroup

def format_esco_full_profile(occupation_profile: str, skillgroup_profile: str, skill_profiles: List[str], profile: Dict[str, Any], riasec: Dict[str, str]) -> Optional[str]:
    """
    Formate un profil complet selon le style ESCO en combinant les différents éléments.
    
    Args:
        occupation_profile: Profil d'occupation formaté selon ESCO
        skillgroup_profile: Groupe de compétences formaté selon ESCO
        skill_profiles: Liste des compétences individuelles formatées selon ESCO
        profile: Dictionnaire contenant les informations de base du profil utilisateur
        riasec: Dictionnaire contenant les résultats du test RIASEC
        
    Returns:
        Une chaîne formatée selon le style de profil complet ESCO
    """
    # Vérifier que toutes les dépendances sont installées
    if not check_dependencies():
        print("Impossible de formater le profil complet: dépendances manquantes.")
        return None
        
    # Vérifier que la clé API OpenAI est disponible
    if not OPENAI_API_KEY:
        print("Erreur: La clé API OpenAI n'est pas définie dans les variables d'environnement.")
        print("Veuillez définir la variable d'environnement OPENAI_API_KEY.")
        return None
    
    # Extraire les informations du profil d'occupation
    occupation_lines = occupation_profile.strip().split('\n')
    preferred_label = ""
    altlabels = ""
    occupation_description = ""
    
    for line in occupation_lines:
        if line.startswith("PREFERREDLABEL:"):
            preferred_label = line.replace("PREFERREDLABEL:", "").strip()
        elif line.startswith("ALTLABELS:"):
            altlabels = line.replace("ALTLABELS:", "").strip()
        elif line.startswith("DESCRIPTION:"):
            occupation_description = line.replace("DESCRIPTION:", "").strip()
    
    # Extraire les informations du groupe de compétences
    if skillgroup_profile:
        skillgroup_parts = skillgroup_profile.strip().split(':', 1)
        skill_group_label = skillgroup_parts[0].strip() if len(skillgroup_parts) > 0 else ""
        skill_group_description = skillgroup_parts[1].strip() if len(skillgroup_parts) > 1 else ""
    else:
        skill_group_label = ""
        skill_group_description = ""
    
    # Extraire les compétences individuelles (jusqu'à 5)
    skills = [s for s in skill_profiles if s is not None][:5] if skill_profiles else []
    # Ajouter des placeholders pour les compétences manquantes
    while len(skills) < 3:
        skills.append("Non spécifié")
    while len(skills) < 5:
        skills.append("Non spécifié (si disponible)")
    
    # Extraire le code RIASEC
    top_riasec = riasec.get("top_3_code", "RCI")  # Valeur par défaut si manquante
    
    # Créer un dictionnaire pour le prompt
    prompt_data = {
        "preferred_label": preferred_label,
        "altlabels": altlabels,
        "occupation_description": occupation_description,
        "skill_group_label": skill_group_label,
        "skill_group_description": skill_group_description,
        "skill_1": skills[0] if len(skills) > 0 else "",
        "skill_2": skills[1] if len(skills) > 1 else "",
        "skill_3": skills[2] if len(skills) > 2 else "",
        "skill_4": skills[3] if len(skills) > 3 else "",
        "skill_5": skills[4] if len(skills) > 4 else "",
        "name": profile.get("name", ""),
        "age": profile.get("age", ""),
        "sex": profile.get("sex", ""),
        "education_level": profile.get("education_level", ""),
        "major": profile.get("major", ""),
        "years_experience": profile.get("years_experience", 0),
        "job_title": profile.get("job_title", ""),
        "story": profile.get("story", ""),
        "career_goals": profile.get("career_goals", ""),
        "top_riasec": top_riasec,
        "interests": profile.get("interests", "")
    }
    
    try:
        # Initialiser le modèle LLM
        llm = ChatOpenAI(
            model_name="gpt-4o",
            temperature=0.2,
            api_key=OPENAI_API_KEY
        )
        
        # Créer le template de prompt
        prompt = PromptTemplate(
            input_variables=list(prompt_data.keys()),
            template=ESCO_FULL_PROFILE_TEMPLATE
        )
        
        # Créer la séquence exécutable (nouvelle API recommandée)
        chain = prompt | llm
        
        # Exécuter la chaîne pour obtenir le profil complet formaté
        response = chain.invoke(prompt_data)
        formatted_full_profile = response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        print(f"Erreur lors du formatage du profil complet ESCO: {str(e)}")
        return None
    
    # Nettoyer le résultat
    formatted_full_profile = formatted_full_profile.strip()
    
    return formatted_full_profile

def save_esco_profiles(
    user_id: int,
    occupation_profile: Optional[str] = None,
    skill_profile: Optional[str] = None,
    skillsgroup_profile: Optional[str] = None,
    full_profile: Optional[str] = None
) -> bool:
    """
    Sauvegarde les profils ESCO formatés dans la base de données.
    
    Args:
        user_id: ID de l'utilisateur
        occupation_profile: Profil d'occupation ESCO formaté
        skill_profile: Profil de compétence ESCO formaté
        skillsgroup_profile: Profil de groupe de compétences ESCO formaté
        full_profile: Profil complet ESCO formaté
        
    Returns:
        True si la sauvegarde a réussi, False sinon
    """
    # Vérifier que la variable d'environnement DATABASE_URL est définie
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Erreur: La variable d'environnement DATABASE_URL n'est pas définie.")
        return False
    
    try:
        # Créer le moteur de base de données
        engine = create_engine(database_url)
        
        # Créer une session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Vérifier si l'utilisateur existe déjà dans la table user_profiles
        check_query = text("SELECT 1 FROM user_profiles WHERE user_id = :user_id")
        result = db.execute(check_query, {"user_id": user_id}).fetchone()
        
        if result:
            # L'utilisateur existe, mettre à jour son profil
            update_parts = []
            params = {"user_id": user_id}
            
            if occupation_profile:
                update_parts.append("esco_occupation_profile = :occupation_profile")
                params["occupation_profile"] = occupation_profile
                
            if skill_profile:
                update_parts.append("esco_skill_profile = :skill_profile")
                params["skill_profile"] = skill_profile
                
            if skillsgroup_profile:
                update_parts.append("esco_skillsgroup_profile = :skillsgroup_profile")
                params["skillsgroup_profile"] = skillsgroup_profile
                
            if full_profile:
                update_parts.append("esco_full_profile = :full_profile")
                params["full_profile"] = full_profile
            
            if update_parts:
                update_query = text(f"""
                    UPDATE user_profiles
                    SET {', '.join(update_parts)}
                    WHERE user_id = :user_id
                """)
                db.execute(update_query, params)
                db.commit()
                print(f"Profils ESCO mis à jour pour l'utilisateur {user_id}")
        else:
            # L'utilisateur n'existe pas, créer un nouveau profil
            columns = ["user_id"]
            values = [":user_id"]
            params = {"user_id": user_id}
            
            if occupation_profile:
                columns.append("esco_occupation_profile")
                values.append(":occupation_profile")
                params["occupation_profile"] = occupation_profile
                
            if skill_profile:
                columns.append("esco_skill_profile")
                values.append(":skill_profile")
                params["skill_profile"] = skill_profile
                
            if skillsgroup_profile:
                columns.append("esco_skillsgroup_profile")
                values.append(":skillsgroup_profile")
                params["skillsgroup_profile"] = skillsgroup_profile
                
            if full_profile:
                columns.append("esco_full_profile")
                values.append(":full_profile")
                params["full_profile"] = full_profile
            
            insert_query = text(f"""
                INSERT INTO user_profiles ({', '.join(columns)})
                VALUES ({', '.join(values)})
            """)
            db.execute(insert_query, params)
            db.commit()
            print(f"Nouveau profil ESCO créé pour l'utilisateur {user_id}")
        
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des profils ESCO: {str(e)}")
        return False

def example_usage():
    """Exemple d'utilisation des formateurs ESCO"""
    # # Exemple de profil utilisateur
    # profile = {
    #     "user_id": "user123",
    #     "name": "Marie Dupont",
    #     "age": 28,
    #     "sex": "F",
    #     "education_level": "Master",
    #     "major": "Informatique",
    #     "career_goals": "Devenir développeuse full-stack senior et diriger une équipe de développement",
    #     "story": "J'ai commencé à coder à l'âge de 15 ans. Après mes études en informatique, j'ai travaillé pendant 3 ans dans une startup où j'ai développé des applications web.",
    #     "skills": "JavaScript, Python, React, Node.js, SQL, Git",
    #     "job_title": "Développeuse web",
    #     "years_experience": 3,
    #     "interests": "Développement web, intelligence artificielle, UX/UI design"
    # }
    
    # # Exemple de scores de compétences
    # skills = {
    #     "creativity": 3.5,
    #     "leadership": 2.8,
    #     "critical_thinking": 4.2,
    #     "problem_solving": 4.5,
    #     "analytical_thinking": 4.0,
    #     "attention_to_detail": 3.8,
    #     "collaboration": 3.5,
    #     "evaluation": 3.2,
    #     "decision_making": 3.0,
    #     "stress_tolerance": 3.5
    # }
    
    # # Exemple de résultats RIASEC
    # riasec = {
    #     "top_3_code": "RIC"
    # }

        # Exemple de profil utilisateur
    profile = {
        "user_id": "user001",
        "name": "Lucas Martin",
        "age": 17,
        "sex": "M",
        "education_level": "High School",
        "major": "N/A",
        "career_goals": "Je ne sais pas encore exactement, mais j’aimerais peut-être travailler avec des technologies ou créer des choses utiles.",
        "story": "Je suis curieux de nature. J’ai aimé réparer des objets électroniques à la maison, mais j’aime aussi écrire et comprendre comment les choses fonctionnent. Je n’ai pas encore décidé ce que je veux faire, mais je veux explorer mes options.",
        "skills": "Bricolage, écriture, résolution de problèmes, pensée logique",
        "job_title": "Étudiant",
        "years_experience": 0,
        "interests": "Technologie, jeux vidéo, psychologie, environnement"
    }

    # Exemple de scores de compétences
    skills = {
        "creativity": 4.2,
        "leadership": 2.5,
        "critical_thinking": 3.8,
        "problem_solving": 4.5,
        "analytical_thinking": 4.0,
        "attention_to_detail": 3.0,
        "collaboration": 3.2,
        "evaluation": 2.8,
        "decision_making": 2.7,
        "stress_tolerance": 3.0
    }

    # Exemple de résultats RIASEC
    riasec = {
        "top_3_code": "IRC"  # Investigative, Realistic, Conventional
    }
    
    print("\n1. Formatage du profil d'occupation ESCO:")
    print("-" * 50)
    occupation_profile = format_esco_occupation(profile, skills, riasec)
    print(occupation_profile)
    print("-" * 50)
    
    print("\n2. Formatage des compétences individuelles ESCO:")
    print("-" * 50)
    skill_profiles = []
    for skill_name, skill_score in list(skills.items())[:3]:  # Limiter à 3 compétences pour l'exemple
        formatted_skill = format_esco_skill(skill_name, skill_score, profile)
        if formatted_skill:
            skill_profiles.append(formatted_skill)
            print(formatted_skill)
        else:
            print(f"Échec du formatage pour la compétence: {skill_name}")
    print("-" * 50)
    
    print("\n3. Formatage du groupe de compétences ESCO:")
    print("-" * 50)
    group_label = "Compétences techniques"
    skill_names = ["problem_solving", "analytical_thinking", "critical_thinking"]
    skillgroup_profile = format_esco_skillgroup(group_label, skill_names, profile, riasec)
    print(skillgroup_profile)
    print("-" * 50)
    
    print("\n4. Formatage du profil complet ESCO:")
    print("-" * 50)
    if occupation_profile and len(skill_profiles) > 0:
        full_profile = format_esco_full_profile(occupation_profile, skillgroup_profile, skill_profiles, profile, riasec)
        print(full_profile if full_profile else "Échec du formatage du profil complet")
    else:
        print("Impossible de formater le profil complet: données d'entrée insuffisantes")
    print("-" * 50)

if __name__ == "__main__":
    if check_dependencies():
        example_usage()
        
        print("\n5. Exemple de sauvegarde des profils ESCO dans la base de données:")
        print("-" * 50)
        print("# Pour sauvegarder les profils ESCO générés ci-dessus dans la base de données:")
        print("""
        # Convertir la liste de compétences en une chaîne de caractères
        skill_profile = "\\n".join(skill_profiles)
        
        # Sauvegarder les profils ESCO dans la base de données
        # Remplacez 123 par l'ID réel de l'utilisateur
        save_esco_profiles(
            user_id=123,
            occupation_profile=occupation_profile,
            skill_profile=skill_profile,
            skillsgroup_profile=skillgroup_profile,
            full_profile=full_profile
        )
        """)
        print("-" * 50)
        
        # Exemple complet avec un utilisateur réel
        print("\n6. Exemple complet avec un utilisateur réel:")
        print("-" * 50)
        print("""
        # 1. Récupérer les données de l'utilisateur depuis la base de données
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker
        
        # Configurer la connexion à la base de données
        DATABASE_URL = os.getenv("DATABASE_URL")
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Récupérer l'utilisateur par son ID
        user_id = 123  # Remplacez par l'ID réel de l'utilisateur
        
        # Récupérer le profil utilisateur
        query = text('''
            SELECT * FROM user_profiles WHERE user_id = :user_id
        ''')
        user_profile_result = db.execute(query, {"user_id": user_id}).fetchone()
        
        # Récupérer les compétences de l'utilisateur
        skills_query = text('''
            SELECT skill_name, score FROM user_skills WHERE user_id = :user_id
        ''')
        skills_result = db.execute(skills_query, {"user_id": user_id}).fetchall()
        
        # Récupérer les résultats RIASEC
        riasec_query = text('''
            SELECT top_3_code FROM gca_results WHERE user_id = :user_id
        ''')
        riasec_result = db.execute(riasec_query, {"user_id": user_id}).fetchone()
        
        # 2. Convertir les données en format attendu par les formateurs ESCO
        profile = {
            "user_id": user_id,
            "name": user_profile_result.name,
            "age": user_profile_result.age,
            "sex": user_profile_result.sex,
            "education_level": user_profile_result.education_level,
            "major": user_profile_result.major,
            "career_goals": user_profile_result.career_goals,
            "story": user_profile_result.story,
            "job_title": user_profile_result.job_title,
            "years_experience": user_profile_result.years_experience,
            "interests": user_profile_result.interests
        }
        
        skills = {skill.skill_name: skill.score for skill in skills_result}
        riasec = {"top_3_code": riasec_result.top_3_code if riasec_result else "RIC"}
        
        # 3. Générer et sauvegarder les profils ESCO
        # [Utiliser le même code que dans l'exemple précédent]
        """)
        print("-" * 50)
    else:
        sys.exit(1)