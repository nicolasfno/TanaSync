// ==================== PLANNING GLOBAL - JAVASCRIPT ==================== //

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the planning view
    initializePlanning();
    setupEventListeners();
    // Charger les données du mois courant
    loadPlanningDataFromDB(planningState.currentMonth, planningState.currentYear);
});

/**
 * STRUCTURE DE DONNÉES ATTENDUES DU BACKEND
 * 
 * Format JSON que le backend devrait envoyer:
 * {
 *     "current_date": "2026-04-28",
 *     "month": "Mai 2026",
 *     "employees": [
 *         {
 *             "id": 1,
 *             "name": "Jean Dupont",
 *             "role": "Développeur",
 *             "avatar_initials": "JD",
 *             "avatar_color": "#FFB6C1",
 *             "available_today": true,
 *             "total_days_in_month": 31,
 *             "absences": [
 *                 {
 *                     "date": "2026-05-08",
 *                     "type": "congé",  // ou "formation", "maladie", "repos"
 *                     "label": "Congé"
 *                 },
 *                 {
 *                     "date": "2026-05-09",
 *                     "type": "congé",
 *                     "label": "Congé"
 *                 }
 *             ]
 *         }
 *     ],
 *     "today": "2026-04-28",
 *     "available_count": 6,
 *     "total_count": 8
 * }
 */

// Global state
const planningState = {
    currentDate: new Date(2026, 4, 28), // Mai 2026 (mois 0-indexed)
    currentMonth: 5, // 1-12
    currentYear: 2026,
    employees: [],
    absences: {}
};

/**
 * Initialiser le planning avec les données statiques
 */
function initializePlanning() {
    updateMonthDisplay();
    updateDaysHeader();
}

/**
 * Mettre à jour l'affichage du mois
 */
function updateMonthDisplay() {
    const monthNames = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
        'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'];
    
    const monthEl = document.getElementById('current-month');
    const monthName = monthNames[planningState.currentMonth - 1];
    monthEl.textContent = `${monthName} ${planningState.currentYear}`;
}

/**
 * Mettre à jour les en-têtes des jours
 */
function updateDaysHeader() {
    const daysHeader = document.getElementById('days-header');
    // Les jours sont déjà statiques dans le HTML pour cette version
}

/**
 * Configuration des event listeners
 */
function setupEventListeners() {
    // Navigation mois précédent
    document.querySelector('.prev-month').addEventListener('click', function() {
        changeMonth(-1);
    });

    // Navigation mois suivant
    document.querySelector('.next-month').addEventListener('click', function() {
        changeMonth(1);
    });

    // Export CSV
    document.querySelector('.export-btn').addEventListener('click', function() {
        exportToCSV();
    });

    // Day cell interactivity
    document.querySelectorAll('.day-cell').forEach(cell => {
        cell.addEventListener('click', function(e) {
            if (this.classList.contains('absence') || this.classList.contains('available')) {
                showAbsenceDetails(e);
            }
        });
    });
}

/**
 * Changer le mois
 */
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
    // Charger les données du nouveau mois
    loadPlanningDataFromDB(planningState.currentMonth, planningState.currentYear);
}

/**
 * Exporter les données en CSV
 */
function exportToCSV() {
    let csvContent = 'data:text/csv;charset=utf-8,';
    csvContent += 'Employé,Rôle,';
    
    // Ajouter les jours
    for (let i = 1; i <= 18; i++) {
        csvContent += `Jour ${i},`;
    }
    csvContent += '\n';
    
    // Ajouter les données des employés
    document.querySelectorAll('.employee-row').forEach(row => {
        const name = row.querySelector('.employee-name').textContent;
        const role = row.querySelector('.employee-role').textContent;
        csvContent += `${name},${role},`;
        
        row.querySelectorAll('.days-row .day-cell').forEach(cell => {
            const content = cell.textContent.trim();
            csvContent += `"${content}",`;
        });
        csvContent += '\n';
    });
    
    // Créer le lien de téléchargement
    const link = document.createElement('a');
    link.setAttribute('href', encodeURI(csvContent));
    link.setAttribute('download', `planning_${planningState.currentMonth}_${planningState.currentYear}.csv`);
    link.click();
}

