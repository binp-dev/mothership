const main = () => {
    subscribe(render);
}

const subscribe = (callback) => {
    const loc = window.location;
    const proto = loc.protocol == "https" ? "wss" : "ws";
    let socket = new WebSocket(`${proto}://${loc.hostname}:${loc.port}/websocket`);
    socket.onopen = (event) => {
        console.log("Websocket connected");
    };
    socket.onmessage = (event) => {
        console.log(`Websocket received: ${event.data}`);
        callback(JSON.parse(event.data));
    };
    socket.onclose = (event) => {
        if (event.wasClean) {
            console.log("Websocket disconnected");
        } else {
            console.error("Websocket connection died");
        }
    };
    socket.onerror = (error) => {
        console.error(`Websocket error: ${error}`);
    };
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

    if (host.status !== undefined && host.status !== null) {
        html += `<div>${host.status.addr}</div>`
        html += `<div>Booted: ${format_date(seconds_to_date(host.status.boot))}</div>`;
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
    const recently = 24 * 60;
    let m = Math.floor((new Date() - date) / (60 * 1000));
    if (m < recently) {
        let h = Math.floor(m / 60);
        m = m % 60;
        return (h != 0 ? h + "h " : "")
            + (m != 0 || h == 0 ? m + "m " : "")
            + "ago";
    } else {
        return ("0" + date.getDate()).slice(-2) + "-"
            + ("0" + (date.getMonth() + 1)).slice(-2) + "-"
            + date.getFullYear() + " "
            + ("0" + date.getHours()).slice(-2) + ":"
            + ("0" + date.getMinutes()).slice(-2);
    }
}

window.onload = main;
