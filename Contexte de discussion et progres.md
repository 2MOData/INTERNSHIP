# Contexte de discussion et progression du projet

## 1. Objectif général du projet

Le projet vise à construire une plateforme d'agents IA spécialisés par domaine métier.

L'idée principale est de permettre à un utilisateur de créer des agents capables de répondre à partir de documents internes ou métier, avec des réponses sourcées et, à terme, des automatisations contrôlées.

Le frontend doit être majoritairement construit avec React, tandis que le backend et les fonctionnalités IA doivent être développés en Python.

## 2. Méthodologie adoptée

Nous avons choisi une méthode incrémentale et pédagogique :

1. travailler par petites étapes ;
2. créer une branche dédiée pour chaque étape ;
3. implémenter une seule capacité à la fois ;
4. tester localement ;
5. corriger les erreurs avant de continuer ;
6. commit ;
7. push ;
8. ouvrir ou merger la Pull Request ;
9. repartir de `main` pour l'étape suivante.

Cette méthode permet de comprendre ce que l'on fait, d'éviter les gros changements difficiles à déboguer et de garder un historique Git clair.

## 3. Préparation de l'environnement

Nous avons commencé par clarifier les outils nécessaires sur Windows avec WSL :

- WSL pour travailler dans un environnement Linux ;
- Git pour versionner le projet ;
- Python et un environnement virtuel `.venv` pour le backend ;
- Node.js et npm pour le frontend React ;
- Docker Desktop avec intégration WSL ;
- Docker Compose pour lancer les services locaux ;
- éventuellement `make`, même si les commandes directes restent utilisables.

Nous avons aussi clarifié que les dépendances Python ne doivent pas être réinstallées à chaque réouverture du projet si l'environnement virtuel existe encore. En revanche, il faut réactiver l'environnement avec :

```bash
source .venv/bin/activate
```

Si une commande comme `alembic` n'est pas reconnue, cela signifie généralement que l'environnement virtuel n'est pas activé ou que les dépendances n'ont pas été installées dans cet environnement.

## 4. Lecture du cahier des charges et plan MVP

La première étape a été de lire le cahier des charges PDF présent dans le dépôt.

À partir de ce document, nous avons établi un plan MVP orienté plateforme d'agents spécialisés :

- agents configurables ;
- documents sources ;
- réponses sourcées ;
- automatisations contrôlées ;
- architecture frontend React et backend Python ;
- possibilité future d'intégrer des workflows externes.


## 5. Initialisation du frontend React

Nous avons ensuite créé le frontend avec React, TypeScript et Vite.

Le but était de disposer d'une première interface visible dans le navigateur, simple mais propre, afin de valider l'environnement frontend.

Nous avons vérifié :

```bash
npm install
npm run dev
npm run lint
npm run build
```

Nous avons aussi clarifié le rôle du fichier `package.json` : c'est lui qui déclare les dépendances npm et les scripts comme `dev`, `lint` et `build`.

Une erreur de lancement des commandes npm depuis un mauvais dossier a été corrigée en rappelant qu'il faut les lancer depuis le dossier contenant le `package.json`, typiquement :

```bash
apps/web
```

## 6. Première API FastAPI

Nous avons ensuite ajouté un backend FastAPI minimal.

La première capacité était un endpoint de santé permettant de vérifier que l'API démarre correctement :

```text
GET /health
```

Cette étape avait pour objectif de valider :

- l'environnement Python ;
- l'installation des dépendances ;
- le démarrage avec Uvicorn ;
- la structure initiale du backend.

Nous avons rencontré et corrigé des erreurs Python classiques :

- indentation incorrecte ;
- import manquant de `status` depuis FastAPI ;
- environnement virtuel non activé.

## 7. Connexion frontend-backend

Après avoir validé séparément le frontend et le backend, nous avons connecté React à FastAPI.

Le frontend a été modifié pour appeler l'endpoint `/health` et afficher l'état de connexion à l'API.

Cette étape a aussi nécessité la configuration CORS côté FastAPI, afin d'autoriser le frontend Vite sur `localhost:5173` à appeler l'API.

Le résultat validé était :

