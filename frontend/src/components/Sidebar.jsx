const navigation = [
  { id: "dashboard", icon: "⌂", label: "Dashboard" },
  { id: "farms", icon: "▦", label: "My farms" },
  { id: "irrigation", icon: "≈", label: "Irrigation" },
  { id: "telemetry", icon: "◌", label: "Telemetry" },
  { id: "messages", icon: "✉", label: "Messages" },
  { id: "weather", icon: "☼", label: "Weather" },
];

export function Sidebar({ activePage, onNavigate, health }) {
  return (
    <aside className="sidebar">
      <div className="brand"><span className="brand-mark">SF</span><span>SmartFarm<small>FIELD OPERATIONS</small></span></div>
      <div className="sidebar-label">WORKSPACE</div>
      <nav className="sidebar-nav" aria-label="Main navigation">
        {navigation.map((item) => (
          <button key={item.id} className={`sidebar-link ${activePage === item.id ? "active" : ""}`} onClick={() => onNavigate(item.id)}>
            <span className="sidebar-icon">{item.icon}</span>{item.label}
            {item.id === "messages" && <span className="nav-badge">{health?.status === "ok" ? "" : "!"}</span>}
          </button>
        ))}
      </nav>
      <div className="sidebar-divider" />
      <button className={`sidebar-link ${activePage === "settings" ? "active" : ""}`} onClick={() => onNavigate("settings")}><span className="sidebar-icon">⚙</span>Settings</button>
      <div className="sidebar-note"><span className={`pulse ${health?.status !== "ok" ? "offline" : ""}`} />{health?.status === "ok" ? "Backend connected" : "Connection needs attention"}</div>
    </aside>
  );
}
