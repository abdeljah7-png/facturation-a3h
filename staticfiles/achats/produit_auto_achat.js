document.addEventListener("change", function(e) {

    if (!e.target.name.includes("produit")) return;

    const produitId = e.target.value;
    const row = e.target.closest("tr");

    if (!produitId) return;

    fetch("/achats/produit-info/" + produitId + "/")
        .then(response => response.json())
        .then(data => {

            const prixInput = row.querySelector('input[name$="prix_ht"]');
            const tvaInput = row.querySelector('input[name$="taux_tva"]');

            if (prixInput) prixInput.value = data.p_achat;
            if (tvaInput) tvaInput.value = data.taux_tva;

        });

});