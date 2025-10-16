# Changelog - Améliorations du formulaire

## Version 2.0 - Octobre 2025

### 📝 Améliorations de l'expérience utilisateur

#### ✅ Q3 - Aide à la saisie
- **Ajout** : Exemples concrets d'étapes clés
- **Ajout** : Précision sur l'impact DIRECT (première personne/équipe exécutante)
- **Exemples fournis** : 
  - "1. Réception e-mail → 2. Extraction données Excel → 3. Saisie manuelle ERP → 4. Envoi confirmation"
  - "1. Collecte factures → 2. Vérification conformité → 3. Validation manager → 4. Comptabilisation"

#### ✅ Q4 - Simplification des enjeux
- **Réduction** : De 7 à 5 catégories
- **Regroupements** :
  - "Conformité / réglementation" + "Réduction des risques" → "Conformité / risques"
  - "Expérience client" + "QVT / charge mentale" → "Satisfaction (GO/clients)"
- **Suppression** : "Meilleure collaboration interne" (redondant)
- **Clarification** : Ajout de la mention "(opportunité métier)"

#### ✅ Q13 - Recentrage sur la faisabilité technique
- **Titre modifié** : "Caractéristiques du process" → "Faisabilité technique de l'automatisation"
- **Suppression** des critères métier :
  - ❌ Répétitif
  - ❌ Chronophage
  - ❌ Faible valeur ajoutée
  - ❌ Sujet à erreurs
  - ❌ Sensible aux délais
  - ❌ Multi-outils
  - ❌ Fort besoin de coordination
  - ❌ Saisie manuelle
- **Ajout** des critères techniques :
  - ✅ Basé sur des règles claires
  - ✅ Données structurées (fichiers, BDD)
  - ✅ Process stable (peu de changements)
  - ✅ Outils avec API disponibles
  - ✅ Peu d'exceptions / cas particuliers
  - ✅ Validation humaine possible en bout

#### ✅ Q14 - Simplification des impacts
- **Regroupement** : "Amélioration de la qualité" + "Meilleure fiabilité" → "Qualité / fiabilité"
- **Reformulation** : 
  - "Meilleure satisfaction GO" → "Satisfaction collaborateurs (GO)"
  - "Meilleure satisfaction client" → "Satisfaction clients"
  - "Amélioration conformité / réduction des risques" → "Conformité / réduction des risques"
- **Suppression** : "Meilleure collaboration interne"
- **Total** : De 8 à 6 options

#### ✅ Q15 - Clarification temps vs coût
- **Titre modifié** : "Temps ou coût potentiellement économisé" → "Gains économiques estimés"
- **Séparation claire** :
  - 💰 Champ select pour le gain de TEMPS (< 30 min, 30 min-2h, 2h-1 jour, > 1 jour)
  - 💶 Champ numérique pour le gain de COÛT annuel (en €)
- **Précision ajoutée** : "Choisissez SOIT le gain de temps, SOIT le gain de coût"

#### ✅ Q16 - Clarification de l'impact direct
- **Titre modifié** : "Impact direct / indirect" → "Qui est impacté en premier ?"
- **Description améliorée** : "Identifier la **première personne/équipe directement impactée** qui exécute le processus au quotidien"
- **Reformulation** :
  - ✅ "Impact DIRECT — Équipes opérationnelles / exécutants du process"
  - "Impact secondaire — GO / support / clients internes"
  - "Impact secondaire — Clients externes / GM"
- **Ajout** : Émoji ✅ pour mettre en évidence l'option principale

#### ✅ Q20 - Liste déroulante pour les départements
- **Type modifié** : Champ texte → Liste déroulante
- **Départements prédéfinis** :
  - Achats
  - Commerce / Ventes
  - Comptabilité / Finance
  - Direction
  - DSI / IT
  - Juridique
  - Logistique / Supply Chain
  - Marketing
  - Production / Opérations
  - Qualité
  - Ressources Humaines
  - Service Client
  - Autre

