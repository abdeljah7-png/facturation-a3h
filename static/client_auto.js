document.addEventListener("DOMContentLoaded", function () {

    const clientSelect = document.getElementById("id_client");

    if (!clientSelect) return;

    clientSelect.addEventListener("change", function () {

        const clientId = this.value;

        if (!clientId) return;

        fetch("/ventes/client-info/" + clientId + "/")

            .then(response => response.json())

            .then(data => {

                if (document.getElementById("id_mf_client"))
                    document.getElementById("id_mf_client").value = data.mf;

                if (document.getElementById("id_adresse_client"))
                    document.getElementById("id_adresse_client").value = data.adresse;

                if (document.getElementById("id_telephone_client"))
                    document.getElementById("id_telephone_client").value = data.telephone;

                if (document.getElementById("id_email_client"))
                    document.getElementById("id_email_client").value = data.email;

            });

    });

});