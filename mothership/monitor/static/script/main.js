import { CONTEXT } from "./context.js";
import { render, update, reboot } from "./hosts.js";
import { navigate } from "./navigate.js"

const main = () => {
    register();
    subscribe();
    navigate(window.location.hash.substring(1));
}

window.onload = main;

const RETRY_TIMEOUT = 10 * 1000;

const subscribe = () => {
    render();
    const notify = document.getElementById("notify");

    const loc = window.location;
    const proto = loc.protocol == "https" ? "wss" : "ws";
    const socket = new WebSocket(`${proto}://${loc.hostname}:${loc.port}/websocket`);
    socket.onopen = (e) => {
        CONTEXT.socket = socket;
        console.log("Websocket connected");
        notify.classList.add("hidden");
        document.getElementById("notify-text").innerText = "Reconnecting ...";
    };
    socket.onerror = (e) => {
        console.error("Websocket error:", e);
    };
    socket.onclose = (e) => {
        CONTEXT.socket = null;
        if (e.wasClean) {
            console.log("Websocket disconnected");
        } else {
            console.error("Websocket connection died");
        }
        notify.classList.remove("hidden");
        setTimeout(subscribe, RETRY_TIMEOUT);
    };
    socket.onmessage = (e) => {
        console.log("Websocket received:", e.data);
        CONTEXT.hosts = JSON.parse(e.data);
        render();
    };
}

const register = () => {
    document.getElementById("update-all").onclick = () => { update("all"); };
    document.getElementById("reboot-all").onclick = () => { reboot("all"); };

    document.getElementById("window-container").onclick = () => {
        navigate("");
    }

    document.getElementById("host-window").onclick = (ev) => {
        ev.stopPropagation();
    };

    window.onhashchange = (ev) => {
        navigate(ev.newURL.split("#", 2)[1]);
    };
}
