document.addEventListener("DOMContentLoaded", function () {

    const clientSelect = document.getElementById("id_client");

    if (!clientSelect) return;

    clientSelect.addEventListener("change", function () {

        const clientId = this.value;
        if (!clientId) return;

        fetch("/client-info/" + clientId + "/")
            .then(r => r.json())
            .then(data => {

                const mf = document.getElementById("id_mf_client");
                if (mf) mf.value = data.mf;

                const adr = document.getElementById("id_adresse_client");
                if (adr) adr.value = data.adresse;

                const tel = document.getElementById("id_telephone_client");
                if (tel) tel.value = data.telephone;

                const email = document.getElementById("id_email_client");
                if (email) email.value = data.email;

            })
            .catch(err => console.error("Erreur client info:", err));

    });

});