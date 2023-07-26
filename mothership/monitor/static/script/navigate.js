import { CONTEXT } from "./context.js";
import { update_host_window } from "./hosts.js"

export const navigate = (target) => {
    if (target === CONTEXT.location) {
        return;
    }
    console.log(`Navigate to "${target}"`);
    CONTEXT.location = target;
    window.location.hash = "#" + target;

    const wc = document.getElementById("window-container");
    if (target === "") {
        wc.style.display = "none";
    } else {
        wc.style.display = "";
    }

    update_host_window();
}
