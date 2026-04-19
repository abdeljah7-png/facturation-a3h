document.addEventListener("DOMContentLoaded", function () {
    // Sélection du client dans le formulaire Devis
    const clientSelect = document.querySelector('select[name="client"]');

    if (!clientSelect) {
        console.log("Select client non trouvé dans l'admin");
        return;
    }

    clientSelect.addEventListener("change", function () {
        const clientId = this.value;
        if (!clientId) return;

        fetch("/client-info/" + clientId + "/")
            .then(response => response.json())
            .then(data => {
                console.log("Données client reçues :", data);

                // Champs client dans le même formulaire
                const form = clientSelect.closest('form');

                const mapping = {
                    'matricule_fiscal': data.matricule_fiscal,
                    'adresse': data.adresse,
                    'telephone': data.telephone,
                    'email': data.email
                };

                Object.keys(mapping).forEach(function(fieldName) {
                    const input = form.querySelector(`input[name="${fieldName}"]`);
                    if (input) input.value = mapping[fieldName] || '';
                });
            })
            .catch(error => console.error("Erreur fetch client :", error));
    });
});