```text
React -> FastAPI -> réponse santé -> affichage dans l'interface
```

## 8. Domaine initial des agents

Nous avons introduit la notion d'agent métier.

Un agent représente une configuration spécialisée avec des champs comme :

- nom ;
- description ;
- domaine ;
- cas d'usage ;
- statut.

Une première API agents a été créée avec un stockage en mémoire, pour aller vite et valider la logique avant d'ajouter PostgreSQL.

Les routes initiales concernaient notamment :

```text
GET /api/v1/agents
POST /api/v1/agents
POST /api/v1/agents/{agent_id}/publish
```

## 9. Interface de création d'agents

Nous avons ensuite ajouté une interface React permettant de créer des agents depuis le navigateur.

Des erreurs TypeScript liées aux imports de types ont été rencontrées, notamment avec `verbatimModuleSyntax`.

La solution a été d'utiliser des imports de types explicites :

```ts
import type { Agent, CreateAgentInput } from "..."
```

Cela a permis de corriger les erreurs de build et d'éviter la page blanche.

Nous avons également rencontré un problème de branche Git avec `agent-ui`, qui était en avance et en retard par rapport à `main`. Cela a conduit à nettoyer les branches et à réintégrer proprement les changements.

## 10. Tests automatisés de l'API agents

Une étape a été consacrée aux tests backend.

Nous avons ajouté des tests avec `pytest` afin de valider :

- l'endpoint de santé ;
- la création d'agents ;
- la liste des agents ;
- les erreurs attendues ;
- le comportement du domaine.

Cela a renforcé notre méthodologie : chaque fonctionnalité importante doit être accompagnée de tests automatisés.

## 11. Infrastructure PostgreSQL et pgvector

Nous avons ensuite ajouté PostgreSQL avec l'extension pgvector dans l'environnement local.

Le but était de préparer la persistance réelle des données et la future recherche vectorielle.

Le choix de PostgreSQL se justifie par sa robustesse, sa compatibilité avec SQLAlchemy et la possibilité d'utiliser pgvector pour les embeddings.

Docker Compose permet de lancer localement les services sans installer PostgreSQL directement dans WSL.

## 12. Connexion FastAPI à PostgreSQL

Après l'infrastructure, nous avons connecté FastAPI à PostgreSQL.

Cette étape a introduit les notions suivantes :

- configuration de l'URL de base de données ;
- session SQLAlchemy ;
- modèles persistés ;
- dépendances FastAPI pour obtenir une session de base de données.

L'objectif était de remplacer progressivement les dépôts en mémoire par une vraie persistance.

## 13. Migrations Alembic

Nous avons ensuite ajouté Alembic pour gérer les migrations de base de données.

Alembic permet de versionner les changements de schéma, par exemple la création des tables agents, corpus ou sources documentaires.

Cette étape a clarifié qu'une commande comme `alembic` dépend de l'activation correcte de l'environnement virtuel.

## 14. Persistance des agents

Une fois SQLAlchemy et Alembic en place, les agents ont été persistés dans PostgreSQL.

Cela signifie que les agents ne disparaissent plus au redémarrage de l'API.

Cette étape a transformé la première logique prototype en une base plus réaliste pour la plateforme.

## 15. Cycle de vie des agents

Nous avons ajouté des endpoints liés au cycle de vie des agents.

L'objectif est de préparer une gestion plus réaliste des agents, avec des statuts et transitions contrôlées.

Cette logique sera importante plus tard pour distinguer les agents en brouillon, publiés, archivés ou prêts à utiliser un corpus documentaire.

## 16. Corpus de connaissances

Nous avons ensuite introduit les corpus documentaires.

Un corpus sert à regrouper les documents utilisés par un agent ou une famille d'agents.

Cette étape prépare le futur RAG, car les questions devront être recherchées dans un corpus précis plutôt que dans tous les documents de la plateforme.

Un utilisateur doit pouvoir créer un corpus et récupérer un `corpus_id`, qui sera ensuite utilisé pour rattacher des sources documentaires.

## 17. Sources documentaires et upload PDF

La dernière étape terminée concerne l'ajout des sources documentaires et de l'upload PDF.

