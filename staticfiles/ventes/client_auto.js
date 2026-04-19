document.addEventListener("DOMContentLoaded", function () {

    const clientSelect = document.getElementById("id_client");

    if (!clientSelect) return;

    clientSelect.addEventListener("change", function () {

        const clientId = this.value;
        if (!clientId) return;

        fetch(`/clients/client-info/${clientId}/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error("Erreur HTTP: " + response.status);
                }
                return response.json();
            })
            .then(data => {

                console.log("Client data:", data);

                const setValue = (id, value) => {
                    const el = document.getElementById(id);
                    if (el) el.value = value || "";
                };

                // Infos client
                setValue("id_nom_client", data.nom);
                setValue("id_adresse_client", data.adresse);
                setValue("id_telephone_client", data.telephone);
                setValue("id_email_client", data.email);

                // 🔥 matricule fiscale (IMPORTANT)
                setValue("id_mf_client", data.matricule_fiscal);

            })
            .catch(error => {
                console.error("Erreur client fetch:", error);
            });

    });

});