import { TIMEFRAMES } from '../../runbooks'

export default function ReporterStep({ wizard, update, onNext, onBack }) {
  const canNext = wizard.reporter.trim().length > 0

  return (
    <>
      <div className="question">Who reported this, and when?</div>
      <div className="question-hint">This goes into the ticket notes.</div>

      <div className="field">
        <label>Reporter — name or username</label>
        <input
          type="text"
          placeholder="e.g. Sarah Johnson or sjohnson"
          value={wizard.reporter}
          onChange={e => update({ reporter: e.target.value })}
          autoFocus
        />
      </div>

      <div className="field">
        <label>Your name (tech handling the ticket)</label>
        <input
          type="text"
          placeholder="Your name"
          value={wizard.techName}
          onChange={e => update({ techName: e.target.value })}
        />
      </div>

      <div className="field">
        <label>When did it start?</label>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {TIMEFRAMES.map(tf => (
            <button
              key={tf.id}
              className={`btn btn-sm ${wizard.timeframe === tf.id ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => update({ timeframe: tf.id })}
            >
              {tf.label}
            </button>
          ))}
        </div>
      </div>

      <div className="nav-row">
        <button className="btn btn-secondary" onClick={onBack}>← Back</button>
        <button className="btn btn-primary" onClick={onNext} disabled={!canNext}>
          Next →
        </button>
      </div>
    </>
  )
}
