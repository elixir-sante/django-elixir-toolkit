document.addEventListener("DOMContentLoaded", function () {

    const fields = document.querySelectorAll("[data-depends-on]");
    const map = {};

    // Construction des dépendances
    fields.forEach((field) => {
        const controller = field.dataset.dependsOn;

        if (!map[controller]) {
            map[controller] = [];
        }
        // On stocke directement l'ID complet du champ (ex: "id_mon_champ")
        map[controller].push(field.id);
    });

    // Fonction d'affichage
    function applyDependencies(controllerId) {
        const controller = document.getElementById("id_" + controllerId);
        if (!controller || !(controllerId in map)) return;

        const isChecked = controller.checked;

        map[controllerId].forEach((fieldId) => {
            // 1. On génère l'ID Crispy : "div_" + "id_mon_champ" = "div_id_mon_champ"
            // 2. On génère l'ID classique : "field_" + "id_mon_champ" = "field_id_mon_champ"
            const fieldWrapper = document.getElementById("div_" + fieldId) || 
                                 document.getElementById("field_" + fieldId);

            if (fieldWrapper) {
                fieldWrapper.style.display = isChecked ? "block" : "none";
            }
        });
    }

    // Initialisation + écouteurs
    Object.keys(map).forEach((controllerId) => {
        const controller = document.getElementById("id_" + controllerId);
        if (!controller) return;

        controller.addEventListener("change", () => applyDependencies(controllerId));
        applyDependencies(controllerId);
    });
});