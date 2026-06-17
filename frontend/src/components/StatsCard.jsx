function StatsCard({ label, value, accent = "default" }) {
  return (
    <article className={`stats-card ${accent}`}>
      <p className="stats-label">{label}</p>
      <p className="stats-value">{value}</p>
    </article>
  )
}

export default StatsCard
