document.addEventListener("DOMContentLoaded", function () {

    const fields = document.querySelectorAll("[data-depends-on]");

    const map = {};

    // Construction des dépendances
    fields.forEach((field) => {
        const controller = field.dataset.dependsOn;

        if (!map[controller]) {
            map[controller] = [];
        }
        map[controller].push(field.id);
    });

    // Fonction d'affichage
    function applyDependencies(controllerId) {
        const controller = document.getElementById("id_" + controllerId);
        if (!controller || !(controllerId in map)) return;

        const isChecked = controller.checked;

        map[controllerId].forEach((fieldId) => {
            const fieldWrapper = document.getElementById("field_" + fieldId);
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
