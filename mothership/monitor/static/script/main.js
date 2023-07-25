import { CONTEXT } from "./context.js";
import { render, reboot } from "./hosts.js";

const main = () => {
    document.getElementById("reboot-all").onclick = () => { reboot("all") };
    subscribe();
}

const RETRY_TIMEOUT = 10 * 1000;

const subscribe = () => {
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
        render(JSON.parse(e.data));
    };
}

window.onload = main;
