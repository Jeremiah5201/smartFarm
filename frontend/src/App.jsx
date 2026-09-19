import { useEffect, useMemo, useState } from "react";
import { api } from "./services/api";
import { useFarmData } from "./hooks/useFarmData";

const metricCards = [
  ["soil_moisture", "Soil moisture", "%", "teal"],
  ["soil_ph", "Soil pH", "pH", "blue"],
  ["temperature", "Temperature", "°C", "orange"],
  ["humidity", "Humidity", "%", "sky"],
  ["light", "Light level", "%", "yellow"],
  ["water_level", "Water tank", "%", "green"],
];

function formatTime(value) {
  if (!value) return "No reading yet";
  return new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

function MetricCard({ field, label, unit, tone, value }) {
  return (
    <article className={`metric-card ${tone}`}>
      <div className="metric-label"><span className="metric-dot" />{label}</div>
      <strong>{value ?? "--"}<small>{value == null ? "" : ` ${unit}`}</small></strong>
      <span className="metric-foot">Live sensor value</span>
    </article>
  );
}

function App() {
  const [farmId, setFarmId] = useState("");
  const [slide, setSlide] = useState(0);
  const [commandState, setCommandState] = useState({ saving: false, message: "", error: "" });
  const { farms, latest, readings, history, health, latestError, loading, refreshing, error, reload } = useFarmData(farmId);
  const selectedFarm = useMemo(() => farms.find((farm) => farm.farm_id === (farmId || farms[0]?.farm_id)), [farms, farmId]);
  const activeFarmId = selectedFarm?.farm_id;

  useEffect(() => {
    if (!farmId && farms[0]?.farm_id) setFarmId(farms[0].farm_id);
  }, [farms, farmId]);

  useEffect(() => {
    const timer = window.setInterval(() => setSlide((current) => (current + 1) % 3), 6000);
    return () => window.clearInterval(timer);
  }, []);

  async function submitOverride(event) {
    event.preventDefault();
    if (!activeFarmId) return;
    const form = new FormData(event.currentTarget);
    setCommandState({ saving: true, message: "", error: "" });
    try {
      await api.override(activeFarmId, {
        pump: form.get("pump") === "on",
        duration_sec: Number(form.get("duration_sec")),
        reason: form.get("reason"),
        force_override: false,
      });
      event.currentTarget.reset();
      setCommandState({ saving: false, message: "Command published to the device.", error: "" });
      reload();
    } catch (submitError) {
      setCommandState({ saving: false, message: "", error: submitError.message });
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">SF</span><span>SmartFarm<small>FIELD OPERATIONS</small></span></div>
        <nav><a className="nav-link active" href="#overview"><span>◈</span> Overview</a><a className="nav-link" href="#irrigation"><span>◌</span> Irrigation</a><a className="nav-link" href="#activity"><span>≋</span> Activity</a></nav>
        <div className="sidebar-note"><span className={`pulse ${health?.status !== "ok" ? "offline" : ""}`} />{health?.status === "ok" ? "Backend connected through REST API" : "Backend connection needs attention"}</div>
      </aside>

      <main className="main-content">
        <header className="topbar"><div><p className="eyebrow">FIELD CONTROL ROOM</p><h1>Farm overview</h1></div><div className="top-actions"><label className="farm-picker">Farm<select value={activeFarmId || ""} onChange={(event) => setFarmId(event.target.value)}><option value="" disabled>Select a farm</option>{farms.map((farm) => <option key={farm.farm_id} value={farm.farm_id}>{farm.farm_name} · {farm.farm_id}</option>)}</select></label><button className="refresh-button" onClick={reload} disabled={refreshing}>{refreshing ? "Refreshing" : "Refresh data"}</button></div></header>

        {loading && <section className="state-panel"><div className="spinner" /><h2>Connecting to your farm data</h2><p>Reading the backend API and preparing the dashboard.</p></section>}
        {!loading && error && <section className="state-panel error-state"><h2>Backend unavailable</h2><p>{error}</p><button className="primary-button" onClick={reload}>Try again</button></section>}
        {!loading && !error && farms.length === 0 && <section className="state-panel"><h2>No farms registered</h2><p>Create a farm through the backend API before opening the dashboard.</p></section>}

        {!loading && !error && selectedFarm && <>
          <section className="hero-strip" id="overview"><div className="hero-copy"><span className="status-chip"><span className={`pulse ${latest ? "" : "offline"}`} /> {latest ? "Telemetry received" : "Waiting for telemetry"}</span><h2>{selectedFarm.farm_name}</h2><p>{selectedFarm.location || "Location not configured"} <span className="separator">/</span> {selectedFarm.crop || "Crop not configured"}</p></div><div className="hero-visual" style={{ backgroundImage: `url(https://images.unsplash.com/photo-${["1500937386664-56d1dfef3854", "1464226184884-fa280b87c399", "1499529112087-3cb3b73cec95"][slide]}?auto=format&fit=crop&w=900&q=80)` }}><div className="visual-overlay"><span>FIELD VIEW 0{slide + 1}</span><strong>Growing conditions, at a glance.</strong><div className="slider-dots">{[0, 1, 2].map((item) => <button key={item} className={item === slide ? "active" : ""} onClick={() => setSlide(item)} aria-label={`Show field view ${item + 1}`} />)}</div></div></div><div className="hero-meta"><span>LAST TELEMETRY</span><strong>{formatTime(latest?.timestamp)}</strong><span className="device-id">{selectedFarm.device_id}</span></div></section>

          <div className="status-marquee" aria-label="SmartFarm status updates"><div><span>SMARTFARM LIVE</span><i /> Soil intelligence <i /> Closed-loop irrigation <i /> Field telemetry synced <i /> Weather-ready data <i /> SMARTFARM LIVE <i /> Soil intelligence <i /> Closed-loop irrigation</div></div>

          <section className="section-block"><div className="section-heading"><div><p className="eyebrow">LIVE CONDITIONS</p><h2>Sensor readings</h2></div><span className="updated">Updated {formatTime(latest?.timestamp)}</span></div>{latestError && <p className="inline-warning">Latest reading unavailable: {latestError}</p>}<div className="metric-grid">{metricCards.map(([field, label, unit, tone]) => <MetricCard key={field} field={field} label={label} unit={unit} tone={tone} value={latest?.[field]} />)}<MetricCard field="rain_detected" label="Rain status" unit="" tone="blue" value={latest ? (latest.rain_detected ? "Detected" : "Clear") : null} /></div></section>

          <section className="content-grid" id="irrigation"><div className="panel"><div className="panel-heading"><div><p className="eyebrow">WATER SYSTEM</p><h2>Irrigation control</h2></div><span className={`pump-state ${latest?.pump_status ? "on" : "off"}`}>{latest?.pump_status ? "Pump on" : "Pump off"}</span></div><div className="pump-summary"><div className={`pump-icon ${latest?.pump_status ? "active" : ""}`}>≈</div><div><strong>{latest?.pump_status ? "Irrigating now" : "Standby"}</strong><p>{latest?.pump_status ? "The device reports an active pump." : "No active irrigation command reported."}</p></div></div><form className="override-form" onSubmit={submitOverride}><label className="toggle-row"><span><strong>Start pump</strong><small>Send a controlled MQTT command</small></span><input type="checkbox" name="pump" defaultChecked /></label><label>Duration (seconds)<input name="duration_sec" type="number" min="1" max="3600" defaultValue="30" required /></label><label>Reason<input name="reason" type="text" placeholder="e.g. Dry soil confirmed" required /></label><button className="primary-button" disabled={commandState.saving}>{commandState.saving ? "Publishing..." : "Publish command"}</button>{commandState.message && <p className="form-success">{commandState.message}</p>}{commandState.error && <p className="form-error">{commandState.error}</p>}</form></div>
            <div className="panel" id="activity"><div className="panel-heading"><div><p className="eyebrow">RECENT EVENTS</p><h2>Irrigation history</h2></div><span className="event-count">{history.length} events</span></div>{history.length === 0 ? <div className="empty-state">No irrigation events recorded yet.</div> : <div className="event-list">{history.map((event) => <div className="event-row" key={event.command_id || event.timestamp}><span className={`event-marker ${event.pump_status ? "on" : "off"}`} /><div><strong>{event.pump_status ? "Pump activated" : "Pump stopped"}</strong><p>{event.reason}</p></div><time>{formatTime(event.timestamp)}<br /><b>{event.duration_sec}s</b></time></div>)}</div>}</div></section>

          <section className="section-block readings-section"><div className="section-heading"><div><p className="eyebrow">DATABASE HISTORY</p><h2>Recent telemetry</h2></div><span className="updated">{readings.length} readings loaded</span></div><div className="table-wrap"><table><thead><tr><th>Timestamp</th><th>Moisture</th><th>pH</th><th>Temperature</th><th>Humidity</th><th>Rain</th></tr></thead><tbody>{readings.map((reading) => <tr key={`${reading.timestamp}-${reading.device_id}`}><td>{formatTime(reading.timestamp)}</td><td>{reading.soil_moisture}%</td><td>{reading.soil_ph}</td><td>{reading.temperature}°C</td><td>{reading.humidity}%</td><td><span className={`rain-tag ${reading.rain_detected ? "yes" : "no"}`}>{reading.rain_detected ? "Detected" : "Clear"}</span></td></tr>)}</tbody></table>{readings.length === 0 && <div className="empty-state">Telemetry will appear here after the ESP32 publishes a reading.</div>}</div></section>
          <section className="coming-soon"><span>MEMBER 3 + MEMBER 4 INTEGRATION</span><strong>Advisories, weather and SMS history will appear here when their API endpoints are connected.</strong></section>
        </>}
      </main>
    </div>
  );
}

export default App;