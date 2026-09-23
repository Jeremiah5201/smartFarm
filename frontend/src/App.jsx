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

function displayValue(value, fallback) {
  return value == null || value === "" ? fallback : value;
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

const defaultProfile = { name: "Amina Okafor", phone: "+234 803 555 0184", email: "amina@smartfarm.local", location: "Ibadan, Nigeria" };

function Modal({ title, eyebrow, children, onClose }) {
  return <div className="modal-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && onClose()}><section className="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title"><button className="modal-close" onClick={onClose} aria-label="Close dialog">×</button><p className="eyebrow">{eyebrow}</p><h2 id="modal-title">{title}</h2>{children}</section></div>;
}

function App() {
  const [farmId, setFarmId] = useState("");
  const [slide, setSlide] = useState(0);
  const [modal, setModal] = useState(null);
  const [profile, setProfile] = useState(() => {
    try { return { ...defaultProfile, ...JSON.parse(localStorage.getItem("smartfarm-profile") || "{}") }; } catch { return defaultProfile; }
  });
  const [farmState, setFarmState] = useState({ saving: false, error: "" });
  const [commandState, setCommandState] = useState({ saving: false, message: "", error: "" });
  const { farms, latest, readings, history, advisory, weather, smsHistory, health, latestError, loading, refreshing, error, reload } = useFarmData(farmId);
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

  async function submitFarm(event) {
    event.preventDefault();
    const newFarm = Object.fromEntries(new FormData(event.currentTarget).entries());
    setFarmState({ saving: true, error: "" });
    try {
      await api.createFarm(newFarm);
      setFarmId(newFarm.farm_id);
      setModal(null);
      setFarmState({ saving: false, error: "" });
      reload();
    } catch (submitError) {
      setFarmState({ saving: false, error: submitError.message });
    }
  }

  function submitProfile(event) {
    event.preventDefault();
    const nextProfile = Object.fromEntries(new FormData(event.currentTarget).entries());
    setProfile(nextProfile);
    localStorage.setItem("smartfarm-profile", JSON.stringify(nextProfile));
    setModal(null);
  }

  return (
    <div className="app-shell">
      <main className="main-content">
        <header className="topbar"><div className="brand"><span className="brand-mark">SF</span><span>SmartFarm<small>FIELD OPERATIONS</small></span></div><nav className="top-nav"><a className="nav-link active" href="#overview">Overview</a><a className="nav-link" href="#irrigation">Irrigation</a><a className="nav-link" href="#activity">Activity</a></nav><div className="account-actions"><button className="add-farm-button" onClick={() => setModal("farm")}>＋ <span>Add farm</span></button><button className="profile-button" onClick={() => setModal("profile")}><span className="avatar">{profile.name.charAt(0)}</span><span className="profile-name">{profile.name}</span><span className="chevron">⌄</span></button></div></header>
        <section className="page-intro"><div><p className="eyebrow">FIELD CONTROL ROOM</p><h1>Farm overview</h1><p className="intro-copy">A calmer way to understand what your fields need next.</p></div><div className="top-actions"><label className="farm-picker">Active farm<select value={activeFarmId || ""} onChange={(event) => setFarmId(event.target.value)}><option value="" disabled>Select a farm</option>{farms.map((farm) => <option key={farm.farm_id} value={farm.farm_id}>{farm.farm_name} · {farm.farm_id}</option>)}</select></label><button className="refresh-button" onClick={reload} disabled={refreshing}>{refreshing ? "Refreshing" : "Refresh data"}</button></div></section>

        {loading && <section className="state-panel"><div className="spinner" /><h2>Connecting to your farm data</h2><p>Reading the backend API and preparing the dashboard.</p></section>}
        {!loading && error && <section className="state-panel error-state"><h2>Backend unavailable</h2><p>{error}</p><button className="primary-button" onClick={reload}>Try again</button></section>}
        {!loading && !error && farms.length === 0 && <section className="state-panel"><h2>No farms registered</h2><p>Create a farm through the backend API before opening the dashboard.</p></section>}

        {!loading && !error && selectedFarm && <>
          <section className="hero-strip" id="overview"><div className="hero-copy"><span className="status-chip"><span className={`pulse ${latest ? "" : "offline"}`} /> {latest ? "Telemetry received" : "Waiting for telemetry"}</span><h2>{selectedFarm.farm_name}</h2><p>{displayValue(selectedFarm.location, "Location not configured")} <span className="separator">/</span> {displayValue(selectedFarm.crop, "Crop not configured")}</p></div><div className="hero-visual" style={{ backgroundImage: `url(https://images.unsplash.com/photo-${["1500937386664-56d1dfef3854", "1464226184884-fa280b87c399", "1499529112087-3cb3b73cec95"][slide]}?auto=format&fit=crop&w=900&q=80)` }}><div className="visual-overlay"><span>FIELD VIEW 0{slide + 1}</span><strong>Growing conditions, at a glance.</strong><div className="slider-dots">{[0, 1, 2].map((item) => <button key={item} className={item === slide ? "active" : ""} onClick={() => setSlide(item)} aria-label={`Show field view ${item + 1}`} />)}</div></div></div><div className="hero-meta"><span>LAST TELEMETRY</span><strong>{formatTime(latest?.timestamp)}</strong><span className="device-id">{selectedFarm.device_id}</span></div></section>

          <div className="status-marquee" aria-label="SmartFarm status updates"><div><span>SMARTFARM LIVE</span><i /> Soil intelligence <i /> Closed-loop irrigation <i /> Field telemetry synced <i /> Weather-ready data <i /> SMARTFARM LIVE <i /> Soil intelligence <i /> Closed-loop irrigation</div></div>

          <section className="section-block"><div className="section-heading"><div><p className="eyebrow">LIVE CONDITIONS</p><h2>Sensor readings</h2></div><span className="updated">Updated {formatTime(latest?.timestamp)}</span></div>{latestError && <p className="inline-warning">Latest reading unavailable: {latestError}</p>}<div className="metric-grid">{metricCards.map(([field, label, unit, tone]) => <MetricCard key={field} field={field} label={label} unit={unit} tone={tone} value={latest?.[field]} />)}<MetricCard field="rain_detected" label="Rain status" unit="" tone="blue" value={latest ? (latest.rain_detected ? "Detected" : "Clear") : null} /></div></section>

          <section className="content-grid" id="irrigation"><div className="panel"><div className="panel-heading"><div><p className="eyebrow">WATER SYSTEM</p><h2>Irrigation control</h2></div><span className={`pump-state ${latest?.pump_status ? "on" : "off"}`}>{latest?.pump_status ? "Pump on" : "Pump off"}</span></div><div className="pump-summary"><div className={`pump-icon ${latest?.pump_status ? "active" : ""}`}>≈</div><div><strong>{latest?.pump_status ? "Irrigating now" : "Standby"}</strong><p>{latest?.pump_status ? "The device reports an active pump." : "No active irrigation command reported."}</p></div></div><form className="override-form" onSubmit={submitOverride}><label className="toggle-row"><span><strong>Start pump</strong><small>Send a controlled MQTT command</small></span><input type="checkbox" name="pump" defaultChecked /></label><label>Duration (seconds)<input name="duration_sec" type="number" min="1" max="3600" defaultValue="30" required /></label><label>Reason<input name="reason" type="text" placeholder="e.g. Dry soil confirmed" required /></label><button className="primary-button" disabled={commandState.saving}>{commandState.saving ? "Publishing..." : "Publish command"}</button>{commandState.message && <p className="form-success">{commandState.message}</p>}{commandState.error && <p className="form-error">{commandState.error}</p>}</form></div>
            <div className="panel" id="activity"><div className="panel-heading"><div><p className="eyebrow">RECENT EVENTS</p><h2>Irrigation history</h2></div><span className="event-count">{history.length} events</span></div>{history.length === 0 ? <div className="empty-state">No irrigation events recorded yet.</div> : <div className="event-list">{history.map((event) => <div className="event-row" key={event.command_id || event.timestamp}><span className={`event-marker ${event.pump_status ? "on" : "off"}`} /><div><strong>{event.pump_status ? "Pump activated" : "Pump stopped"}</strong><p>{event.reason}</p></div><time>{formatTime(event.timestamp)}<br /><b>{event.duration_sec}s</b></time></div>)}</div>}</div></section>

          <section className="section-block readings-section"><div className="section-heading"><div><p className="eyebrow">DATABASE HISTORY</p><h2>Recent telemetry</h2></div><span className="updated">{readings.length} readings loaded</span></div><div className="table-wrap"><table><thead><tr><th>Timestamp</th><th>Moisture</th><th>pH</th><th>Temperature</th><th>Humidity</th><th>Rain</th></tr></thead><tbody>{readings.map((reading) => <tr key={`${reading.timestamp}-${reading.device_id}`}><td>{formatTime(reading.timestamp)}</td><td>{reading.soil_moisture}%</td><td>{reading.soil_ph}</td><td>{reading.temperature}°C</td><td>{reading.humidity}%</td><td><span className={`rain-tag ${reading.rain_detected ? "yes" : "no"}`}>{reading.rain_detected ? "Detected" : "Clear"}</span></td></tr>)}</tbody></table>{readings.length === 0 && <div className="empty-state">Telemetry will appear here after the ESP32 publishes a reading.</div>}</div></section>
          <section className="insight-grid"><div className="insight-panel"><p className="eyebrow">FIELD ADVISORY</p><h2>{advisory[0]?.type || "No advisory yet"}</h2><p>{advisory[0]?.message || "The intelligence service has not published a recommendation."}</p><span className="insight-meta">{advisory[0]?.severity || "WAITING"}</span></div><div className="insight-panel weather-panel"><p className="eyebrow">WEATHER CONTEXT</p><h2>{weather?.temperature != null ? `${weather.temperature}°C · ${displayValue(weather.description, "Current conditions")}` : "Weather unavailable"}</h2><p>{weather?.rain_probability != null ? `Rain probability ${weather.rain_probability}%${weather.location ? ` in ${weather.location}` : ""}.` : "Forecast data is not available yet."}</p><span className="insight-meta">{displayValue(weather?.source, "NOT CONNECTED")}</span></div><div className="insight-panel"><p className="eyebrow">SMS HISTORY</p><h2>{smsHistory.length ? `${smsHistory.length} messages` : "No messages yet"}</h2><p>{smsHistory.length ? "Recent farmer notifications are available." : "SMS notifications will appear after the advisory service sends one."}</p><span className="insight-meta">FARMER ALERTS</span></div></section>
        </>}
        {modal === "farm" && <Modal eyebrow="NEW FIELD" title="Add a farm" onClose={() => setModal(null)}><form className="modal-form" onSubmit={submitFarm}><label>Farm ID<input name="farm_id" placeholder="FARM002" required /></label><label>Farm name<input name="farm_name" placeholder="North Field" required /></label><label>Device ID<input name="device_id" placeholder="ESP32-02" required /></label><div className="form-columns"><label>Location<input name="location" placeholder="Oyo, Nigeria" /></label><label>Crop<input name="crop" placeholder="Tomatoes" /></label></div><button className="primary-button" disabled={farmState.saving}>{farmState.saving ? "Creating farm..." : "Create farm"}</button>{farmState.error && <p className="form-error">{farmState.error}</p>}</form></Modal>}
        {modal === "profile" && <Modal eyebrow="YOUR ACCOUNT" title="Profile settings" onClose={() => setModal(null)}><form className="modal-form" onSubmit={submitProfile}><div className="profile-editor"><span className="avatar large">{profile.name.charAt(0)}</span><div><strong>{profile.name}</strong><p>Keep your contact details current for field alerts.</p></div></div><label>Full name<input name="name" defaultValue={profile.name} required /></label><label>Phone number<input name="phone" type="tel" defaultValue={profile.phone} required /></label><label>Email address<input name="email" type="email" defaultValue={profile.email} required /></label><label>Home location<input name="location" defaultValue={profile.location} /></label><button className="primary-button">Save profile</button></form></Modal>}
      </main>
    </div>
  );
}

export default App;