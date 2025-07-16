// OpenNote-inspired Landing Page for Navigo
// Transformed to focus on educational note-taking and learning tools
// Maintains Navigo branding while adopting OpenNote's clean educational aesthetic

import Link from 'next/link';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-white relative overflow-hidden">
      
      {/* Floating notebook elements */}
      <div className="writing-elements">
        <div className="pencil"></div>
        <div className="eraser"></div>
        <div className="pen"></div>
      </div>
      
      {/* Floating background pattern */}
      <div className="floating-dots"></div>

      {/* Header */}
      <header className="relative z-20 px-6 lg:px-12 py-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-indigo-500 to-sky-400 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">N</span>
            </div>
            <div>
              <div className="font-bold text-xl text-gray-900">Navigo</div>
              <div className="text-xs text-gray-500">Orientation & Carrières</div>
            </div>
          </div>
          <nav className="hidden md:flex items-center space-x-8">
            <Link href="/onboarding" className="text-gray-600 hover:text-gray-900 transition-colors">Tests</Link>
            <Link href="/career" className="text-gray-600 hover:text-gray-900 transition-colors">Carrières</Link>
            <Link href="/chat" className="text-gray-600 hover:text-gray-900 transition-colors">Chat IA</Link>
            <Link href="/login" className="bg-gradient-to-r from-indigo-500 to-sky-400 text-white px-4 py-2 rounded-lg hover:from-indigo-600 hover:to-sky-500 transition-all ink-button">
              Commencer
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center px-6 lg:px-12 py-20">
        <div className="paper-container">
          <div className="paper-sheet">
            <div className="paper-lines"></div>
            <div className="paper-content">
              
              
              <div className="text-center space-y-8">
                <h1 className="handwritten-title text-5xl lg:text-7xl text-gray-800 mb-6">
                  Découvre ton chemin professionnel
                </h1>
                
                <div className="ink-pen-line"></div>
                
                <p className="handwritten-text text-gray-600 max-w-2xl mx-auto leading-relaxed">
                  Ton style d'apprentissage est unique—tes outils d'exploration professionnelle aussi. Crée ton environnement parfait avec les outils interactifs de Navigo pour découvrir tes possibilités de carrière.
                </p>
                
                {/* Empty notebook illustration */}
                <div className="my-12 text-center">
                  <div className="inline-block bg-white p-8 rounded-lg shadow-lg border-2 border-dashed border-gray-300 max-w-md">
                    <div className="text-6xl text-gray-300 mb-4">🗺️</div>
                    <p className="text-gray-400 italic">Ton histoire est encore à écrire...</p>
                    <p className="text-sm text-gray-500 mt-2">Ton parcours professionnel commence par une page blanche</p>
                  </div>
                </div>
                
                <div className="flex flex-col sm:flex-row gap-4 justify-center mt-12">
                  <Link href="/register" className="cta-primary bg-gradient-to-r from-indigo-500 to-sky-400 text-white px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-300 hover:from-indigo-600 hover:to-sky-500 hover:scale-105 hover:shadow-lg ink-button">
                    Commencer mon exploration
                  </Link>
                  <Link href="/onboarding" className="cta-secondary text-gray-600 hover:text-gray-900 transition-colors px-8 py-4 font-medium text-lg border-2 border-gray-300 rounded-lg hover:border-gray-400 hover:shadow-md ink-button">
                    Voir comment ça marche
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
      {/* Toolkit Section */}
      <section className="px-6 lg:px-12 py-20 bg-gradient-to-b from-white to-gray-50 animate-on-scroll">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="handwritten-title text-4xl lg:text-5xl text-gray-900 mb-4">
              Des outils qui s'adaptent à toi
            </h2>
            <div className="ink-pen-line"></div>
            <p className="handwritten-text text-gray-600 max-w-3xl mx-auto mt-6">
              Combine tests de personnalité, exploration de carrières, chat IA et analyses personnalisées. Chaque outil conçu pour t'aider à découvrir tes possibilités professionnelles.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Digital Notes */}
            <div className="feature-card-enhanced">
              <div className="go-corner">
                <div className="go-arrow">→</div>
              </div>
              <div className="feature-icon text-4xl mb-4">📱</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">SwipeMyWay</h3>
              <p className="text-gray-600 text-sm">
                Découvre tes préférences en glissant sur des rôles. Interface intuitive qui apprend de tes choix instantanément.
              </p>
              <div className="mt-4 text-xs text-indigo-500 font-semibold">EXPLORATION RAPIDE</div>
            </div>
            
            {/* Learning Whiteboards */}
            <div className="feature-card-enhanced">
              <div className="go-corner">
                <div className="go-arrow">→</div>
              </div>
              <div className="feature-icon text-4xl mb-4">🌳</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Arbre des Carrières</h3>
              <p className="text-gray-600 text-sm">
                Navigation émotionnelle: Bâtisseur, Communicateur, Explorateur. Chaque branche mène vers des rôles réels.
              </p>
              <div className="mt-4 text-xs text-sky-400 font-semibold">NAVIGATION INTUITIVE</div>
            </div>
            
            {/* Learning Paths */}
            <div className="feature-card-enhanced">
              <div className="go-corner">
                <div className="go-arrow">→</div>
              </div>
              <div className="feature-icon text-4xl mb-4">🕰️</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Tests HEXACO</h3>
              <p className="text-gray-600 text-sm">
                Analyse approfondie de ta personnalité avec 6 dimensions clés pour mieux te connaître professionnellement.
              </p>
              <div className="mt-4 text-xs text-indigo-500 font-semibold">CONNAISSANCE DE SOI</div>
            </div>
            
            {/* Practice Problems */}
            <div className="feature-card-enhanced">
              <div className="go-corner">
                <div className="go-arrow">→</div>
              </div>
              <div className="feature-icon text-4xl mb-4">🤖</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Chat IA Navigo</h3>
              <p className="text-gray-600 text-sm">
                Conversations guidées avec notre IA pour explorer tes motivations et clarifier tes objectifs de carrière.
              </p>
              <div className="mt-4 text-xs text-sky-400 font-semibold">GUIDANCE PERSONNALISÉE</div>
            </div>
          </div>
        </div>
      </section>
      {/* Note-Taking Section */}
      <section className="px-6 lg:px-12 py-20 animate-on-scroll">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Paper sheet mockup */}
            <div className="paper-container">
              <div className="paper-sheet bg-white min-h-96">
                <div className="paper-lines"></div>
                <div className="paper-content">
                  <h3 className="handwritten-title text-3xl text-gray-800 mb-6">Découvre tes passions avec notre système d'exploration</h3>
                  <div className="space-y-4 handwritten-text text-gray-600">
                    <p>🎯 Identifie tes valeurs et motivations</p>
                    <p>🔍 Explore des carrières alignées avec ta personnalité</p>
                    <p>📊 Visualise tes compétences et ton potentiel</p>
                    <p>🗺️ Planifie ton parcours professionnel</p>
                    <p className="text-gray-400 italic text-sm mt-8">Ton avenir professionnel, révélé avec clarté...</p>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Description */}
            <div className="space-y-6">
              <h2 className="handwritten-title text-4xl text-gray-900">
                Une approche interactive pour découvrir ta voie
              </h2>
              <div className="ink-pen-line"></div>
              <p className="handwritten-text text-gray-600 leading-relaxed">
                Transforme ta manière d'explorer les carrières. Notre système comprend tes préférences, suggère des connexions, et t'aide à construire ta carte personnelle des possibilités.
              </p>
              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <div className="text-green-500 mt-1">✓</div>
                  <span className="text-gray-700">Tests de personnalité scientifiquement validés</span>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="text-green-500 mt-1">✓</div>
                  <span className="text-gray-700">Recommandations basées sur tes résultats</span>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="text-green-500 mt-1">✓</div>
                  <span className="text-gray-700">Exploration interactive des métiers</span>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="text-green-500 mt-1">✓</div>
                  <span className="text-gray-700">Suivi de progression personnalisé</span>
                </div>
              </div>
              <Link href="/onboarding" className="inline-block cta-primary bg-gradient-to-r from-indigo-500 to-sky-400 text-white px-8 py-4 rounded-lg hover:from-indigo-600 hover:to-sky-500 transition-all duration-300 font-semibold hover:scale-105 hover:shadow-lg ink-button">
                Commencer l'exploration
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Learning Features Section */}
      <section className="px-6 lg:px-12 py-20 bg-gradient-to-b from-gray-50 to-white animate-on-scroll">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="handwritten-title text-4xl lg:text-5xl text-gray-900 mb-4">
              Vois tes possibilités prendre vie
            </h2>
            <div className="ink-pen-line"></div>
            <p className="handwritten-text text-gray-600 max-w-3xl mx-auto mt-6">
              Transforme tes réflexions en découvertes concrètes. Notre système "Synthèse" convertit tes réponses en recommandations personnalisées et connections visuelles.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {/* Visual Learning */}
            <div className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-all duration-300 hover:transform hover:scale-105 assessment-card">
              <div className="assessment-icon text-5xl mb-6 text-center">🗺️</div>
              <h3 className="handwritten-title text-2xl text-gray-900 mb-4 text-center">Cartographie Professionnelle</h3>
              <p className="handwritten-text text-gray-600 text-center mb-6">
                Transforme tes intérêts en cartes visuelles, graphiques interactifs et diagrammes qui révèlent des connexions cachées entre métiers.
              </p>
              <div className="assessment-btn w-full bg-indigo-100 text-indigo-700 py-3 px-6 rounded-lg hover:bg-indigo-200 transition-all text-center font-semibold">
                Explorer les Visualisations
              </div>
            </div>
            
            {/* Interactive Lessons */}
            <div className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-all duration-300 hover:transform hover:scale-105 assessment-card">
              <div className="assessment-icon text-5xl mb-6 text-center">📈</div>
              <h3 className="handwritten-title text-2xl text-gray-900 mb-4 text-center">Progression Guidée</h3>
              <p className="handwritten-text text-gray-600 text-center mb-6">
                Transforme tes découvertes en parcours guidés avec étapes, défis et révélations progressives de tes talents.
              </p>
              <div className="assessment-btn w-full bg-sky-100 text-sky-700 py-3 px-6 rounded-lg hover:bg-sky-200 transition-all text-center font-semibold">
                Essayer le Mode Guidé
              </div>
            </div>
            
            {/* Knowledge Connections */}
            <div className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-all duration-300 hover:transform hover:scale-105 assessment-card">
              <div className="assessment-icon text-5xl mb-6 text-center">🤖</div>
              <h3 className="handwritten-title text-2xl text-gray-900 mb-4 text-center">IA Personnalisée</h3>
              <p className="handwritten-text text-gray-600 text-center mb-6">
                Découvre comment tes intérêts se connectent entre domaines grâce à notre cartographie relationnelle alimentée par l'IA.
              </p>
              <div className="assessment-btn w-full bg-purple-100 text-purple-700 py-3 px-6 rounded-lg hover:bg-purple-200 transition-all text-center font-semibold">
                Voir les Connexions
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="px-6 lg:px-12 py-20 animate-on-scroll">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="handwritten-title text-4xl lg:text-5xl text-gray-900 mb-4">
              Découvre Plus, Dépense Moins
            </h2>
            <div className="ink-pen-line"></div>
            <p className="handwritten-text text-gray-600 max-w-2xl mx-auto mt-6">
              Choisis l'environnement d'exploration parfait pour tes besoins. Commence gratuitement et évolue avec des fonctionnalités avancées.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {/* Free Tier */}
            <div className="paper-container">
              <div className="paper-sheet bg-white min-h-96 text-center">
                <div className="paper-lines"></div>
                <div className="paper-content">
                  <h3 className="handwritten-title text-2xl text-gray-900 mb-4">Gratuit</h3>
                  <p className="text-gray-600 mb-6">Parfait pour découvrir Navigo</p>
                  <div className="handwritten-text text-3xl text-gray-900 mb-6">0$</div>
                  <ul className="handwritten-text text-gray-600 space-y-2 mb-8">
                    <li>• Tests de base</li>
                    <li>• Exploration limitée</li>
                    <li>• Application mobile</li>
                    <li>• Support communautaire</li>
                  </ul>
                  <button className="cta-secondary w-full border-2 border-gray-300 text-gray-700 py-3 px-6 rounded-lg hover:border-gray-400 hover:shadow-md transition-all font-semibold ink-button">
                    Commencer Gratuitement
                  </button>
                </div>
              </div>
            </div>
            
            {/* Premium Tier */}
            <div className="paper-container">
              <div className="paper-sheet bg-gradient-to-br from-indigo-50 to-sky-50 min-h-96 text-center border-2 border-indigo-200">
                <div className="paper-content">
                  <div className="bg-indigo-500 text-white px-3 py-1 rounded-full text-sm font-semibold mb-4 inline-block">Plus Populaire</div>
                  <h3 className="handwritten-title text-2xl text-gray-900 mb-4">Premium</h3>
                  <p className="text-gray-600 mb-6">Débloque tout ton potentiel d'exploration</p>
                  <div className="handwritten-text text-3xl text-gray-900 mb-6">15$<span className="text-base">/mois</span></div>
                  <ul className="handwritten-text text-gray-600 space-y-2 mb-8">
                    <li>• Tous les tests avancés</li>
                    <li>• Analyses approfondies</li>
                    <li>• Recommandations IA</li>
                    <li>• Support prioritaire</li>
                    <li>• Outils de collaboration</li>
                  </ul>
                  <button className="cta-primary w-full bg-gradient-to-r from-indigo-500 to-sky-400 text-white py-3 px-6 rounded-lg hover:from-indigo-600 hover:to-sky-500 transition-all font-semibold hover:scale-105 hover:shadow-lg ink-button">
                    Passer à Premium
                  </button>
                </div>
              </div>
            </div>
            
            {/* Enterprise Tier */}
            <div className="paper-container">
              <div className="paper-sheet bg-white min-h-96 text-center">
                <div className="paper-lines"></div>
                <div className="paper-content">
                  <h3 className="handwritten-title text-2xl text-gray-900 mb-4">Entreprise</h3>
                  <p className="text-gray-600 mb-6">Pour écoles et institutions</p>
                  <div className="handwritten-text text-3xl text-gray-900 mb-6">Sur mesure</div>
                  <ul className="handwritten-text text-gray-600 space-y-2 mb-8">
                    <li>• Accès illimité complet</li>
                    <li>• Intégrations personnalisées</li>
                    <li>• Analyses avancées</li>
                    <li>• Support dédié</li>
                    <li>• SSO et conformité</li>
                  </ul>
                  <button className="cta-secondary w-full border-2 border-gray-300 text-gray-700 py-3 px-6 rounded-lg hover:border-gray-400 hover:shadow-md transition-all font-semibold ink-button">
                    Contacter les Ventes
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-6 lg:px-12 py-20 bg-gradient-to-br from-indigo-500 to-sky-400 relative overflow-hidden stars-container">
        {/* Stars */}
        <div className="star star-1"></div>
        <div className="star star-2"></div>
        <div className="star star-3"></div>
        <div className="star star-4"></div>
        <div className="star star-5"></div>
        
        <div className="max-w-4xl mx-auto text-center relative z-10">
          <h2 className="handwritten-title text-4xl lg:text-6xl text-white mb-6">
            Une exploration qui fonctionne vraiment pour toi
          </h2>
          <div className="w-32 h-1 bg-white/30 mx-auto rounded mb-8"></div>
          <p className="handwritten-text text-xl text-white/90 max-w-2xl mx-auto mb-12">
            Rejoins des milliers d'étudiants qui ont transformé leur approche de l'orientation avec la plateforme intelligente de Navigo.
          </p>
          
          {/* Features list */}
          <div className="grid md:grid-cols-4 gap-6 mb-12 text-white">
            <div className="space-y-2">
              <div className="text-2xl">🔍</div>
              <p className="font-semibold">Découvre tes passions cachées</p>
            </div>
            <div className="space-y-2">
              <div className="text-2xl">🎯</div>
              <p className="font-semibold">Organise tes objectifs efficacement</p>
            </div>
            <div className="space-y-2">
              <div className="text-2xl">🤝</div>
              <p className="font-semibold">Partage tes découvertes avec des pairs</p>
            </div>
            <div className="space-y-2">
              <div className="text-2xl">📈</div>
              <p className="font-semibold">Suis ta progression d'exploration</p>
            </div>
          </div>
          
          <Link href="/register" className="cta-primary inline-block bg-white text-indigo-600 px-12 py-4 rounded-lg font-bold text-xl hover:shadow-2xl transition-all duration-300 hover:scale-105 ink-button">
            Essaie Navigo aujourd'hui
          </Link>
          <p className="handwritten-text text-white/80 mt-4 text-sm">Étudiants qui créent des outils pour étudiants • Gratuit pour commencer</p>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-white py-12 px-6 lg:px-12 border-t border-gray-200">
        <div className="max-w-7xl mx-auto text-center">
          <div className="mb-8">
            <div className="flex items-center justify-center space-x-3 mb-4">
              <div className="w-8 h-8 bg-gradient-to-r from-indigo-500 to-sky-400 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold">N</span>
              </div>
              <div className="handwritten-title text-2xl text-gray-900">Navigo</div>
            </div>
            <p className="handwritten-text text-gray-600 max-w-2xl mx-auto">
              Plateforme d'exploration professionnelle conçue pour les étudiants modernes. Conçue avec passion pour l'éducation et la découverte.
            </p>
          </div>
          
          <div className="border-t border-gray-200 pt-8">
            <p className="text-sm text-gray-500">
              © 2024 Plateforme Navigo. Conçue pour les esprits curieux du monde entier.
              <br />
              <span className="italic">Où chaque découverte devient un tremplin vers ton avenir.</span>
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
