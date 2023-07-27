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

    for (const [i, elem] of Array.from(root.childNodes).sort((a, b) => (a.id > b.id) - (a.id < b.id)).entries()) {
        elem.style.order = i;
    }

    update_host_window();
}

const update_host_tile = (elem, mac, host) => {
    let html = `<div class="mono">${mac.toUpperCase()}</div>`;

    elem.classList.remove("recent", "known", "warning", "error");

    if (host.config !== null) {
        html += `<div>Class: ${host_class(host)}</div>`;
        html += `<div>Base: ${host.config.base}</div>`;
        elem.classList.add("known");
    } else {
        html += `<div>Not in config</div>`;
    }

    if (host.status !== null) {
        html += `<div>${host.status.addr}</div>`
        const booted = seconds_to_date(host.status.boot);
        html += `<div>Booted: ${compact_date_html(booted)}</div>`;
        const last_seen = seconds_to_date(host.status.online);
        if (!is_now(last_seen)) {
            html += `<div>Last seen: ${compact_date_html(last_seen)}</div>`;
            elem.classList.add("error");
            if (is_recent(last_seen)) {
                elem.classList.add("recent");
            }
        } else {
            if (is_recent(booted)) {
                elem.classList.add("recent");
            }
        }
        if (host.status.error !== undefined) {
            elem.classList.add("warning");
        }
    } else {
        html += `<div>Offline</div>`;
        elem.classList.add("error");
    }

    if (host.config !== null && host.status !== null) {
        if (host.config.nand !== undefined) {
            if (host.status.nand === undefined
                || (host.config.nand.bootloader !== undefined && host.config.nand.bootloader !== host.status.nand.bootloader)
                || (host.config.nand.fw_env_hash !== undefined && host.config.nand.fw_env_hash !== host.status.nand.fw_env_hash)
            ) {
                elem.classList.add("warning");
            }
        }
    }

    elem.innerHTML = html;
}

export const update_host_window = () => {
    const elem = document.getElementById("host-window");
    const mac = CONTEXT.location;
    const host = CONTEXT.hosts[mac];

    let html = `<h1 class="mono">${mac.toUpperCase()}</h1>`;

    let online = false;
    if (host !== undefined) {
        if (host.config !== null) {
            html += `<div>Class: ${host_class(host)}</div>`;
            html += `<div>Base: ${host.config.base}</div>`;
        } else {
            html += `<div><span class="badge err">Not in config</span></div>`;
        }

        if (host.status !== null) {
            const last_seen = seconds_to_date(host.status.online);
            online = is_now(last_seen);

            html += `<div>Address: ${host.status.addr}</div>`

            const booted = seconds_to_date(host.status.boot);
            let boot_html = `Booted: ${format_date_relative(booted)} (${format_date(booted)})`;
            if (online) {
                boot_html += `<button class="reboot danger">Reboot</button>`;
            }
            html += `<div>${boot_html}</div>`;

            if (online) {
                html += `<div>Status: <span class="badge ok">Online</span><button class="update">Update</button></div>`;
            } else {
                html += `<div>Status: <span class="badge err">Offline</span></div>`;
                html += `<div>Last seen: ${format_date_relative(last_seen)} (${format_date(last_seen)})</div>`;
            }

            if (host.status.error !== undefined) {
                html += `<div>Error:</div><div class="code err">${host.status.error}</div>`;
            }
        } else {
            html += `<div>Status: <span class="badge err">Offline</span></div>`;
        }

        if (host.config !== null && host.status !== null) {
            if (host.config.nand !== undefined) {
                html += nand_block(host);
            }
        }
    } else {
        html += `<h2><span class="badge err">Host '${mac}' not found</span></h2>`
    }

    elem.innerHTML = html;

    if (online) {
        elem.querySelector(".update").onclick = () => { update(mac) };
        elem.querySelector(".reboot").onclick = () => { reboot(mac) };
    }
}

export const update = (mac) => {
    CONTEXT.socket.send(`{"type": "update", "target": "${mac}"}`)
}

export const reboot = (mac) => {
    CONTEXT.socket.send(`{"type": "reboot", "target": "${mac}"}`)
}

const host_class = (host) => {
    let types = [];
    if (host.config.nand !== undefined) {
        types.push("nand");
    }
    if (types.length == 0) {
        return "default"
    } else {
        return types.join("-");
    }
}

const nand_block = (host) => {
    let html = `<div><b>NAND:</b></div>`;
    if (host.status.nand !== undefined) {
        let bootc = "";
        if (host.config.nand.bootloader === host.status.nand.bootloader) {
            bootc = "ok"
        } else if (host.config.nand.bootloader !== undefined) {
            bootc = "err"
        }
        html += `<div>Bootloader: <span class="badge ${bootc}">${host.status.nand.bootloader}</span></div>`;

        let envc = "";
        if (host.config.nand.fw_env_hash === host.status.nand.fw_env_hash) {
            envc = "ok"
        } else if (host.config.nand.fw_env_hash !== undefined) {
            envc = "err"
        }
        html += `<div>FW env hash: <span class="badge ${envc}">${host.status.nand.fw_env_hash}</span></div>`;
    } else {
        html += `<span class="badge err">Cannot read</span>`;
    }
    return html;
}
