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
    return ("0" + date.getDate()).slice(-2) + "-"
        + ("0" + (date.getMonth() + 1)).slice(-2) + "-"
        + date.getFullYear() + " "
        + ("0" + date.getHours()).slice(-2) + ":"
        + ("0" + date.getMinutes()).slice(-2);
}

export const format_date_relative = (date) => {
    let m = minutes_passed(date);
    let h = Math.floor(m / 60);
    m = m % 60;
    let d = Math.floor(h / 24);
    h = h % 24;
    return (d != 0 ? d + "d " : "") + (h != 0 ? h + "h " : "")
        + (m != 0 || (d == 0 && h == 0) ? m + "m " : "")
        + "ago";
}

export const compact_date_html = (date) => {
    const full = format_date(date);
    let text = full;

    let m = minutes_passed(date);
    if (is_recent(date)) {
        text = format_date_relative(date);
    }

    return `<span class="date" title="${full}">${text}</span>`;
}
