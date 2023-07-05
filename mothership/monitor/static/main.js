const main = () => {
    request(console.log);
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

document.body.onload = main;