Objectif de cette étape :

- permettre l'envoi d'un PDF dans un corpus ;
- stocker le fichier localement dans un dossier non versionné ;
- enregistrer les métadonnées du fichier en base PostgreSQL ;
- lister les sources d'un corpus ;
- refuser les fichiers invalides ou vides ;
- donner à chaque source un statut initial, par exemple `uploaded` ;
- ajouter des tests automatisés utilisant un dossier temporaire plutôt que `.data/documents`.

Cette étape a été validée et commitée côté utilisateur.

## 18. Discussion sur l'automatisation et n8n

Nous avons discuté de l'intérêt éventuel d'intégrer un outil comme n8n.

La conclusion est que n8n peut être pertinent à terme pour les automatisations de processus, mais qu'il ne faut pas l'ajouter immédiatement.

Notre position actuelle :

- FastAPI reste le coeur métier et IA ;
- n8n pourrait plus tard exécuter des workflows externes ;
- l'IA ne doit pas déclencher librement des actions ;
- le backend doit valider les permissions, les paramètres et les approbations humaines ;
- l'architecture doit rester compatible avec un futur moteur d'automatisation.

Principe retenu :

```text
L'IA propose, notre plateforme autorise, n8n exécute.
```

## 19. Extraction du texte des PDF

L'étape d'extraction du texte des PDF a été réalisée avec un service Python isolé.

Objectif de cette étape :

- ouvrir un PDF local ;
- extraire le texte page par page ;
- conserver le numéro de page ;
- rejeter les PDF invalides ;
- signaler les PDF sans texte extractible ;
- tester le comportement sans encore dépendre du flux d'upload complet.

La dépendance retenue est :

```text
PyMuPDF>=1.26,<2
```

Le module utilise PyMuPDF via :

```python
import fitz
```

Les fichiers concernés étaient principalement :

```text
apps/api/requirements.txt
apps/api/app/pdf_extractor.py
apps/api/tests/test_pdf_extractor.py
```

Cette étape est considérée comme terminée.

## 20. Connexion de l'extraction PDF à l'upload

Après le service isolé, nous avons relié l'extraction au flux d'upload PDF.


Le flux visé est devenu :

```text
Upload PDF
  -> stockage local du fichier
  -> création d'une source PDF
  -> extraction du texte
  -> sauvegarde du texte page par page
  -> statut ready ou error
```

Pour cela, nous avons ajouté une table de pages extraites :

```text
source_pages
```
Cette table permet de conserver :

- l'identifiant de la source ;
- le numéro de page ;
- le texte extrait ;
- la date de création.

Nous avons aussi ajouté un endpoint permettant de consulter les pages extraites d'une source :

```text
GET /api/sources/{source_id}/pages
```

Cette étape a introduit ou modifié notamment :

```text
apps/api/app/models.py
apps/api/app/schemas.py
apps/api/app/source_repository.py
apps/api/app/source_service.py
apps/api/app/main.py
apps/api/app/document_storage.py
apps/api/migrations/versions/9a2c0b7d4f6e_create_source_pages_table.py
apps/api/tests/conftest.py
apps/api/tests/test_sources.py
```

Cette étape est considérée comme terminée dans le plan fonctionnel.

## 21. Changement de méthode de travail avec l'assistant

Nous avons ensuite changé la façon de travailler avec l'assistant.

Préférence retenue :

- l'assistant ne modifie plus directement les fichiers du dépôt quand ce n'est pas nécessaire ;
- l'assistant fournit plutôt les blocs de code à insérer ;
- l'utilisateur applique les changements localement ;
- l'utilisateur lance les tests ;
- l'utilisateur fait lui-même les commits, pushs, Pull Requests et merges.

Le format souhaité pour les prochaines étapes est donc :

```text
1. nom de la branche à créer ;
2. fichiers à créer ou modifier ;
3. blocs de code exacts à insérer ;
4. commandes de test ;
5. commandes git add / commit / push ;
6. consignes de Pull Request ou de merge.
```
## 22. Découpage du texte extrait en chunks

L'étape suivante réalisée avec succès a été le découpage du texte extrait en chunks.

