# Comment Démarrer le Backend DermaFlow AI

## Méthode la Plus Simple (Recommandée)

### 1. Double-Cliquez
1. Ouvrez l'Explorateur de Fichiers
2. Allez dans : `C:\Users\Pc\Desktop\clinicflow-ai\`
3. **Double-cliquez** sur `start-server-simple.bat`
4. Une fenêtre de commande s'ouvrira et le serveur démarrera
5. La documentation API s'ouvrira automatiquement dans votre navigateur
6. **Gardez cette fenêtre OUVERTE** - ne la fermez pas !

### 2. Ouvrir le Frontend
1. Ouvrez un autre dossier dans l'Explorateur de Fichiers
2. Allez dans : `C:\Users\Pc\Desktop\clinicflow-ai\frontend\`
3. Double-cliquez sur `inscription.html` pour accéder à la page de création de compte
   OU double-cliquez sur `connexion.html` pour accéder à la page de connexion

---

## Depuis VS Code (Si vous préférez)

### Méthode A : Utilisation de la Configuration de Lancement
1. Ouvrez VS Code
2. Ouvrez le dossier du projet : `C:\Users\Pc\Desktop\clinicflow-ai\`
3. Appuyez sur `Ctrl+Maj+D` (ou cliquez sur l'icone Run à gauche)
4. Sélectionnez "Start Backend" dans le menu déroulant
5. Appuyez sur `F5` ou cliquez sur le bouton vert de lecture

### Méthode B : Utilisation du Terminal
1. Ouvrez VS Code
2. Appuyez sur `` Ctrl+` `` (backtick) pour ouvrir le terminal
3. Exécutez ces commandes :
```bash
cd backend
.\venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## Points d'Accès

Une fois démarré, tout est disponible à :

| URL | Description |
|-----|-----------|
| `http://localhost:8000` | Backend API |
| `http://localhost:8000/docs` | Documentation API interactive |
| `http://localhost:8000/health` | Vérification de santé (affichera `{"status":"sain"}`) |

---

## Fichiers Frontend

Ouvrez-les dans votre navigateur (double-cliquez) :

| Fichier | Objectif |
|---------|----------|
| `frontend/inscription.html` | Créer un nouveau compte |
| `frontend/connexion.html` | Page de connexion |
| `frontend/tableau_bord_patient.html` | Tableau de bord patient |
| `frontend/tableau_bord_dermatologue.html` | Tableau de bord médecin |
| `frontend/tableau_bord_admin.html` | Tableau de bord administrateur |

---

## Dépannage

### Erreur "Failed to fetch" ?
→ Le backend n'est pas lancé. Exécutez `start-server-simple.bat` d'abord.

### "Port 8000 déjà utilisé" ?
→ Un autre programme utilise le port 8000. Fermez-le ou utilisez un autre port.

### Environnement virtuel non trouvé ?
→ Créez-en un nouveau :
```bash
cd backend
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
.\venv\Scripts\pip install email-validator requests
```

### Toujours pas fonctionnel ?
1. Vérifiez que Python est installé : `python --version`
2. Vérifiez que pip est installé : `pip --version`
3. Assurez-vous d'être dans le bon dossier

---

## Checklist de Démarrage Rapide

- [ ] Double-cliquez sur `start-server-simple.bat`
- [ ] Attendez le message "Application startup complete"
- [ ] Ouvrez `http://localhost:8000/docs` dans votre navigateur (devrait fonctionner)
- [ ] Ouvrez `frontend/inscription.html` dans un autre onglet
- [ ] Essayez de créer un compte !

---

## Conseils Professionnels

1. **Épinglez le fichier batch à votre barre de tâches** : Clic droit sur `start-server-simple.bat` → "Épingler à la barre de tâches"
2. **Créez un raccourci sur le bureau** : Clic droit sur `start-server-simple.bat` → "Envoyer vers" → "Bureau"
3. **Utilisez l'extension Live Server** dans VS Code pour le frontend (optionnel mais pratique)

---

**Besoin d'aide ?** Vérifiez que :
- La fenêtre du backend est ouverte et affiche "Uvicorn running"
- Vous utilisez `http://localhost:8000` (et non `https`)
- Aucun pare-feu ne bloque le port 8000
