import { useState, useEffect } from 'react'
import { sites as sitesApi } from '../../api'
import SearchList from '../ui/SearchList'

const SCOPE_OPTIONS = [
  { id: 'individual', icon: '👤', label: 'Just them',     hint: 'One specific user or device' },
  { id: 'multiple',   icon: '👥', label: 'A few people',  hint: 'Multiple users in an area' },
  { id: 'site',       icon: '🏢', label: 'Whole site',    hint: 'Everyone at this location' },
]

export default function SiteStep({ wizard, update, onNext, onBack }) {
  const [sites, setSites]     = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)

  useEffect(() => {
    sitesApi.list()
      .then(d => setSites(d.sites))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const canNext = wizard.site !== null && wizard.scope !== null

  return (
    <>
      <div className="question">Where and how many people are affected?</div>
      <div className="question-hint">Knowing the scope helps pick the right Marvis queries.</div>

      <div className="field">
        <label>Scope of impact</label>
        <div className="scope-row">
          {SCOPE_OPTIONS.map(opt => (
            <button
              key={opt.id}
              className={`scope-btn ${wizard.scope === opt.id ? 'selected' : ''}`}
              onClick={() => update({ scope: opt.id })}
            >
              <span className="scope-icon">{opt.icon}</span>
              <div className="scope-label">{opt.label}</div>
              <div className="scope-hint">{opt.hint}</div>
            </button>
          ))}
        </div>
      </div>

      <div className="field">
        <label>Site</label>
        {error && <div className="alert alert-error mt-2"><span>⚠</span> {error}</div>}
        {loading ? (
          <div style={{ padding: 16, textAlign: 'center' }}><span className="spinner" /></div>
        ) : (
          <SearchList
            items={sites}
            selected={wizard.site}
            onSelect={s => update({ site: s, client: null })}
            renderItem={s => ({
              icon: '📍',
              main: s.name,
              sub: s.id,
            })}
            placeholder="Search sites…"
          />
        )}
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