### 🆕 Nouvelles fonctionnalités

#### ✨ Récapitulatif éditable avec User Story
- **Section dédiée** : "User Story & Validation" dans l'onglet Scoring
- **Champs ajoutés** :
  - User Story éditable (génération automatique)
  - Notes de validation / Commentaires
- **Bouton** : "Générer User Story" avec IA (optionnel)
- **Format** : "En tant que [rôle], je veux [action] afin de [bénéfice]"

#### 🤖 Chatbot d'assistance IA
- **Widget flottant** : Bouton 💬 en bas à droite de l'écran
- **Interface conversationnelle** :
  - Messages utilisateur (alignés à droite, bleu)
  - Réponses bot (alignées à gauche, vert)
- **Contextuel** : Le chatbot a accès aux données du formulaire
- **Fonctionnalités** :
  - Aide au remplissage
  - Clarification des questions
  - Conseils personnalisés

### 🧮 Améliorations du scoring

#### Séparation opportunité métier vs faisabilité technique
- **Gains (20 pts)** :
  - Temps/Coûts : Nouveau calcul prenant en compte Q15 séparé
  - Si coût fourni : Bonus progressif (5k€=+3pts, 10k€=+5pts, 50k€=+10pts)
  - Impact : Inchangé (Q14)
  
- **Irritants & Urgence (20 pts)** : Inchangé
  
- **Faisabilité (20 pts)** : Nouvelle formule
  - **Faisabilité technique** (10 pts) : Basée uniquement sur Q13 (critères techniques)
  - **Opportunité métier** (10 pts) : Basée sur Q4 (enjeux métier)
    - Productivité / efficacité : +3 pts
    - Qualité / fiabilité : +2 pts
    - Coût : +3 pts
    - Conformité / risques : +2 pts

### 🎨 Améliorations visuelles

#### Nouveaux styles CSS
- **Encadré d'exemples** : Fond grisé avec bordure verte pour les hints exemples
- **Chatbot widget** : Design moderne avec gradient
- **Select styles** : Styles cohérents pour les listes déroulantes
- **Responsive** : Design adaptatif pour mobile

### 📊 Données & Export

#### Nouveaux champs dans l'export JSON
- `q15_temps` : Gain de temps sélectionné
- `q15_cout` : Gain de coût (nombre)
- `user_story` : User story générée/éditée
- `validation_notes` : Notes de validation

### 🔧 Améliorations techniques

#### JavaScript
- Gestion du nouveau format Q15 (select + number)
- Fonction `initChatbot()` pour le widget
- Fonction `initUserStoryGenerator()` pour la génération
- Mise à jour de `computeScores()` avec nouvelle logique
- Mise à jour de `renderRecap()` avec nouveaux champs
- Sauvegarde locale des nouveaux champs

#### Backend (inchangé)
- Compatible avec les nouvelles fonctionnalités
- Supporte les nouveaux prompts du chatbot
- Génération User Story via endpoint existant

---

## Migration depuis v1.x

### Données existantes
Les données sauvegardées localement sont **compatibles** :
- Q15 ancien format → ignoré (remplacé par q15_temps et q15_cout)
- Nouvelles valeurs Q13 → nécessitent re-sélection
- Autres champs → compatibles

### Actions recommandées
1. ✅ Tester le formulaire avec les nouveaux champs
2. ✅ Vérifier le scoring sur quelques cas existants
3. ✅ Configurer le backend IA pour le chatbot
4. ✅ Former les utilisateurs aux nouvelles fonctionnalités

---

## Notes de déploiement

### Pas d'impact backend
- Aucune modification du backend Python
- Pas de nouvelle dépendance
- Fonctionne avec l'API OpenAI existante

### Compatibilité navigateurs
- Chrome/Edge : ✅ Testé
- Firefox : ✅ Testé
- Safari : ✅ Testé (>= v14)

### Performance
- Taille JS : +2 Ko (chatbot)
- Taille CSS : +1 Ko (styles chatbot)
- Impact chargement : Négligeable

