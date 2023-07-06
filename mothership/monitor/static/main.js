const main = () => {
    request(render);
}

const request = (callback) => {
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
    html = `<div class="mac">MAC: ${mac}</div>`;
    if (host.device !== undefined && host.device !== null) {
        html += `<div>Name: ${host.device.name}</div>`
        html += `<div>Base: ${host.device.base}</div>`;
    }
    if (host.info !== undefined && host.info !== null) {
        html += `<div>IP: ${host.info.addr}</div>`
        html += `<div>Boot: ${seconds_to_date(host.info.boot)}</div>`;
        html += `<div>Online: ${seconds_to_date(host.info.online)}</div>`;
    }
    elem.innerHTML = html;
}

const seconds_to_date = (seconds) => {
    let date = new Date(0);
    date.setUTCSeconds(seconds);
    return date;
}

window.onload = main;
