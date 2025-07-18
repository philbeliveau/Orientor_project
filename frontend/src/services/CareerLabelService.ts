import careerLabels from '../config/careerLabels.json';

/**
 * Type pour les IDs de carrière supportés
 */
export type CareerLabelId = keyof typeof careerLabels;

/**
 * Interface pour le service de mapping des carrières
 */
export interface CareerLabelMapping {
  [key: string]: string;
}

/**
 * Service pour gérer la conversion des IDs de carrière en libellés lisibles
 */
export class CareerLabelService {
  private static labelMap: CareerLabelMapping = careerLabels;

  /**
   * Convertit un ID de carrière en libellé lisible
   * @param careerId - L'ID technique de la carrière
   * @returns Le libellé lisible ou un fallback sécurisé
   */
  public static getCareerLabel(careerId: string | number): string {
    // Validation d'entrée
    if (!careerId && careerId !== 0) {
      return 'Carrière non spécifiée';
    }

    // Conversion en string pour la recherche
    const normalizedId = String(careerId).trim();
    
    // Recherche dans le mapping
    const label = this.labelMap[normalizedId];
    
    if (label) {
      return label;
    }

    // Fallback sécurisé avec nettoyage de l'ID pour affichage
    return this.createFallbackLabel(normalizedId);
  }

  /**
   * Vérifie si un ID de carrière existe dans le mapping
   * @param careerId - L'ID technique de la carrière
   * @returns true si l'ID existe dans le mapping
   */
  public static hasCareerLabel(careerId: string | number): boolean {
    if (!careerId && careerId !== 0) {
      return false;
    }
    
    const normalizedId = String(careerId).trim();
    return normalizedId in this.labelMap;
  }

  /**
   * Obtient tous les mappings disponibles
   * @returns L'objet complet des mappings
   */
  public static getAllMappings(): CareerLabelMapping {
    return { ...this.labelMap };
  }

  /**
   * Ajoute un nouveau mapping (pour usage dynamique)
   * @param careerId - L'ID de la carrière
   * @param label - Le libellé associé
   */
  public static addMapping(careerId: string, label: string): void {
    if (!careerId?.trim() || !label?.trim()) {
      throw new Error('L\'ID et le libellé de carrière ne peuvent pas être vides');
    }
    
    this.labelMap[careerId.trim()] = label.trim();
  }

  /**
   * Crée un libellé de fallback lisible à partir d'un ID technique
   * @param careerId - L'ID technique brut
   * @returns Un libellé fallback plus lisible
   */
  private static createFallbackLabel(careerId: string): string {
    // Nettoyage basique des IDs techniques pour les rendre plus lisibles
    let cleanId = careerId;
    
    // Supprime les préfixes communs
    cleanId = cleanId.replace(/^career_/, '');
    
    // Remplace les underscores par des espaces
    cleanId = cleanId.replace(/_/g, ' ');
    
    // Capitalize la première lettre de chaque mot
    cleanId = cleanId.replace(/\b\w/g, (char) => char.toUpperCase());
    
    // Si c'est juste un nombre, on retourne un format plus descriptif
    if (/^\d+$/.test(cleanId)) {
      return `Carrière ${cleanId}`;
    }
    
    return cleanId || 'Carrière inconnue';
  }

  /**
   * Traite un tableau d'IDs de carrière en une seule opération
   * @param careerIds - Tableau d'IDs de carrière
   * @returns Tableau des libellés correspondants
   */
  public static getMultipleCareerLabels(careerIds: (string | number)[]): string[] {
    if (!Array.isArray(careerIds)) {
      return [];
    }
    
    return careerIds.map((id) => this.getCareerLabel(id));
  }

  /**
   * Recherche des carrières par texte partiel dans les libellés
   * @param searchText - Texte à rechercher
   * @returns Tableau des correspondances {id, label}
   */
  public static searchCareerLabels(searchText: string): Array<{id: string, label: string}> {
    if (!searchText?.trim()) {
      return [];
    }
    
    const searchTerm = searchText.toLowerCase().trim();
    const results: Array<{id: string, label: string}> = [];
    
    for (const [id, label] of Object.entries(this.labelMap)) {
      if (label.toLowerCase().includes(searchTerm)) {
        results.push({ id, label });
      }
    }
    
    return results;
  }
}

/**
 * Fonction utilitaire pour un accès rapide au mapping principal
 * @param careerId - L'ID de la carrière
 * @returns Le libellé lisible
 */
export const getCareerLabel = (careerId: string | number): string => {
  return CareerLabelService.getCareerLabel(careerId);
};

/**
 * Hook-like function pour une utilisation dans les composants React
 * @param careerId - L'ID de la carrière
 * @returns Objet avec le libellé et des informations sur le mapping
 */
export const useCareerLabel = (careerId: string | number) => {
  const label = CareerLabelService.getCareerLabel(careerId);
  const isCustomLabel = !CareerLabelService.hasCareerLabel(careerId);
  
  return {
    label,
    isCustomLabel,
    originalId: careerId
  };
};

export default CareerLabelService;