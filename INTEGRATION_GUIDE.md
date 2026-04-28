# 🎯 GUIDE D'INTÉGRATION - Planning Global avec API Backend

## 📋 Vue d'ensemble

Vous avez maintenant:
- ✅ **Frontend statique** fonctionnel dans `planning_global.html`
- ✅ **CSS/Styling** complet dans `planning_global.css`
- ✅ **Structure JavaScript** prête pour l'intégration dans `planning_global.js`
- ✅ **API Backend** créée et routée dans `views.py` et `urls.py`

---

## 🔧 Étapes d'intégration

### **Étape 1: Vérifier que l'API fonctionne**

1. Allez sur: `http://localhost:8000/rh/api/planning/2026/5/`
   - Cela devrait retourner un JSON avec les données du planning de mai 2026

2. Format attendu du retour JSON:
```json
{
    "month": "Mai 2026",
    "employees": [
        {
            "id": 1,
            "name": "Jean Dupont",
            "role": "Développeur",
            "avatar_initials": "JD",
            "avatar_color": "#FFB6C1",
            "available_today": false,
            "total_days_in_month": 31,
            "absences": [
                {
                    "date": "2026-05-08",
                    "type": "congé",
                    "label": "Congé"
                }
            ]
        },
        // ... autres employés
    ],
    "available_count": 6,
    "total_count": 8,
    "today": "2026-04-28"
}
```

---

### **Étape 2: Activer le chargement des données dans le frontend**

Dans le fichier `planning_global.js`, il y a une fonction `loadPlanningDataFromDB()` prête à l'emploi.

**Pour l'activer, mettez à jour la fonction `changeMonth()`:**

Cherchez cette ligne dans `planning_global.js`:
```javascript
function changeMonth(direction) {
    planningState.currentMonth += direction;
    
    if (planningState.currentMonth > 12) {
        planningState.currentMonth = 1;
        planningState.currentYear += 1;
    } else if (planningState.currentMonth < 1) {
        planningState.currentMonth = 12;
        planningState.currentYear -= 1;
    }
    
    updateMonthDisplay();
    // Ici, vous ferez un appel API pour charger les données du nouveau mois
    // loadPlanningDataFromDB(planningState.currentMonth, planningState.currentYear);
}
```

**Et décommentez/ajoutez cet appel:**
```javascript
function changeMonth(direction) {
    planningState.currentMonth += direction;
    
    if (planningState.currentMonth > 12) {
        planningState.currentMonth = 1;
        planningState.currentYear += 1;
    } else if (planningState.currentMonth < 1) {
        planningState.currentMonth = 12;
        planningState.currentYear -= 1;
    }
    
    updateMonthDisplay();
    // 👇 DÉCOMMENTEZ CETTE LIGNE:
    loadPlanningDataFromDB(planningState.currentMonth, planningState.currentYear);
}
```

---

### **Étape 3: Charger les données au démarrage de la page**

Ajoutez aussi cet appel dans la fonction `initializePlanning()`:

```javascript
function initializePlanning() {
    updateMonthDisplay();
    updateDaysHeader();
    // Charger les données du mois courant
    loadPlanningDataFromDB(planningState.currentMonth, planningState.currentYear);
}
```

---

## 📊 Comment ça marche (Flux d'intégration)

### **1. Charger les données (Frontend → API)**

```javascript
// L'utilisateur ouvre la page ou change de mois
loadPlanningDataFromDB(5, 2026);

// Cela envoie une requête GET à:
// GET /rh/api/planning/2026/5/
```

### **2. Backend traite la demande**

```python
# La fonction api_planning_global() dans views.py:
# 1. Récupère tous les employés
# 2. Récupère leurs congés acceptés pour le mois
# 3. Vérifie qui est disponible aujourd'hui
# 4. Construit la réponse JSON
```

### **3. Afficher les données (JSON → DOM)**

```javascript
// La fonction populatePlanningWithData() prend le JSON et:
// 1. Met à jour le compteur de disponibilité
// 2. Crée les lignes employés dynamiquement
// 3. Remplit les cellules avec les absences
// 4. Re-attache les event listeners
```

---

## 🎨 Types d'absences supportées

L'API supporte actuellement: `congé`, `formation`, `maladie`, `repos`

Les couleurs sont définies dans le CSS:
- **Congé**: `#8B4454` (marron)
- **Formation**: `#CD7F32` (bronze)
- **Maladie**: `#DC143C` (rouge)
- **Repos**: `#696969` (gris foncé)
- **Télétravail**: `#20B2AA` (turquoise)

Pour ajouter d'autres types, mettez à jour le dictionnaire dans `views.py`:
```python
absence_types = {
    'congé': 'Congé',
    'formation': 'Formation',
    'maladie': 'Maladie',
    'repos': 'Repos',
    'votre_type': 'Votre label'  # ← Ajoutez ici
}
```

