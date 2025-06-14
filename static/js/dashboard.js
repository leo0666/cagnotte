function toggleMenu() {
    const menu = document.getElementById('menu');
    menu.classList.toggle('hidden');
}

document.addEventListener("DOMContentLoaded", () => {
    // Gestion des modales
    const modals = [
        ["openModalCagnotteAdd", "closeModalCagnotteAdd", "modalOverlayCagnotteAdd", "modalBackdropCagnotteAdd"],
        ["openModalCagnotteEdit", "closeModalCagnotteEdit", "modalOverlayCagnotteEdit", "modalBackdropCagnotteEdit"],
        ["openModalCagnotteDel", "closeModalCagnotteDel", "modalOverlayCagnotteDel", "modalBackdropCagnotteDel"],
        ["openModalParticipantAdd", "closeModalParticipantAdd", "modalOverlayParticipantAdd", "modalBackdropParticipantAdd"],
        ["openModalParticipantEdit", "closeModalParticipantEdit", "modalOverlayParticipantEdit", "modalBackdropParticipantEdit"],
        ["openModalParticipantDel", "closeModalParticipantDel", "modalOverlayParticipantDel", "modalBackdropParticipantDel"],
        ["openModalAmountEdit", "closeModalAmountEdit", "modalOverlayAmountEdit", "modalBackdropAmountEdit"],
        ["openModalAccessKey", "closeModalAccessKey", "modalOverlayAccessKey", "modalBackdropAccessKey"]
    ];

    const cloneButton = [
        ["moreCagnotteAdd", "cagnotteAdd-container", "cagnotteAdd-entry"],
        ["moreCagnotteEdit", "cagnotteEdit-container", "cagnotteEdit-entry"],
        ["moreCagnotteDel", "cagnotteDel-container", "cagnotteDel-entry"],
        ["moreParticipantAdd", "participantAdd-container", "participantAdd-entry", true],
        ["moreParticipantEdit", "participantEdit-container", "participantEdit-entry", true],
        ["moreParticipantDel", "participantDel-container", "participantDel-entry"],
        ["moreAmountEdit", "amountEdit-container", "amountEdit-entry"],
        ["moreAccessKey", "accessKey-container", "accessKey-entry"]
    ]

    modals.forEach(([openId, closeId, overlayId, backdropId]) => {
        setupModal(openId, closeId, overlayId, backdropId);
    });
    
    // Clonage de formulaires
    cloneButton.forEach(([buttonId, containerId, entryClass, resetAmount = false]) => {
        setupCloneButton(buttonId, containerId, entryClass, resetAmount)
    })

    // Soumission des formulaires
    setupFormSubmit("cagnotteAdd", "cagnotteAdd-container", "cagnotteAdd-entry", "/cagnotte/add", "POST",
        (entry) => {
            const name = entry.querySelector('[name="name"]').value.trim();
            const description = entry.querySelector('[name="description"]').value.trim();

            return {
                name,
                description,
            };
        },
        "modal-errorCagnotteAdd"
    );

    setupFormSubmit("cagnotteEdit", "cagnotteEdit-container", "cagnotteEdit-entry", "/cagnotte/edit", "PUT",
        (entry) => {
            const id_cagnotte_raw = entry.querySelector('[name="id_cagnotte"]').value;
            const name = entry.querySelector('[name="name"]').value.trim();
            const description = entry.querySelector('[name="description"]').value.trim();
            
            const id_cagnotte = id_cagnotte_raw === "" ? null : parseInt(id_cagnotte_raw);

            return {
                id_cagnotte,
                name: name || null,
                description: description || null,
            };
        },
        "modal-errorCagnotteEdit"
    );

    setupFormSubmit("cagnotteDel", "cagnotteDel-container", "cagnotteDel-entry", "/cagnotte/del", "DELETE",
        (entry) => {
            const id_cagnotte_raw = entry.querySelector('[name="id_cagnotte"]').value;
            const id_cagnotte = id_cagnotte_raw === "" ? null : parseInt(id_cagnotte_raw);

            return {
                id_cagnotte,
            };
        },
        "modal-errorCagnotteDel"
    );

    setupFormSubmit("participantAdd", "participantAdd-container", "participantAdd-entry", "/participant/add", "POST",
        (entry) => {
            const first_name = entry.querySelector('[name="first_name"]').value.trim();
            const last_name = entry.querySelector('[name="last_name"]').value.trim();
            const email = entry.querySelector('[name="email"]').value.trim();
            const amount_raw = entry.querySelector('[name="amount"]').value;
            const id_cagnotte_raw = entry.querySelector('[name="id_cagnotte"]').value;

            const amount = amount_raw === "" ? null : parseFloat(amount_raw);
            const id_cagnotte = id_cagnotte_raw === "" ? null : parseInt(id_cagnotte_raw);

            return {
                first_name,
                last_name,
                email,
                amount,
                id_cagnotte,
            };
        },
        "modal-errorParticipantAdd"
    );

    setupFormSubmit("participantEdit", "participantEdit-container", "participantEdit-entry", "/participant/edit", "PUT",
        (entry) => {
            const id_participant = parseInt(entry.querySelector('[name="id_participant"]').value);
            const first_name = entry.querySelector('[name="first_name"]').value.trim();
            const last_name = entry.querySelector('[name="last_name"]').value.trim();
            const email = entry.querySelector('[name="email"]').value.trim();
            const amount_raw = entry.querySelector('[name="amount"]').value;
            const id_cagnotte_raw = entry.querySelector('[name="id_cagnotte"]').value;

            const amount = amount_raw === "" ? null : parseFloat(amount_raw);
            const id_cagnotte = id_cagnotte_raw === "" ? null : parseInt(id_cagnotte_raw);

            if (first_name === "" && last_name === "" && email === "" && amount === null && id_cagnotte === null) {
                const err = document.querySelector("#modal-errorParticipantEdit");
                err.textContent = "Il doit y avoir au moins un champ rempli.";
                err.classList.remove("hidden");
                return;
            }

            return {
                id_participant,
                first_name: first_name || null,
                last_name: last_name || null,
                email: email || null,
                amount,
                id_cagnotte,
            };
        },
        "modal-errorParticipantEdit"
    );

    setupFormSubmit("participantDel", "participantDel-container", "participantDel-entry", "/participant/del", "DELETE",
        (entry) => {
            const id_participant_raw = entry.querySelector('[name="id_participant"]').value;

            const id_participant = id_participant_raw === "" ? null : parseFloat(id_participant_raw);

            return {
                id_participant,
            };
        },
        "modal-errorParticipantDel"
    );

    setupFormSubmit("amountEdit", "amountEdit-container", "amountEdit-entry", "/amount", "PUT",
        (entry) => {
            const id_participant_raw = entry.querySelector('[name="id_participant"]').value;
            const amount_raw = entry.querySelector('[name="amount"]').value;

            const id_participant = id_participant_raw === "" ? null : parseFloat(id_participant_raw);
            const amount = amount_raw === "" ? null : parseFloat(amount_raw);

            return {
                id_participant,
                amount,
            };
        },
        "modal-errorAmountEdit"
    );

    setupFormSubmit("accessKey", "accessKey-container", "accessKey-entry", "/access_dashboard", "POST",
        (entry) => {
            const id_participant_raw = entry.querySelector('[name="id_participant"]').value;

            const id_participant = id_participant_raw === "" ? null : parseFloat(id_participant_raw);

            return {
                id_participant,
            };
        },
        "modal-errorAccessKey"
    );
});