/**
 * Afficher les détails d'une absence au clic
 */
function showAbsenceDetails(e) {
    const cell = e.target;
    const type = cell.getAttribute('data-type');
    const employeeRow = cell.closest('.employee-row');
    const employeeName = employeeRow.querySelector('.employee-name').textContent;
    
    console.log(`Absence: ${type} for ${employeeName}`);
    // Ici, vous pouvez ajouter une modal ou un détail
}

/**
 * ================= FONCTION D'INTÉGRATION BACKEND =================
 * 
 * Cette fonction sera appelée après le chargement de la page
 * pour remplir le planning avec les données réelles de la BD
 */
async function loadPlanningDataFromDB(month, year) {
    try {
        // Appel API au backend
        const response = await fetch(`/rh/api/planning/${year}/${month}/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        });

        if (!response.ok) {
            throw new Error('Erreur lors du chargement des données');
        }

        const data = await response.json();
        
        // Remplir le planning avec les données
        populatePlanningWithData(data);
        
    } catch (error) {
        console.error('Erreur:', error);
    }
}

/**
 * Remplir le planning avec les données du backend
 */
function populatePlanningWithData(data) {
    // Mettre à jour le compteur de disponibilités
    document.getElementById('available-count').textContent = data.available_count;
    document.getElementById('total-count').textContent = data.total_count;

    // Effacer les lignes existantes
    const gridBody = document.querySelector('.grid-body');
    gridBody.innerHTML = '';

    // Créer les lignes pour chaque employé
    data.employees.forEach(employee => {
        const row = createEmployeeRow(employee);
        gridBody.appendChild(row);
    });

    // Re-attacher les event listeners
    setupEventListeners();
}

/**
 * Créer une ligne d'employé dynamiquement
 */
function createEmployeeRow(employee) {
    const row = document.createElement('div');
    row.className = 'employee-row';
    row.setAttribute('data-employee-id', employee.id);

    // Infos employé
    const employeeInfo = document.createElement('div');
    employeeInfo.className = 'employee-info';
    employeeInfo.innerHTML = `
        <div class="employee-avatar" style="background-color: ${employee.avatar_color};">
            ${employee.avatar_initials}
        </div>
        <div class="employee-details">
            <div class="employee-name">${employee.name}</div>
            <div class="employee-role">${employee.role}</div>
        </div>
    `;

    // Jours
    const daysRow = document.createElement('div');
    daysRow.className = 'days-row';

    // Créer les cellules pour chaque jour du mois
    for (let day = 1; day <= employee.total_days_in_month; day++) {
        const dayCell = document.createElement('div');
        dayCell.className = 'day-cell';

        // Vérifier s'il y a une absence ce jour
        const absence = employee.absences.find(a => {
            const absenceDate = new Date(a.date);
            return absenceDate.getDate() === day;
        });

        if (absence) {
            dayCell.classList.add('absence');
            dayCell.setAttribute('data-type', absence.type);
            dayCell.setAttribute('title', absence.label);
            dayCell.textContent = absence.label;
        }

        daysRow.appendChild(dayCell);
    }

    row.appendChild(employeeInfo);
    row.appendChild(daysRow);

    return row;
}

/**
 * Obtenir le token CSRF pour les requêtes POST
 */
function getCSRFToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Fonction à appeler pour charger les données au changement de mois
 * Remplacez l'appel dans changeMonth() :
 * 
 * function changeMonth(direction) {
 *     // ... code existant ...
 *     loadPlanningDataFromDB(planningState.currentMonth, planningState.currentYear);
 * }
 */