L'objectif était de préparer le futur RAG sans encore ajouter les embeddings ni pgvector.

Le flux de cette étape est :

```text
source_pages
  -> texte page par page
  -> découpage en chunks
  -> conservation du numéro de page
  -> conservation de l'index du chunk
```

Le service de chunking reste isolé et ne persiste pas encore les chunks en base.

Les fichiers proposés pour cette étape étaient :

```text
apps/api/app/text_chunker.py
apps/api/tests/test_text_chunker.py
```

Le service introduit notamment les concepts suivants :

- `SourcePageText` : représentation simple d'une page extraite ;
- `TextChunk` : morceau de texte découpé ;
- `max_chunk_size` : taille maximale d'un chunk ;
- `chunk_overlap` : chevauchement entre deux chunks ;
- validation de la configuration de chunking.

Les tests couvraient notamment :

- texte plus court que la taille maximale ;
- normalisation des espaces ;
- découpage avec overlap ;
- texte vide ;
- conservation des numéros de page ;
- rejet des configurations invalides.

Un premier échec de test a été corrigé : le texte choisi pour la deuxième page était plus long que `max_chunk_size`, donc il produisait plusieurs chunks alors que le test attendait un seul chunk. Le test a été corrigé avec un texte plus court, par exemple :

```text
Court.
```

Cette étape est la dernière étape considérée comme faite avec succès.

## 23. Dernière limite rencontrée

Nous avons ensuite commencé à préparer l'étape suivante : la persistance des chunks dans PostgreSQL avec une table `source_chunks`.

Cependant, cette étape n'est pas encore considérée comme terminée.

Des problèmes de tests ont été rencontrés autour de l'intégration entre :

- `source_pages` ;
- `source_chunks` ;
- `SourceRepository` ;
- les fixtures de test ;
- la sauvegarde et la récupération des pages extraites.

La dernière situation observée était :

```text
source.status == "ready"
GET /api/sources/{source_id}/pages retourne []
```


Cela indique qu'une source pouvait être marquée `ready` sans que les pages extraites soient réellement retrouvées par les tests.


Cette étape doit donc être reprise proprement plus tard, mais elle ne doit pas être considérée comme validée.

## 24. Prochaine étape recommandée

La prochaine étape doit être :

```text
Persister les chunks en base de données
```

Mais elle doit être reprise prudemment, en partant de la dernière base stable :

```text
PDF uploadé
  -> texte extrait page par page
  -> source_pages validé
  -> text_chunker isolé validé
```

Objectif de la prochaine étape :

- créer une table `source_chunks` ;
- relier chaque chunk à une source et à une page source ;
- ajouter une migration Alembic ;
- ajouter un service de traitement des chunks persistés ;
- ajouter un endpoint pour générer les chunks d'une source ;
- ajouter un endpoint pour lister les chunks ;
- tester d'abord le repository et le service de manière ciblée ;
- ensuite seulement tester l'API complète.

La branche recommandée sera :

```bash
git switch main
git pull
git switch -c persist-source-chunks
```

Il faudra éviter de mélanger cette étape avec les embeddings ou pgvector.

## 25. Étapes futures après la persistance des chunks

Une fois les chunks persistés et testés, les prochaines étapes probables seront :

1. ajouter pgvector et une structure pour stocker les embeddings ;
2. générer des embeddings pour les chunks ;
3. ajouter une recherche vectorielle par corpus ;
4. créer un endpoint de question/réponse sourcée ;
5. construire l'interface frontend pour interroger un agent ;
6. plus tard seulement, envisager des automatisations contrôlées.

## 26. Principe à conserver pour la suite

Nous devons continuer avec la même logique :

- une branche par étape ;
- une fonctionnalité limitée ;
- des tests ciblés ;
- correction des erreurs avant d'avancer ;
- commit clair ;
- push ;
- Pull Request ou merge selon la méthode choisie par l'utilisateur ;
- retour sur `main` avant la prochaine étape.

Le principe important reste :

```text
Ne pas passer à pgvector ou aux embeddings tant que les chunks persistés ne sont pas propres et testés.
```