// Fonctions utilitaires

function setupModal(openId, closeId, overlayId, backdropId) {
    const openBtn = document.getElementById(openId);
    const closeBtn = document.getElementById(closeId);
    const overlay = document.getElementById(overlayId);
    const backdrop = document.getElementById(backdropId);

    if (openBtn && closeBtn && overlay && backdrop) {
        openBtn.addEventListener("click", () => {
            overlay.classList.add("show");
            backdrop.style.display = "block";
        });

        const closeModal = () => {
            overlay.classList.remove("show");
            backdrop.style.display = "none";
        };

        closeBtn.addEventListener("click", closeModal);
        backdrop.addEventListener("click", closeModal);
    }
}

function setupCloneButton(buttonId, containerId, entryClass, resetAmount = false) {
    const button = document.getElementById(buttonId);
    const container = document.getElementById(containerId);

    if (button && container) {
        button.addEventListener("click", () => {
            const original = container.querySelector(`.${entryClass}`);
            const clone = original.cloneNode(true);

            clone.querySelectorAll("input, select").forEach(input => { 
                if (resetAmount && input.name === "amount") input.value = "0";
                
                else input.value = ""; });

            container.appendChild(clone);
        });
    }
}

function setupFormSubmit(formId, containerId, entryClass, url, method, extractFn, errorContainerId) {
    const form = document.getElementById(formId);
    const container = document.getElementById(containerId);
    const errorBox = document.getElementById(errorContainerId);

    if (form && container) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            const entries = container.querySelectorAll(`.${entryClass}`);
            const data = [];

            for (const entry of entries) {
                const item = extractFn(entry);
                data.push(item);
            }

            const response = await fetch(url, {
                method,
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data),
            });

            if (response.redirected) {
                window.location.href = response.url;
            } else if (errorBox) {
                errorBox.textContent = await response.text();
                errorBox.classList.remove("hidden");
            }
        });
    }
}
