# 🏉 RAG Rugby Chatbot

## 🌐 Application déployée (via Cloudflared : mon pc doit donc etre allumé au moment ou vous accédez à l'appli, sinon ça ne marchera pas)
**URL publique** : [https://rag-rugby.omar.christianmbip.engineer](https://rag-rugby.omar.christianmbip.engineer)

## 📋 Concept de l'application

Cette application est un chatbot intelligent basé sur la technique **RAG (Retrieval-Augmented Generation)** qui répond à des questions sur les règles du rugby en français. 

### Fonctionnement
1. **Ingestion** : Le document PDF "regles-du-rugby.pdf" (216 pages) est chargé et divisé en chunks de 1000 caractères
2. **Vectorisation** : Chaque chunk est transformé en embeddings avec le modèle `nomic-embed-text`
3. **Stockage** : Les embeddings sont stockés dans une base vectorielle Chroma persistante
4. **Recherche** : Lorsqu'une question est posée, les 3 chunks les plus pertinents sont récupérés
5. **Génération** : Le modèle `Llama 3.2` génère une réponse concise basée sur le contexte récupéré

### Caractéristiques
- ✅ Réponses précises basées uniquement sur le document source
- ✅ Interface web intuitive avec Gradio
- ✅ Cache LRU pour optimiser les questions répétées
- ✅ Nettoyage automatique des balises XML dans les réponses
- ✅ Déploiement avec Docker et tunnel Cloudflare

---

## 🚀 Installation et exécution en local

### Prérequis
- Docker et Docker Compose installés
- 8 GB de RAM minimum (recommandé : 16 GB)
- Connexion internet pour télécharger les modèles

### Étapes d'installation

#### 1. Cloner le projet
```bash
git clone https://github.com/Om1-ba/chat-bot-RAG-Rugby-.git
cd chat-bot-RAG-Rugby-
```

#### 2. Structure des fichiers
Assurez-vous d'avoir cette structure :
```
.
├── docker-compose.yml
├── Dockerfile
├── main.py
├── requirements.txt
├── regles-du-rugby.pdf
```

#### 3. Lancer les conteneurs Docker
```bash
docker-compose up -d
```

#### 4. Télécharger les modèles Ollama
**⚠️ IMPORTANT** : Téléchargez les modèles avant de lancer l'application
```bash
# Télécharger Llama 3.2 (~2 GB) - peut prendre 5-10 minutes
docker exec -it ollama ollama pull llama3.2

# Télécharger nomic-embed-text (~274 MB) - environ 1-2 minutes
docker exec -it ollama ollama pull nomic-embed-text
```

**Vérifier que les modèles sont installés :**
```bash
docker exec -it ollama ollama list
```

Vous devriez voir :
```
NAME                    ID              SIZE
llama3.2:latest         a80c4f17acd5    2.0 GB
nomic-embed-text:latest 0a109f422b47    274 MB
```

#### 5. Redémarrer l'application RAG
```bash
docker-compose restart rag-app
```

#### 6. Accéder à l'interface
Ouvrez votre navigateur : **http://localhost:7860**

### Commandes utiles
```bash
# Voir les logs en temps réel
docker-compose logs -f rag-app

# Vérifier l'état des conteneurs
docker-compose ps

# Redémarrer uniquement le chatbot
docker-compose restart rag-app

# Arrêter tous les conteneurs
docker-compose down

# Supprimer les volumes (réinitialiser la base vectorielle)
docker-compose down -v

# Accéder au shell du conteneur Ollama
docker exec -it ollama bash
```

---

## 🛠️ Choix techniques

### Architecture
- **Docker Compose** : Orchestration de deux services (Ollama + Application)
- **Volumes persistants** : 
  - `ollama_data` : Stocke les modèles téléchargés
  - `chroma_data` : Conserve la base vectorielle entre les redémarrages

### Stack technique
| Composant | Technologie | Justification |
|-----------|-------------|---------------|
| **LLM** | Llama 3.2 | Modèle léger (2GB) avec bon équilibre qualité/rapidité |
| **Embeddings** | nomic-embed-text | Optimisé pour la recherche sémantique |
| **Vector DB** | ChromaDB | Léger, simple, avec persistance locale |
| **Framework** | LangChain | Abstraction RAG et intégration Ollama |
| **Interface** | Gradio | Déploiement rapide d'UI avec partage public |
| **PDF Parser** | PyMuPDF | Extraction de texte robuste |
| **Tunnel** | Cloudflare Argo | Exposition sécurisée sans configuration réseau |

### Optimisations implémentées
1. **Cache LRU** (`@lru_cache`) : Évite de recalculer les réponses identiques
2. **Réduction du contexte** : 3 chunks au lieu de 4 (balance pertinence/vitesse)
3. **Température basse** (0.1) : Réponses plus déterministes et rapides
4. **Persistance Chroma** : La vectorisation ne se fait qu'une seule fois

---

## ⚠️ Limitations et améliorations possibles

### Limitations actuelles
1. **Langue** : Uniquement le français (lié au PDF source)
2. **Monodocument** : L'application ne traite qu'un seul PDF
3. **Pas de streaming** : Les réponses apparaissent d'un coup (Gradio ne supporte pas le streaming Ollama nativement)
4. **Ressources** : Nécessite un serveur avec GPU pour de meilleures performances (actuellement CPU)
5. **Pas de mémoire conversationnelle** : Chaque question est traitée indépendamment

### Améliorations possibles
- [ ] Ajouter un système de conversation multi-tours avec historique
- [ ] Supporter le téléversement de PDFs personnalisés
- [ ] Implémenter un système de feedback utilisateur (👍/👎)
- [ ] Ajouter des métadonnées (numéros de page) dans les réponses
- [ ] Migrer vers un modèle avec GPU (ex: via Modal, Runpod)
- [ ] Interface multilingue avec traduction automatique
- [ ] Ajout de graphiques de similarité des chunks récupérés

---

## 🔧 Dépannage

### Problème : "Connection refused" lors du lancement
**Solution** : Vérifiez que les modèles sont téléchargés
```bash
docker exec -it ollama ollama list
```

### Problème : L'application ne trouve pas les modèles
**Solution** : Redémarrez le conteneur après téléchargement
```bash
docker-compose restart rag-app
```

### Problème : Réponses très lentes
**Causes possibles** :
- CPU uniquement (pas de GPU)
- RAM insuffisante
- Modèle trop lourd

**Solution** : Réduire `chunk_size` ou utiliser un modèle plus petit

---

## 🌐 Application déployée (via Cloudflared : mon pc doit donc etre allumé au moment ou vous accédez à l'appli, sinon ça ne marchera pas)

**URL publique** : [https://rag-rugby.omar.christianmbip.engineer](https://rag-rugby.omar.christianmbip.engineer)

> ⚠️ **Note** : Le tunnel Cloudflare nécessite que le service soit actif en permanence. Si l'URL ne répond pas, relancez le tunnel avec :
> ```bash
> cloudflared tunnel run rag-rugby
> ```

---

## 👥 Auteurs

**Christian & Omar** | Projet RAG - Guide du Rugby  
Alimenté par Llama 3.2 et Ollama

---

## 📄 Licence

Ce projet est à usage éducatif. Le document "regles-du-rugby.pdf" appartient à ses auteurs respectifs.