Et ajoutez le CSS correspondant dans `planning_global.css`:
```css
.day-cell.absence[data-type="votre_type"] {
    background-color: #COULEUR;
    color: white;
}
```

---

## 🔌 Points d'extensibilité

### **Filtrage par équipe/département**

Actuellement le bouton "Toutes les équipes" ne fait rien. Pour l'implémenter:

1. **Backend**: Modifiez `api_planning_global()` pour accepter un paramètre `team`:
```python
def api_planning_global(request, year, month):
    team = request.GET.get('team', None)
    if team:
        employees = employees.filter(department=team)  # Selon votre structure
    # ... reste du code
```

2. **URL**: Ajoutez la variable GET à l'URL (elle est optionnelle)

3. **Frontend**: Écoutez le clic sur le bouton filtre:
```javascript
document.querySelector('.filter-btn').addEventListener('click', function() {
    const team = this.textContent;
    loadPlanningDataFromDB(
        planningState.currentMonth,
        planningState.currentYear,
        team
    );
});
```

### **Filtrer par type d'absence**

Similaire au filtrage par équipe, mais côté frontend en JavaScript (plus rapide):

```javascript
function filterByType(type) {
    document.querySelectorAll('.day-cell.absence').forEach(cell => {
        if (type === 'all' || cell.getAttribute('data-type') === type) {
            cell.style.display = 'flex';
        } else {
            cell.style.display = 'none';
        }
    });
}
```

### **Exporter en CSV**

La fonction `exportToCSV()` est déjà implémentée et fonctionne avec les données affichées.

---

## 🚀 Cas d'usage avancés

### **Ajouter un congé au clic**

Écoutez les clics sur les cellules vides:

```javascript
document.querySelectorAll('.day-cell:not(.absence)').forEach(cell => {
    cell.addEventListener('click', function() {
        const day = this.textContent;
        const employeeId = this.closest('.employee-row').getAttribute('data-employee-id');
        showCreateAbsenceModal(employeeId, day);
    });
});
```

### **Modal pour voir les détails d'une absence**

```javascript
function showAbsenceDetails(e) {
    const cell = e.target;
    if (!cell.classList.contains('absence')) return;
    
    const type = cell.getAttribute('data-type');
    const employeeRow = cell.closest('.employee-row');
    const employeeName = employeeRow.querySelector('.employee-name').textContent;
    
    // Afficher une modal avec les détails
    alert(`${employeeName} - ${type}`);
}
```

### **Sync en temps réel avec WebSocket**

Pour que les changements d'absences soient visibles en temps réel:

```javascript
// Dans planning_global.js
const socket = new WebSocket('ws://localhost:8000/rh/ws/planning/');

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    if (data.type === 'absence_updated') {
        // Recharger les données
        loadPlanningDataFromDB(
            planningState.currentMonth,
            planningState.currentYear
        );
    }
};
```

---

## ✅ Checklist d'implémentation

- [ ] API endpoint testé manuellement
- [ ] Frontend statique affiché correctement
- [ ] `loadPlanningDataFromDB()` décommentée/activée
- [ ] Les données se chargent au démarrage de la page
- [ ] La navigation mois charge les nouvelles données
- [ ] Les couleurs des absences s'affichent correctement
- [ ] Le compteur de disponibilité est correct
- [ ] Export CSV fonctionne
- [ ] Responsive design sur mobile

---

## 🐛 Dépannage

### **Les données ne se chargent pas**

1. Ouvrez la console du navigateur (F12)
2. Vérifiez s'il y a une erreur de CORS ou 404
3. Testez directement l'API: `http://localhost:8000/rh/api/planning/2026/5/`

### **Le token CSRF cause une erreur**

La fonction `getCSRFToken()` est fournie, mais vérifiez que:
```python
# Dans settings.py, ces middlewares sont présents:
MIDDLEWARE = [
    ...
    'django.middleware.csrf.CsrfViewMiddleware',
    ...
]
```

### **Les congés ne s'affichent pas**

1. Vérifiez que les congés sont en statut `"Accepté"` dans la BD
2. Vérifiez que les dates sont dans le bon mois/année
3. Vérifiez les logs Django: `python manage.py runserver` avec debug actif

---

## 📈 Prochaines étapes suggérées

1. **Ajouter l'édition des absences** (modal form)
2. **Implémenter les filtres** (équipe, type d'absence)
3. **Ajouter les notifications** quand un congé change de statut
4. **Optimiser les performances** avec pagination
5. **Ajouter des statistiques** (jours restants par employé, etc.)

---

## 📚 Références

- **Frontend**: `rh/templates/rh/planning_global.html`
- **Styles**: `rh/static/rh/css/planning_global.css`
- **JavaScript**: `rh/static/rh/js/planning_global.js`
- **API Backend**: `rh/views.py` - fonction `api_planning_global()`
- **Routes**: `rh/urls.py` - chemin `api/planning/<int:year>/<int:month>/`
- **Modèles**: `rh/models.py` - `Conge`, et `employees/models.py` - `EmployeeProfile`
