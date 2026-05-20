import { useState, useEffect } from 'react'
import { marvis as marvisApi } from '../../api'
import QueryCard from '../ui/QueryCard'

function clientIdentifier(client) {
  if (!client) return null
  return client.username || client.hostname || client.mac || null
}

export default function InvestigateStep({ wizard, update, onNext, onBack }) {
  const [suggestions, setSuggestions] = useState(wizard.suggestions || [])
  const [escalation, setEscalation]   = useState(wizard.escalationGuidance || null)
  const [loading, setLoading]         = useState(suggestions.length === 0)
  const [customQuery, setCustomQuery] = useState('')
  const [customRunning, setCustomRunning] = useState(false)

  useEffect(() => {
    if (suggestions.length > 0) return
    marvisApi.suggestions({
      category_id: wizard.category?.id || 'other',
      client:      clientIdentifier(wizard.client),
      site:        wizard.site?.name,
      timeframe:   wizard.timeframe,
    })
      .then(d => {
        setSuggestions(d.queries)
        setEscalation(d.escalation_guidance)
        update({ suggestions: d.queries, escalationGuidance: d.escalation_guidance })
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const handleResult = (index, result, included) => {
    const updated = [...(wizard.queryResults || [])]
    const existing = updated.findIndex(r => r.query === suggestions[index].query)
    const entry = { ...suggestions[index], result, included }
    if (existing >= 0) {
      updated[existing] = entry
    } else {
      updated.push(entry)
    }
    update({ queryResults: updated })
  }

  const runCustom = async () => {
    if (!customQuery.trim()) return
    setCustomRunning(true)
    try {
      const result = await marvisApi.query(customQuery.trim())
      const entry = { label: 'Custom query', query: customQuery.trim(), result, included: true }
      const updated = [...(wizard.queryResults || []), entry]
      update({ queryResults: updated })
      setCustomQuery('')
    } catch (err) {
      alert(`Query failed: ${err.message}`)
    } finally {
      setCustomRunning(false)
    }
  }

  const includedCount = (wizard.queryResults || []).filter(r => r.included).length

  return (
    <>
      <div className="question">Investigate with Marvis</div>
      <div className="question-hint">
        Click <strong>Run</strong> on queries to execute them. Check the ones you want included in the ticket notes.
        {wizard.client && (
          <> Pre-filled for <strong>{clientIdentifier(wizard.client)}</strong> at <strong>{wizard.site?.name}</strong>.</>
        )}
      </div>

      {escalation && (
        <div className="alert alert-warn" style={{ marginBottom: 16 }}>
          <span>⚠</span> <strong>Escalation note:</strong> {escalation}
        </div>
      )}

      {loading ? (
        <div style={{ padding: 24, textAlign: 'center' }}><span className="spinner" /></div>
      ) : (
        <div className="query-list">
          {suggestions.map((s, i) => (
            <QueryCard
              key={i}
              label={s.label}
              query={s.query}
              existingResult={wizard.queryResults?.find(r => r.query === s.query)}
              onResult={(result, included) => handleResult(i, result, included)}
            />
          ))}
        </div>
      )}

      {/* Custom query */}
      <div className="query-custom">
        <label>Run a custom Marvis query</label>
        <div style={{ display: 'flex', gap: 8, marginTop: 6 }}>
          <input
            type="text"
            placeholder='e.g. "show me events for john in the last 2 hours"'
            value={customQuery}
            onChange={e => setCustomQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && runCustom()}
          />
          <button
            className="btn btn-primary btn-sm"
            onClick={runCustom}
            disabled={!customQuery.trim() || customRunning}
            style={{ whiteSpace: 'nowrap' }}
          >
            {customRunning ? <span className="spinner" /> : 'Run'}
          </button>
        </div>
      </div>

      <div className="nav-row">
        <button className="btn btn-secondary" onClick={onBack}>← Back</button>
        <span className="text-sm text-muted" style={{ marginRight: 'auto', alignSelf: 'center' }}>
          {includedCount > 0 && `${includedCount} result${includedCount > 1 ? 's' : ''} added to notes`}
        </span>
        <button className="btn btn-primary" onClick={onNext}>
          Generate notes →
        </button>
      </div>
    </>
  )
}
