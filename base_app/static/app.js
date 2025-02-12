// CONFIGURATION DE TAILWIND
tailwind.config = {
    theme: {
        extend: {
            fontFamily: {
                sans: ["Montserrat", "sans-serif"]
            }
        }
    }
};



// GRAPHIQUE AVEC CHART.JS
// Configuration
const ctx = document.getElementById('mailChart').getContext('2d');
new Chart(ctx, {
    type: 'bar', // Type de graphique (barres verticales)
    data: {
        labels: mailData.labels, // Mois (labels)
        datasets: [{
            label: 'Nombre de mails envoyés',
            data: mailData.values, // Nombre de mails par mois
            backgroundColor: 'rgba(75, 192, 192, 0.2)', // Couleur des barres
            borderColor: 'rgba(75, 192, 192, 1)', // Couleur des bordures
            borderWidth: 1 // Épaisseur des bordures
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true, // Commencer l'axe Y à 0
                ticks: {
                    stepSize: 1, // Toujours incrémenter par 1 (pas de 0.5)
                    callback: function(value) {
                        return Number.isInteger(value) ? value : ''; // Afficher uniquement les entiers
                    }
                },
                title: {
                    display: true,
                    text: 'Nombre de mails', // Titre de l'axe Y
                    font: {
                        size: 14,
                        weight: 'bold' // Texte en gras pour l'axe Y
                    }
                }
            },
            x: {
                title: {
                    display: true,
                    text: 'Mois', // Titre de l'axe X
                    font: {
                        size: 14,
                        weight: 'bold' // Texte en gras pour l'axe Y
                    }
                }
            }
        }
    }
});




// FONCTIONNALITÉ D'INFOS-BULLES
function showInfo(event) {
    event.preventDefault();

    const name = event.target.getAttribute('data-name');
    const category = event.target.getAttribute('data-category');
    const email = event.target.getAttribute('data-email');
    const firstname = event.target.getAttribute('data-firstname');
    const lastname = event.target.getAttribute('data-lastname');

    const tooltipContent = `
        <div>
            <span class="font-bold">Nom :</span> ${firstname} ${lastname}<br>
            <span class="font-bold">Catégorie :</span> ${category}<br>
            <span class="font-bold">Email :</span> ${email}
        </div>
    `;

    const tooltip = document.createElement('div');
    tooltip.classList.add('tooltip');
    tooltip.innerHTML = tooltipContent;

    tooltip.style.position = 'absolute';
    tooltip.style.backgroundColor = '#fff';
    tooltip.style.border = '1px solid #ccc';
    tooltip.style.borderRadius = '5px';
    tooltip.style.padding = '10px';
    tooltip.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)';
    tooltip.style.zIndex = '1000';

    const rect = event.target.getBoundingClientRect();
    tooltip.style.left = `${rect.left}px`;
    tooltip.style.top = `${rect.bottom + window.scrollY}px`;

    document.body.appendChild(tooltip);

    tooltip.addEventListener('click', (e) => {
        tooltip.remove();
    });

    setTimeout(() => {
        tooltip.remove();
    }, 5000); // L'infobulle disparaît après 5 secondes
}


// BARRE DE RECHERCHE
function surligne(text, lettres) {
    if (!lettres) return text;
    const regex = new RegExp(`(${lettres})`, 'gi');
    return text.replace(regex, '<span class="bg-yellow-300">$1</span>');
}

function filterEmployees(columnIndex) {
    let searchValue = '';
    if (columnIndex === 0) {
        searchValue = document.getElementById('search-firstname').value.toLowerCase();
    } else {
        searchValue = document.getElementById('search-lastname').value.toLowerCase();
    }
    let rows = document.querySelectorAll('table tbody tr');

    rows.forEach(row => {
        let cell = row.cells[columnIndex];
        let cellValue = row.cells[columnIndex].textContent.toLowerCase();

        if (cellValue.includes(searchValue) || searchValue === '') {
            cell.innerHTML = surligne(cell.textContent, searchValue);
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}