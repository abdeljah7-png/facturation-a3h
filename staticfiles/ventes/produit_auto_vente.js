document.addEventListener("change", function(e) {

    if (!e.target.name.includes("produit")) return;

    const produitId = e.target.value;
    const row = e.target.closest("tr");

    if (!produitId) return;

    fetch("/ventes/produit-info/" + produitId + "/")
        .then(response => response.json())
        .then(data => {

            const prixInput = row.querySelector('input[name$="prix_ht"]');
            const tvaInput = row.querySelector('input[name$="taux_tva"]');

            if (prixInput) prixInput.value = data.prix_ht;
            if (tvaInput) tvaInput.value = data.taux_tva;

        });

});