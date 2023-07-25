import { seconds_to_date, is_now, is_recent, format_date } from "./utils.js";
import { CONTEXT } from "./context.js";

export const render = (hosts) => {
    const root = document.getElementById("hosts");
    for (const mac in hosts) {
        const host = hosts[mac]
        let elem = document.getElementById(mac);
        if (elem === null) {
            elem = document.createElement("div");
            elem.id = mac;
            elem.classList.add("host");
            root.appendChild(elem);
        }
        update_host_element(elem, mac, host);
    }
}

const update_host_element = (elem, mac, host) => {
    let html = `<div class="mac">${mac.toUpperCase()}</div>`;

    elem.classList.remove("recent", "known", "warning", "error");

    if (host.config !== undefined && host.config !== null) {
        html += `<div>Type: ${host.config.base}</div>`;
        elem.classList.add("known");
    } else {
        html += `<div>Not in config</div>`;
    }

    let rebootable = false;
    if (host.status !== undefined && host.status !== null) {
        const boot = seconds_to_date(host.status.boot);
        html += `<div>${host.status.addr}</div>`
        html += `<div>Booted: ${format_date(boot)}</div>`;
        html += `<button class="reboot">Reboot</button>`;
        rebootable = true;
        const online = seconds_to_date(host.status.online);
        if (!is_now(online)) {
            html += `<div>Last seen: ${format_date(online)}</div>`;
            elem.classList.add("error");
            if (is_recent(online)) {
                elem.classList.add("recent");
            }
        } else {
            if (is_recent(boot)) {
                elem.classList.add("recent");
            }
        }

    } else {
        html += `<div>Offline</div>`;
        elem.classList.add("error");
    }

    elem.innerHTML = html;
    if (rebootable) {
        elem.querySelector(".reboot").onclick = () => { reboot(mac) };
    }
}

export const reboot = (mac) => {
    CONTEXT.socket.send(`{"type": "reboot", "target": "${mac}"}`)
}
