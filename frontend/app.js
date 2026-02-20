/* ─── Atmos Weather — Shared Utilities ─── */
const API = '/api';
const $ = (id) => document.getElementById(id);
let metric = true;

/* ── WMO Weather Code → description + Material Symbols icon + color class ── */
const wmoMap = {
    0: { desc: 'Clear', icon: 'clear_day', nightIcon: 'bedtime', color: 'text-yellow-300' },
    1: { desc: 'Mainly Clear', icon: 'clear_day', nightIcon: 'clear_night', color: 'text-yellow-200' },
    2: { desc: 'Partly Cloudy', icon: 'partly_cloudy_day', nightIcon: 'partly_cloudy_night', color: 'text-slate-300' },
    3: { desc: 'Cloudy', icon: 'cloud', nightIcon: 'cloud', color: 'text-slate-300' },
    45: { desc: 'Fog', icon: 'foggy', nightIcon: 'foggy', color: 'text-slate-400' },
    48: { desc: 'Depositing Fog', icon: 'foggy', nightIcon: 'foggy', color: 'text-slate-400' },
    51: { desc: 'Light Drizzle', icon: 'rainy_light', nightIcon: 'rainy_light', color: 'text-blue-300' },
    53: { desc: 'Drizzle', icon: 'rainy_light', nightIcon: 'rainy_light', color: 'text-blue-300' },
    55: { desc: 'Dense Drizzle', icon: 'rainy', nightIcon: 'rainy', color: 'text-blue-400' },
    61: { desc: 'Light Rain', icon: 'rainy', nightIcon: 'rainy', color: 'text-blue-400' },
    63: { desc: 'Rain', icon: 'rainy', nightIcon: 'rainy', color: 'text-blue-400' },
    65: { desc: 'Heavy Rain', icon: 'rainy_heavy', nightIcon: 'rainy_heavy', color: 'text-blue-500' },
    71: { desc: 'Light Snow', icon: 'weather_snowy', nightIcon: 'weather_snowy', color: 'text-sky-200' },
    73: { desc: 'Snow', icon: 'weather_snowy', nightIcon: 'weather_snowy', color: 'text-sky-300' },
    75: { desc: 'Heavy Snow', icon: 'ac_unit', nightIcon: 'ac_unit', color: 'text-sky-400' },
    80: { desc: 'Rain Showers', icon: 'rainy', nightIcon: 'rainy', color: 'text-blue-300' },
    81: { desc: 'Moderate Showers', icon: 'rainy', nightIcon: 'rainy', color: 'text-blue-400' },
    82: { desc: 'Heavy Showers', icon: 'rainy_heavy', nightIcon: 'rainy_heavy', color: 'text-blue-500' },
    95: { desc: 'Thunderstorm', icon: 'thunderstorm', nightIcon: 'thunderstorm', color: 'text-yellow-300' },
    96: { desc: 'Thunderstorm + Hail', icon: 'thunderstorm', nightIcon: 'thunderstorm', color: 'text-yellow-400' },
    99: { desc: 'Severe Thunderstorm', icon: 'thunderstorm', nightIcon: 'thunderstorm', color: 'text-red-400' },
};

function getWeatherInfo(code, isNight = false) {
    const entry = wmoMap[code] || { desc: 'Unknown', icon: 'cloud', nightIcon: 'cloud', color: 'text-slate-300' };
    return {
        desc: entry.desc,
        icon: isNight ? entry.nightIcon : entry.icon,
        color: entry.color,
    };
}

function temp(v) {
    return metric ? `${Math.round(v)}°C` : `${Math.round((v * 9) / 5 + 32)}°F`;
}

function tempVal(v) {
    return metric ? Math.round(v) : Math.round((v * 9) / 5 + 32);
}

function getHour(time) {
    return Number(String(time || new Date().toISOString()).slice(11, 13));
}

function isNightTime(hour) {
    return hour < 6 || hour >= 18;
}

function themeFrom(code, hour) {
    const night = isNightTime(hour);
    if ([95, 96, 99].includes(code)) return 'thunderstorm';
    if ([61, 63, 65, 80, 81, 82].includes(code)) return 'rain';
    if ([51, 53, 55].includes(code)) return 'drizzle';
    if ([71, 73, 75].includes(code)) return 'snow';
    if ([45, 48].includes(code)) return 'fog';
    if ([1, 2, 3].includes(code)) return night ? 'cloudy-night' : 'cloudy';
    if (!night && (hour === 6 || hour === 17)) return 'sunset';
    return night ? 'clear-night' : 'sunny-day';
}

function setTheme(code, time) {
    const h = getHour(time);
    document.body.setAttribute('data-theme', themeFrom(code, h));
}

async function jfetch(url, opts) {
    const r = await fetch(url, opts);
    const t = await r.text();
    let d;
    try { d = JSON.parse(t); } catch { d = t; }
    if (!r.ok) throw new Error(d.detail || t || 'Request failed');
    return d;
}

function showError(id, msg = '') {
    const el = $(id);
    if (el) {
        el.textContent = msg;
        if (msg) {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        } else {
            el.style.opacity = '0';
            el.style.transform = 'translateY(-4px)';
        }
    }
}

function bindUnitToggle(btnId, reloadFn) {
    const b = $(btnId);
    if (!b) return;
    b.onclick = () => {
        metric = !metric;
        b.textContent = metric ? '°C / °F' : '°F / °C';
        if (reloadFn) reloadFn();
    };
}

/* ── Icon HTML helper ── */
function weatherIconHtml(code, isNight = false, sizeClass = 'text-3xl') {
    const info = getWeatherInfo(code, isNight);
    return `<span class="material-symbols-outlined ${sizeClass} ${info.color} drop-shadow-[0_0_8px_currentColor] transition-all duration-500">${info.icon}</span>`;
}
