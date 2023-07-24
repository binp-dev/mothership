const main = () => {
    subscribe();
}

let socket = undefined;

const subscribe = () => {
    const timeout = 4 * 1000;

    const notify = document.getElementById("notify");
    notify.innerText = "Connecting ...";

    const loc = window.location;
    const proto = loc.protocol == "https" ? "wss" : "ws";
    socket = new WebSocket(`${proto}://${loc.hostname}:${loc.port}/websocket`);
    socket.onopen = (e) => {
        console.log("Websocket connected");
        notify.classList.add("hidden");
        notify.innerText = "Reconnecting ...";
    };
    socket.onerror = (e) => {
        console.error("Websocket error:", e);
    };
    socket.onclose = (e) => {
        if (e.wasClean) {
            console.log("Websocket disconnected");
        } else {
            console.error("Websocket connection died");
        }
        notify.classList.remove("hidden");
        setTimeout(subscribe, timeout);
    };
    socket.onmessage = (e) => {
        console.log("Websocket received:", e.data);
        render(JSON.parse(e.data));
    };
}

const reboot = (mac) => {
    socket.send(`{"type": "reboot", "target": "${mac}"}`)
}

const render = (hosts) => {
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

    elem.classList.remove("known", "warning", "error");

    if (host.config !== undefined && host.config !== null) {
        html += `<div>Type: ${host.config.base}</div>`;
        elem.classList.add("known");
    } else {
        html += `<div>Not in config</div>`;
    }

    let rebootable = false;
    if (host.status !== undefined && host.status !== null) {
        html += `<div>${host.status.addr}</div>`
        html += `<div>Booted: ${format_date(seconds_to_date(host.status.boot))}</div>`;
        html += `<button class="reboot">Reboot</button>`;
        rebootable = true;
        const online = seconds_to_date(host.status.online);
        if (!is_now(online)) {
            html += `<div>Last seen: ${format_date(online)}</div>`;
            elem.classList.add("error");
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

const seconds_to_date = (seconds) => {
    let date = new Date(0);
    date.setUTCSeconds(seconds);
    return date;
}

const is_now = (date) => {
    return new Date() - date < (60 * 1000);
}

const format_date = (date) => {
    const full = ("0" + date.getDate()).slice(-2) + "-"
        + ("0" + (date.getMonth() + 1)).slice(-2) + "-"
        + date.getFullYear() + " "
        + ("0" + date.getHours()).slice(-2) + ":"
        + ("0" + date.getMinutes()).slice(-2);
    let text = full;

    const recently = 24 * 60;
    let m = Math.floor((new Date() - date) / (60 * 1000));
    if (m < recently) {
        let h = Math.floor(m / 60);
        m = m % 60;
        text = (h != 0 ? h + "h " : "")
            + (m != 0 || h == 0 ? m + "m " : "")
            + "ago";
    }

    return `<span class="date" title="${full}">${text}</span>`;
}

window.onload = main;
