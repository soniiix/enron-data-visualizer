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




// PAGE D'ERREUR, POUR COPIER LA COMMANDE
function copyToClipboard(cmdId) {
    const text = document.getElementById(cmdId).innerText;
    const icon = document.getElementById("icon-" + cmdId);
    icon.className = "fa-solid fa-check";
    icon.style.color="green";
    // Remettre l'icône de base après 2.5 secondes
    setTimeout(() => {
        icon.className = "fa-regular fa-clone hover:cursor-pointer";
        icon.style.color = "";
    }, 2500);
    navigator.clipboard.writeText(text);
}




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
function filterEmployees(){
    document.querySelectorAll("input[type=text]")[0].addEventListener("input", function(){
        var prenom = document.querySelectorAll("input[type=text]")[0].value.toLowerCase()
        Array.from(document.querySelectorAll("#personne")).forEach(
            (x) => {
                var firstName = x.querySelectorAll("span")[0].textContent.toLowerCase();
                if(firstName.includes(prenom)){x.style.display = ""}
                else{x.style.display = "none"}
            }
        )
    })

    document.querySelectorAll("input[type=text]")[1].addEventListener("input", function(){
        var nom = document.querySelectorAll("input[type=text]")[1].value.toLowerCase();
        Array.from(document.querySelectorAll("#personne")).forEach(
            (x) => {
                var lastName = x.querySelectorAll("span")[1].textContent.toLowerCase();;
                if(lastName.includes(nom)){x.style.display = ""}
                else{x.style.display = "none"}
            }
        )
    })
}
filterEmployees();