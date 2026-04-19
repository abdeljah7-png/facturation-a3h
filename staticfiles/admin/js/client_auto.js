document.addEventListener("DOMContentLoaded", function () {

    const clientSelect = document.getElementById("id_client");

    if (!clientSelect) return;

    clientSelect.addEventListener("change", function () {

        const clientId = this.value;
        if (!clientId) return;

        fetch("/client-info/" + clientId + "/")
            .then(response => response.json())
            .then(data => {
                document.getElementById("id_mf_client").value = data.mf || "";
                document.getElementById("id_adresse_client").value = data.adresse || "";
                document.getElementById("id_telephone_client").value = data.telephone || "";
                document.getElementById("id_email_client").value = data.email || "";
            })
            .catch(error => console.error("Erreur:", error));

    });

});