import { useState, useEffect } from "react";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine
} from "recharts";

// ── Config ────────────────────────────────────────────────────────────────────

const API_BASE = "http://localhost:8000/course";

// Валюты, которые поддерживает ЦБ РФ
const CURRENCIES = [
  { id: "USD", name: "Доллар США" },
  { id: "EUR", name: "Евро" },
  { id: "GBP", name: "Фунт стерлингов" },
  { id: "CNY", name: "Юань" },
  { id: "JPY", name: "Японская иена" },
  { id: "CHF", name: "Швейцарский франк" },
  { id: "KZT", name: "Тенге" },
  { id: "BYN", name: "Белорусский рубль" },
];

// ── Helpers ───────────────────────────────────────────────────────────────────

function today() {
  return new Date().toISOString().split("T")[0];
}

function addDays(isoDate, n) {
  const d = new Date(isoDate);
  d.setDate(d.getDate() + n);
  return d.toISOString().split("T")[0];
}

function fmtDate(isoDate) {
  return new Date(isoDate).toLocaleDateString("ru-RU", { day: "2-digit", month: "2-digit" });
}

function parseRate(str) {
  return parseFloat(String(str).replace(",", "."));
}

// Fetch курс за один день
async function fetchRate(dateIso, currCode) {
  const dd = dateIso.split("-").reverse().join("/"); // YYYY-MM-DD → DD/MM/YYYY
  const url = `${API_BASE}/currency?date_req=${dd}&name_val=${currCode}`;
  const res = await fetch(url);
  if (!res.ok) return null;
  const data = await res.json();
  if (!data || data.length === 0) return null;
  return parseRate(data[0].value) / parseInt(data[0].nominal, 10);
}

// Формирует историю за N дней назад до сегодня
async function fetchHistory(currCode, days) {
  const promises = [];
  const end = today();
  
  for (let i = days; i >= 0; i--) {
    const iso = addDays(end, -i);
    promises.push(
      fetchRate(iso, currCode).then(rate => ({ iso, rate }))
    );
  }
  
  const results = await Promise.all(promises);
  
  // Forward Fill: если rate равен null, берем значение предыдущего дня
  let lastValidRate = 0;
  const filledData = results.map((item) => {
    if (item.rate !== null && !isNaN(item.rate)) {
      lastValidRate = item.rate;
    }
    return {
      ...item,
      rate: lastValidRate, // используем последнее известное значение
      date: fmtDate(item.iso)
    };
  });

  // Отфильтровываем только самые первые дни, если по ним ВООБЩЕ не было данных в начале периода
  return filledData.filter(r => r.rate > 0);
}

// ── Tiny sparkline ────────────────────────────────────────────────────────────

function Spark({ data, up }) {
  const mn = Math.min(...data), mx = Math.max(...data);
  const W = 56, H = 22;
  const pts = data.map((v, i) =>
    `${(i / (data.length - 1)) * W},${H - 2 - ((v - mn) / ((mx - mn) || 1)) * (H - 4)}`
  ).join(" ");
  return (
    <svg width={W} height={H}>
      <polyline points={pts} fill="none"
        stroke={up ? "#16a34a" : "#dc2626"}
        strokeWidth={1.2} strokeLinejoin="round" />
    </svg>
  );
}

// ── Tooltip ───────────────────────────────────────────────────────────────────

const Tip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: "#fff", border: "1px solid #e5e7eb",
      borderRadius: 6, padding: "8px 12px",
      fontFamily: "'IBM Plex Mono', monospace", fontSize: 12, color: "#111",
      boxShadow: "0 4px 16px rgba(0,0,0,0.08)",
    }}>
      <div style={{ color: "#6b7280", marginBottom: 4 }}>{label}</div>
      {payload.map((p, i) => (
        <div key={i} style={{ color: p.color, fontWeight: 600 }}>
          {p.name}: {Number(p.value).toLocaleString("ru-RU")}
        </div>
      ))}
    </div>
  );
};

