import { seconds_to_date, is_now, is_recent, format_date, format_date_relative, compact_date_html } from "./utils.js";
import { CONTEXT } from "./context.js";
import { navigate } from "./navigate.js"

export const render = () => {
    const root = document.getElementById("hosts");
    const hosts = CONTEXT.hosts;

    for (const mac in hosts) {
        const host = hosts[mac]
        let elem = document.getElementById(mac);
        if (elem === null) {
            elem = document.createElement("div");
            elem.id = mac;
            elem.classList.add("tile");
            elem.onclick = () => { navigate(mac); };
            root.appendChild(elem);
        }
        update_host_tile(elem, mac, host);
    }

    for (const elem of Array.from(root.childNodes)) {
        if (hosts[elem.id] === undefined) {
            root.removeChild(elem);
        }
    }

    update_host_window();
}

const update_host_tile = (elem, mac, host) => {
    let html = `<div class="mac">${mac.toUpperCase()}</div>`;

    elem.classList.remove("recent", "known", "warning", "error");

    if (host.config !== undefined && host.config !== null) {
        html += `<div>Type: ${host.config.base}</div>`;
        elem.classList.add("known");
    } else {
        html += `<div>Not in config</div>`;
    }

    if (host.status !== undefined && host.status !== null) {
        const boot = seconds_to_date(host.status.boot);
        html += `<div>${host.status.addr}</div>`
        html += `<div>Booted: ${compact_date_html(boot)}</div>`;
        const online = seconds_to_date(host.status.online);
        if (!is_now(online)) {
            html += `<div>Last seen: ${compact_date_html(online)}</div>`;
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
}

export const update_host_window = () => {
    const elem = document.getElementById("host-window");
    const mac = CONTEXT.location;
    const host = CONTEXT.hosts[mac];

    let html = `<h1 class="mac">${mac.toUpperCase()}</h1>`;

    let rebootable = false;
    if (host !== undefined) {
        if (host.config !== undefined && host.config !== null) {
            html += `<div>Type: ${host.config.base}</div>`;
        } else {
            html += `<div><span class="badge err">Not in config</span></div>`;
        }

        if (host.status !== undefined && host.status !== null) {
            const boot = seconds_to_date(host.status.boot);
            html += `<div>Address: ${host.status.addr}</div>`
            html += `<div>Booted: ${format_date_relative(boot)} (${format_date(boot)}) <button class="reboot">Reboot</button></div>`;
            rebootable = true;
            const online = seconds_to_date(host.status.online);
            if (is_now(online)) {
                html += `<div>Last seen: <span class="badge ok">Now</span></div>`;
            } else {
                html += `<div>Last seen: <span class="badge err">${format_date_relative(online)}</span> (${format_date(online)})</div>`;
            }

        } else {
            html += `<div>Status: <span class="badge err">Offline</span></div>`;
        }
    } else {
        html += `<h2><span class="badge err">Host '${mac}' not found</span></h2>`
    }

    elem.innerHTML = html;

    if (rebootable) {
        elem.querySelector(".reboot").onclick = () => { reboot(mac) };
    }
}

export const reboot = (mac) => {
    CONTEXT.socket.send(`{"type": "reboot", "target": "${mac}"}`)
}
