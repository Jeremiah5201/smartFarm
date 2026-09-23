function formatMessageTime(value) {
  if (!value) return "No timestamp";
  return new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export function MessagesPage({ messages, onRefresh }) {
  const sent = messages.filter((message) => message.status === "sent");
  const failed = messages.filter((message) => message.status !== "sent");

  return (
    <section className="messages-page">
      <div className="page-heading-row"><div><p className="eyebrow">COMMUNICATIONS</p><h1>Message center</h1><p className="intro-copy">Every field alert, with delivery status in one place.</p></div><button className="refresh-button" onClick={onRefresh}>Refresh messages</button></div>
      <div className="message-summary"><article><span className="summary-icon sent-icon">✓</span><div><strong>{sent.length}</strong><span>Sent successfully</span></div></article><article><span className="summary-icon failed-icon">!</span><div><strong>{failed.length}</strong><span>Failed delivery</span></div></article><article><span className="summary-icon total-icon">✉</span><div><strong>{messages.length}</strong><span>Total messages</span></div></article></div>
      <div className="message-columns">
        <MessageGroup title="Sent messages" eyebrow="DELIVERED" messages={sent} tone="sent" empty="No successfully delivered messages yet." />
        <MessageGroup title="Failed messages" eyebrow="NEEDS ATTENTION" messages={failed} tone="failed" empty="No failed messages. Your alerts are flowing." />
      </div>
    </section>
  );
}

function MessageGroup({ title, eyebrow, messages, tone, empty }) {
  return <section className="message-group"><div className="section-heading"><div><p className="eyebrow">{eyebrow}</p><h2>{title}</h2></div><span className={`message-count ${tone}`}>{messages.length}</span></div>{messages.length === 0 ? <div className="message-empty"><span>{tone === "sent" ? "✉" : "✓"}</span><p>{empty}</p></div> : <div className="message-list">{messages.map((message) => <article className="message-row" key={message.id || `${message.timestamp}-${message.recipient}`}><span className={`message-status ${tone}`}>{tone === "sent" ? "✓" : "!"}</span><div><strong>{message.recipient || "Unknown recipient"}</strong><p>{message.message || message.body || "No message content"}</p><time>{formatMessageTime(message.timestamp)} · {message.provider_status || message.status}</time></div></article>)}</div>}</section>;
}
