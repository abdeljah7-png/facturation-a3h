document.addEventListener("DOMContentLoaded", function () {

    const fournisseurSelect = document.getElementById("id_fournisseur");

    if (!fournisseurSelect) return;

    fournisseurSelect.addEventListener("change", function () {

        const fournisseurId = this.value;

        if (!fournisseurId) return;

        fetch("/achats/fournisseur-info/" + fournisseurId + "/")

            .then(response => response.json())

            .then(data => {

                if (document.getElementById("id_mf_fournisseur"))
                    document.getElementById("id_mf_fournisseur").value = data.mf;

                if (document.getElementById("id_adresse_fournisseur"))
                    document.getElementById("id_adresse_fournisseur").value = data.adresse;

                if (document.getElementById("id_telephone_fournisseur"))
                    document.getElementById("id_telephone_fournisseur").value = data.telephone;

                if (document.getElementById("id_email_fournisseur"))
                    document.getElementById("id_email_fournisseur").value = data.email;

            });

    });

});