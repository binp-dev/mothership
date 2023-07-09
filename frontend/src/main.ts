import { io } from "socket.io-client";

const main = () => {
    request(render);
}

const request = (callback: (data: any) => void) => {
    const xhr = new XMLHttpRequest();
    xhr.open("GET", "/hosts", true);
    xhr.onload = (e) => {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                callback(JSON.parse(xhr.responseText));
            } else {
                console.error(xhr.statusText);
            }
        }
    };
    xhr.onerror = (e) => {
        console.error(xhr.statusText);
    };
    xhr.send(null);
}

type Host = {
    mac: string,
    config?: {
        base: string,
    } | null,
    status?: {
        addr: string,
        boot: number,
        online: number,
    } | null,
};

const render = (hosts: Host[]) => {
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

const update_host_element = (elem: Element, mac: string, host: Host) => {
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

const seconds_to_date = (seconds: number): Date => {
    let date = new Date(0);
    date.setUTCSeconds(seconds);
    return date;
}

const is_now = (date: Date): boolean => {
    return (new Date().getTime() - date.getTime()) < (60 * 1000);
}

const format_date = (date: Date): string => {
    const recently = 24 * 60;
    let m = Math.floor((new Date().getTime() - date.getTime()) / (60 * 1000));
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
