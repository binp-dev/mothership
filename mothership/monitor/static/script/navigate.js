import { CONTEXT } from "./context.js";

export const navigate = (target) => {
    if (target === CONTEXT.location) {
        return;
    }
    console.log(`Navigate to "${target}"`);
    CONTEXT.location = target;
    window.location.hash = "#" + target;
    if (target === "") {
        CONTEXT.window_container.style.display = "none";
    } else {
        CONTEXT.window_container.style.display = "";
    }
}
