const RECENTLY = 24 * 60;

export const seconds_to_date = (seconds) => {
    let date = new Date(0);
    date.setUTCSeconds(seconds);
    return date;
}

const minutes_passed = (date) => {
    return Math.floor((new Date() - date) / (60 * 1000));
}

export const is_now = (date) => {
    return minutes_passed(date) < 1;
}

export const is_recent = (date) => {
    return minutes_passed(date) < RECENTLY;
}

export const format_date = (date) => {
    const full = ("0" + date.getDate()).slice(-2) + "-"
        + ("0" + (date.getMonth() + 1)).slice(-2) + "-"
        + date.getFullYear() + " "
        + ("0" + date.getHours()).slice(-2) + ":"
        + ("0" + date.getMinutes()).slice(-2);
    let text = full;

    let m = minutes_passed(date);
    if (m < RECENTLY) {
        let h = Math.floor(m / 60);
        m = m % 60;
        text = (h != 0 ? h + "h " : "")
            + (m != 0 || h == 0 ? m + "m " : "")
            + "ago";
    }

    return `<span class="date" title="${full}">${text}</span>`;
}