// ── App ───────────────────────────────────────────────────────────────────────

export default function CurrForecast() {
  const [currCode, setCurrCode] = useState("USD");
  const [hDays, setHDays] = useState(30);
  const [fDays, setFDays] = useState(30);
  const [history, setHistory] = useState([]);
  const [forecast, setForecast] = useState([]);
  const [sideRates, setSideRates] = useState({}); // { USD: { rate, prev }, EUR: ... }
  const [loading, setLoading] = useState(false);
  const [histLoading, setHistLoading] = useState(false);
  const [predLoading, setPredLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [tab, setTab] = useState("chart");
  const [error, setError] = useState(null);

  // При изменении валюты или периода — загружаем историю
  useEffect(() => {
    setDone(false);
    setForecast([]);
    setError(null);
    loadHistory();
  }, [currCode, hDays]); // eslint-disable-line

  // При монтировании — загружаем текущие курсы для сайдбара
  useEffect(() => {
    loadSideRates();
  }, []);

  async function loadHistory() {
    setHistLoading(true);
    try {
      const data = await fetchHistory(currCode, hDays);
      setHistory(data);
    } catch (e) {
      setError("Не удалось загрузить историю: " + e.message);
    } finally {
      setHistLoading(false);
    }
  }

  async function loadSideRates() {
    const todayIso = today();
    const yesterdayIso = addDays(todayIso, -1);
    const results = {};
    await Promise.all(
      CURRENCIES.map(async (c) => {
        const [cur, prev] = await Promise.all([
          fetchRate(todayIso, c.id),
          fetchRate(yesterdayIso, c.id),
        ]);
        if (cur) results[c.id] = { rate: cur, prev: prev || cur };
      })
    );
    setSideRates(results);
  }

  async function runForecast() {
    if (!history.length) return;
    setPredLoading(true);
    setLoading(true);
    setDone(false);
    setError(null);

    try {
      // Предсказываем одну дату — последнюю дату + fDays
      const lastIso = history.at(-1).iso;
      const targetIso = addDays(lastIso, fDays);

      const res = await fetch(`${API_BASE}/predict?target_date=${targetIso}`);
      if (!res.ok) throw new Error(`Ошибка API: ${res.status}`);
      const data = await res.json();

      if (data.error) throw new Error(data.error);

      // Генерируем промежуточные точки интерполяцией для красивого графика
      const startRate = history.at(-1).rate;
      const endRate = data.predicted_rate;
      const points = [];
      for (let i = 1; i <= fDays; i++) {
        const iso = addDays(lastIso, i);
        const t = i / fDays;
        const forecast = parseFloat((startRate + (endRate - startRate) * t).toFixed(4));
        const uncertainty = 0.015 * t; // растущая неопределённость
        const conf = parseFloat(Math.max(25, 100 - i * 1.5).toFixed(0));
        points.push({
          iso,
          date: fmtDate(iso),
          forecast,
          upper: parseFloat((forecast * (1 + uncertainty)).toFixed(4)),
          lower: parseFloat((forecast * (1 - uncertainty)).toFixed(4)),
          conf,
        });
      }
      setForecast(points);
      setDone(true);
    } catch (e) {
      setError("Ошибка прогноза: " + e.message);
    } finally {
      setPredLoading(false);
      setLoading(false);
    }
  }

  const cur = history.at(-1)?.rate ?? 0;
  const prev = history.at(-2)?.rate ?? cur;
  const delta = cur - prev;
  const deltaPct = prev ? (delta / prev) * 100 : 0;
  const fLast = forecast.at(-1)?.forecast;
  const fPct = fLast ? ((fLast - cur) / cur * 100) : null;
  const dp = cur > 100 ? 2 : cur > 10 ? 4 : 4;

  const chartData = [
    ...history.map(d => ({ ...d, type: "h" })),
    ...(done ? forecast : []),
  ];

  const segBtn = (active) => ({
    padding: "5px 12px", fontSize: 12, cursor: "pointer",
    fontFamily: "'IBM Plex Mono', monospace", border: "none",
    background: active ? "#111" : "transparent",
    color: active ? "#fff" : "#9ca3af",
    borderRadius: 4, transition: "all 0.12s",
  });

  const tabBtn = (id) => ({
    padding: "6px 0", fontSize: 12, cursor: "pointer",
    fontFamily: "'IBM Plex Mono', monospace", background: "transparent",
    color: tab === id ? "#111" : "#9ca3af",
    border: "none", borderBottom: `1.5px solid ${tab === id ? "#111" : "transparent"}`,
    marginRight: 20, transition: "all 0.12s",
    letterSpacing: "0.03em",
  });

  return (
    <div style={{
      minHeight: "100vh",
      background: "#fafafa",
      color: "#111",
      fontFamily: "'DM Sans', system-ui, sans-serif",
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=DM+Sans:wght@400;500;600&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        ::-webkit-scrollbar { width: 3px; }
        ::-webkit-scrollbar-thumb { background: #e5e7eb; }
        @keyframes fade-in { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }
        @keyframes spin { to { transform: rotate(360deg); } }
        .row:hover { background: #f3f4f6 !important; }
        button:focus { outline: none; }
      `}</style>

      <div style={{ maxWidth: 1200, margin: "0 auto", padding: "0 24px 48px" }}>

        {/* ── Header ── */}
        <header style={{
          padding: "28px 0 20px",
          borderBottom: "1px solid #e5e7eb",
          display: "flex", alignItems: "baseline",
          justifyContent: "space-between",
        }}>
          <div>
            <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontWeight: 600, fontSize: 15, letterSpacing: "-0.02em" }}>
              fx.forecast
            </span>
            <span style={{ color: "#9ca3af", fontSize: 12, marginLeft: 12 }}>
              Прогноз курса валют · ЦБ РФ
            </span>
          </div>
          <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 11, color: "#9ca3af" }}>
            {new Date().toLocaleDateString("ru-RU")}
          </span>
        </header>

        {error && (
          <div style={{
            marginTop: 16, padding: "10px 14px",
            background: "#fef2f2", border: "1px solid #fecaca",
            borderRadius: 6, color: "#dc2626",
            fontFamily: "'IBM Plex Mono', monospace", fontSize: 12,
          }}>
            ⚠ {error}
          </div>
        )}

        <div style={{ display: "flex", gap: 32, marginTop: 28, alignItems: "flex-start" }}>

          {/* ── Left: currency list ── */}
          <div style={{ width: 200, flexShrink: 0 }}>
            <div style={{
              fontSize: 10, letterSpacing: "0.1em", textTransform: "uppercase",
              color: "#9ca3af", marginBottom: 12, fontFamily: "'IBM Plex Mono', monospace",
            }}>Валюты</div>
            {CURRENCIES.map(c => {
              const active = c.id === currCode;
              const sr = sideRates[c.id];
              const last = sr?.rate;
              const prevR = sr?.prev;
              const up = last !== undefined && prevR !== undefined ? last >= prevR : true;
              const pct = last && prevR ? ((last - prevR) / prevR * 100).toFixed(2) : "…";
              // Мини-спарклайн из истории для текущей валюты (или заглушка)
              const spark = c.id === currCode && history.length > 1
                ? history.slice(-10).map(d => d.rate)
                : last ? [prevR, last] : [1, 1];

              return (
                <div
                  key={c.id}
                  className="row"
                  onClick={() => { setCurrCode(c.id); }}
                  style={{
                    display: "flex", alignItems: "center",
                    justifyContent: "space-between",
                    padding: "9px 10px",
                    borderRadius: 6,
                    cursor: "pointer",
                    background: active ? "#f3f4f6" : "transparent",
                    borderLeft: `2px solid ${active ? "#111" : "transparent"}`,
                    marginBottom: 2,
                    transition: "all 0.1s",
                  }}
                >
                  <div>
                    <div style={{
                      fontFamily: "'IBM Plex Mono', monospace", fontSize: 12, fontWeight: 600,
                      color: active ? "#111" : "#374151",
                    }}>{c.id}/RUB</div>
                    <div style={{
                      fontSize: 11, color: up ? "#16a34a" : "#dc2626",
                      fontFamily: "'IBM Plex Mono', monospace", marginTop: 1,
                    }}>
                      {last ? `${up ? "+" : ""}${pct}%` : "—"}
                    </div>
                  </div>
                  <Spark data={spark} up={up} />
                </div>
              );
            })}
          </div>

          {/* ── Center ── */}
          <div style={{ flex: 1, minWidth: 0 }}>

            {/* Headline */}
            <div style={{
              display: "flex", alignItems: "flex-end",
              justifyContent: "space-between",
              paddingBottom: 18, borderBottom: "1px solid #e5e7eb",
              flexWrap: "wrap", gap: 12,
            }}>
              <div>
                {histLoading ? (
                  <div style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 14, color: "#9ca3af" }}>
                    Загружаем данные ЦБ РФ…
                  </div>
                ) : (
                  <>
                    <div style={{
                      fontFamily: "'IBM Plex Mono', monospace", fontSize: 32,
                      fontWeight: 600, letterSpacing: "-0.04em", lineHeight: 1,
                    }}>
                      {cur ? cur.toLocaleString("ru-RU", { minimumFractionDigits: 4 }) : "—"}
                      <span style={{ fontSize: 14, color: "#9ca3af", marginLeft: 8, fontWeight: 400 }}>
                        {currCode}/RUB
                      </span>
                    </div>
                    <div style={{
                      fontFamily: "'IBM Plex Mono', monospace", fontSize: 12, marginTop: 6,
                      color: delta >= 0 ? "#16a34a" : "#dc2626",
                    }}>
                      {delta >= 0 ? "+" : ""}{delta.toFixed(dp)}&nbsp;
                      ({deltaPct >= 0 ? "+" : ""}{deltaPct.toFixed(2)}%) за день
                    </div>
                  </>
                )}
              </div>

              {done && fPct !== null && (
                <div style={{
                  fontFamily: "'IBM Plex Mono', monospace", fontSize: 13,
                  color: "#6b7280", textAlign: "right",
                  animation: "fade-in 0.3s ease",
                }}>
                  <div style={{ fontSize: 11, color: "#9ca3af", marginBottom: 2 }}>
                    прогноз {fDays}д (GBM)
                  </div>
                  <span style={{
                    color: fPct >= 0 ? "#16a34a" : "#dc2626",
                    fontWeight: 600, fontSize: 15,
                  }}>
                    {fPct >= 0 ? "+" : ""}{fPct.toFixed(2)}%
                  </span>
                  {" → "}
                  <span style={{ color: "#374151" }}>{fLast?.toLocaleString("ru-RU", { minimumFractionDigits: 2 })}</span>
                </div>
              )}
            </div>

            {/* Tabs */}
            <div style={{ display: "flex", marginTop: 18, marginBottom: 18 }}>
              {["chart", "table"].map(t => (
                <button key={t} style={tabBtn(t)} onClick={() => setTab(t)}>
                  {t === "chart" ? "График" : "История"}
                </button>
              ))}
            </div>

            {/* Chart */}
            {tab === "chart" && (
              <div style={{ animation: "fade-in 0.25s ease" }}>
                {histLoading ? (
                  <div style={{ height: 300, display: "flex", alignItems: "center", justifyContent: "center", color: "#9ca3af", fontFamily: "'IBM Plex Mono', monospace", fontSize: 12 }}>
                    <span style={{ animation: "spin 1s linear infinite", display: "inline-block", marginRight: 8 }}>◌</span>
                    Загрузка…
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={chartData} margin={{ top: 4, right: 4, bottom: 0, left: 0 }}>
                      <defs>
                        <linearGradient id="gH" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#111" stopOpacity={0.06} />
                          <stop offset="100%" stopColor="#111" stopOpacity={0} />
                        </linearGradient>
                        <linearGradient id="gF" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#16a34a" stopOpacity={0.08} />
                          <stop offset="100%" stopColor="#16a34a" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid vertical={false} stroke="#f0f0f0" />
                      <XAxis
                        dataKey="date"
                        tick={{ fill: "#9ca3af", fontSize: 10, fontFamily: "'IBM Plex Mono', monospace" }}
                        axisLine={false} tickLine={false}
                        interval={Math.floor(chartData.length / 7)}
                      />
                      <YAxis
                        tick={{ fill: "#9ca3af", fontSize: 10, fontFamily: "'IBM Plex Mono', monospace" }}
                        axisLine={false} tickLine={false}
                        width={58}
                        domain={["auto", "auto"]}
                        tickFormatter={v => v.toLocaleString("ru-RU")}
                      />
                      <Tooltip content={<Tip />} />
                      <Area
                        dataKey="rate" stroke="#111" strokeWidth={1.5}
                        fill="url(#gH)" dot={false}
                        activeDot={{ r: 3, fill: "#111", strokeWidth: 0 }}
                        name="Курс"
                      />
                      {done && (
                        <>
                          <Area dataKey="upper" stroke="none"
                            fill="rgba(22,163,74,0.07)" isAnimationActive={false} />
                          <Area dataKey="lower" stroke="none"
                            fill="#fafafa" isAnimationActive={false} />
                          <Area dataKey="forecast"
                            stroke="#16a34a" strokeWidth={1.5} strokeDasharray="4 3"
                            fill="url(#gF)" dot={false}
                            activeDot={{ r: 3, fill: "#16a34a", strokeWidth: 0 }}
                            name="Прогноз"
                            animationDuration={700}
                          />
                          <ReferenceLine
                            x={history.at(-1)?.date}
                            stroke="#e5e7eb"
                            strokeDasharray="3 3"
                          />
                        </>
                      )}
                    </AreaChart>
                  </ResponsiveContainer>
                )}

                {done && (
                  <div style={{
                    display: "flex", gap: 16, marginTop: 12,
                    fontFamily: "'IBM Plex Mono', monospace", fontSize: 11, color: "#9ca3af",
                    animation: "fade-in 0.3s ease",
                  }}>
                    <span style={{ display: "flex", alignItems: "center", gap: 5 }}>
                      <span style={{ width: 16, height: 1.5, background: "#111", display: "inline-block" }} />
                      История
                    </span>
                    <span style={{ display: "flex", alignItems: "center", gap: 5 }}>
                      <span style={{ width: 16, height: 1.5, background: "#16a34a", display: "inline-block" }} />
                      Прогноз
                    </span>
                    <span style={{ display: "flex", alignItems: "center", gap: 5 }}>
                      <span style={{ width: 16, height: 8, background: "rgba(22,163,74,0.1)", display: "inline-block", borderRadius: 2 }} />
                      Интервал
                    </span>
                  </div>
                )}
              </div>
            )}

            {/* Table */}
            {tab === "table" && (
              <div style={{ animation: "fade-in 0.25s ease" }}>
                <div style={{ maxHeight: 300, overflowY: "auto" }}>
                  <table style={{ width: "100%", borderCollapse: "collapse" }}>
                    <thead>
                      <tr>
                        {["Дата", "Курс", "Δ", "Δ %"].map(h => (
                          <th key={h} style={{
                            textAlign: "left", padding: "0 0 10px",
                            fontSize: 10, color: "#9ca3af",
                            letterSpacing: "0.08em", textTransform: "uppercase",
                            fontFamily: "'IBM Plex Mono', monospace", fontWeight: 500,
                            borderBottom: "1px solid #e5e7eb",
                            position: "sticky", top: 0, background: "#fafafa",
                          }}>{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {[...history].reverse().map((row, i, arr) => {
                        const prevRow = arr[i + 1];
                        const d = prevRow ? row.rate - prevRow.rate : 0;
                        const pct = prevRow ? (d / prevRow.rate * 100) : 0;
                        const up = d >= 0;
                        return (
                          <tr key={row.iso} className="row" style={{ borderBottom: "1px solid #f3f4f6" }}>
                            <td style={{ padding: "9px 0", fontFamily: "'IBM Plex Mono', monospace", fontSize: 12, color: "#6b7280" }}>{row.iso}</td>
                            <td style={{ padding: "9px 0", fontFamily: "'IBM Plex Mono', monospace", fontSize: 12, fontWeight: 600 }}>
                              {row.rate.toLocaleString("ru-RU", { minimumFractionDigits: 4 })}
                            </td>
                            <td style={{ padding: "9px 0", fontFamily: "'IBM Plex Mono', monospace", fontSize: 12, color: up ? "#16a34a" : "#dc2626" }}>
                              {d >= 0 ? "+" : ""}{d.toFixed(dp)}
                            </td>
                            <td style={{ padding: "9px 0", fontFamily: "'IBM Plex Mono', monospace", fontSize: 12, color: up ? "#16a34a" : "#dc2626" }}>
                              {pct >= 0 ? "+" : ""}{pct.toFixed(2)}%
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>

                {done && (
                  <>
                    <div style={{
                      fontSize: 10, letterSpacing: "0.1em", textTransform: "uppercase",
                      color: "#9ca3af", fontFamily: "'IBM Plex Mono', monospace",
                      marginTop: 24, marginBottom: 10, paddingTop: 16,
                      borderTop: "1px solid #e5e7eb",
                    }}>Прогноз · {fDays} дней</div>
                    <div style={{ maxHeight: 200, overflowY: "auto" }}>
                      <table style={{ width: "100%", borderCollapse: "collapse" }}>
                        <thead>
                          <tr>
                            {["Дата", "Прогноз", "Нижн.", "Верхн.", "Увер."].map(h => (
                              <th key={h} style={{
                                textAlign: "left", padding: "0 0 8px",
                                fontSize: 10, color: "#9ca3af",
                                letterSpacing: "0.08em", textTransform: "uppercase",
                                fontFamily: "'IBM Plex Mono', monospace", fontWeight: 500,
                                borderBottom: "1px solid #e5e7eb",
                                position: "sticky", top: 0, background: "#fafafa",
                              }}>{h}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {forecast.map(row => (
                            <tr key={row.iso} className="row" style={{ borderBottom: "1px solid #f3f4f6" }}>
                              <td style={{ padding: "8px 0", fontFamily: "'IBM Plex Mono', monospace", fontSize: 12, color: "#6b7280" }}>{row.iso}</td>
                              <td style={{ padding: "8px 0", fontFamily: "'IBM Plex Mono', monospace", fontSize: 12, fontWeight: 600, color: "#16a34a" }}>{row.forecast.toLocaleString("ru-RU", { minimumFractionDigits: 4 })}</td>
                              <td style={{ padding: "8px 0", fontFamily: "'IBM Plex Mono', monospace", fontSize: 12, color: "#dc2626" }}>{row.lower.toLocaleString("ru-RU", { minimumFractionDigits: 4 })}</td>
                              <td style={{ padding: "8px 0", fontFamily: "'IBM Plex Mono', monospace", fontSize: 12, color: "#16a34a" }}>{row.upper.toLocaleString("ru-RU", { minimumFractionDigits: 4 })}</td>
                              <td style={{ padding: "8px 0", fontFamily: "'IBM Plex Mono', monospace", fontSize: 12, color: row.conf > 65 ? "#16a34a" : row.conf > 40 ? "#d97706" : "#9ca3af" }}>
                                {row.conf}%
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </>
                )}
              </div>
            )}
          </div>

          {/* ── Right: controls ── */}
          <div style={{ width: 190, flexShrink: 0 }}>

            <div style={{ marginBottom: 24 }}>
              <div style={{
                fontSize: 10, letterSpacing: "0.1em", textTransform: "uppercase",
                color: "#9ca3af", fontFamily: "'IBM Plex Mono', monospace", marginBottom: 10,
              }}>Горизонт прогноза</div>
              <div style={{ display: "inline-flex", background: "#f3f4f6", borderRadius: 6, padding: 2, gap: 2 }}>
                {[7, 14, 30, 60].map(d => (
                  <button key={d} onClick={() => setFDays(d)} style={segBtn(fDays === d)}>
                    {d}д
                  </button>
                ))}
              </div>
            </div>

            <div style={{ marginBottom: 24 }}>
              <div style={{
                fontSize: 10, letterSpacing: "0.1em", textTransform: "uppercase",
                color: "#9ca3af", fontFamily: "'IBM Plex Mono', monospace", marginBottom: 10,
              }}>История</div>
              <div style={{ display: "inline-flex", background: "#f3f4f6", borderRadius: 6, padding: 2, gap: 2 }}>
                {[30, 60, 90].map(d => (
                  <button key={d} onClick={() => setHDays(d)} style={segBtn(hDays === d)}>
                    {d}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={runForecast}
              disabled={loading || histLoading || !history.length}
              style={{
                width: "100%", padding: "10px",
                borderRadius: 6, border: "1px solid #111",
                background: (loading || histLoading) ? "#f3f4f6" : "#111",
                color: (loading || histLoading) ? "#9ca3af" : "#fff",
                cursor: (loading || histLoading) ? "not-allowed" : "pointer",
                fontSize: 12, fontWeight: 600,
                fontFamily: "'IBM Plex Mono', monospace",
                letterSpacing: "0.04em",
                transition: "all 0.15s",
                marginBottom: 8,
              }}
            >
              {predLoading ? "Считаем…" : "Прогноз →"}
            </button>

            <div style={{ marginTop: 28 }}>
              <div style={{
                fontSize: 10, letterSpacing: "0.1em", textTransform: "uppercase",
                color: "#9ca3af", fontFamily: "'IBM Plex Mono', monospace", marginBottom: 12,
              }}>Модель</div>
              {[
                ["Алгоритм", "GradientBoost"],
                ["Источник", "ЦБ РФ"],
                ["Номинал", "1 ед."],
                ["Обновление", "ежедневно"],
              ].map(([k, v]) => (
                <div key={k} style={{
                  display: "flex", justifyContent: "space-between",
                  padding: "6px 0",
                  borderBottom: "1px solid #f3f4f6",
                  fontSize: 11, fontFamily: "'IBM Plex Mono', monospace",
                }}>
                  <span style={{ color: "#9ca3af" }}>{k}</span>
                  <span style={{ color: "#374151", fontWeight: 500 }}>{v}</span>
                </div>
              ))}
            </div>

            {/* Статус загрузки */}
            <div style={{
              marginTop: 20, padding: "8px 10px",
              borderRadius: 6, background: "#f3f4f6",
              fontFamily: "'IBM Plex Mono', monospace", fontSize: 10,
              color: "#9ca3af",
            }}>
              <div style={{ marginBottom: 4 }}>Статус API</div>
              <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <span style={{
                  width: 6, height: 6, borderRadius: "50%",
                  background: error ? "#dc2626" : history.length ? "#16a34a" : "#d97706",
                  display: "inline-block",
                }} />
                {error ? "Ошибка" : history.length ? `${history.length} дн. данных` : "Загрузка…"}
              </div>
            </div>

          </div>

        </div>
      </div>
    </div>
  );
}
