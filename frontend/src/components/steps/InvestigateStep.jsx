import { useState, useEffect } from 'react'
import { marvis as marvisApi } from '../../api'
import QueryCard from '../ui/QueryCard'

export default function InvestigateStep({ wizard, update, onNext, onBack }) {
  const [suggestions, setSuggestions] = useState(wizard.suggestions || [])
  const [escalation, setEscalation]   = useState(wizard.escalationGuidance || null)
  const [loading, setLoading]         = useState(suggestions.length === 0)

  const mac      = wizard.client?.mac
  const siteId   = wizard.site?.id
  const siteName = wizard.site?.name

  // Filter out client-type cards if no MAC available
  const visibleSuggestions = suggestions.filter(
    s => s.troubleshoot_type !== 'client' || mac
  )

  useEffect(() => {
    if (suggestions.length > 0) return
    marvisApi.suggestions({ category_id: wizard.category?.id || 'other' })
      .then(d => {
        setSuggestions(d.queries)
        setEscalation(d.escalation_guidance)
        update({ suggestions: d.queries, escalationGuidance: d.escalation_guidance })
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const handleResult = (index, result, included, displayQuery) => {
    const tt = visibleSuggestions[index].troubleshoot_type
    const updated = [...(wizard.queryResults || [])]
    const existing = updated.findIndex(r => r.troubleshoot_type === tt)
    const entry = { ...visibleSuggestions[index], query: displayQuery, result, included }
    if (existing >= 0) {
      updated[existing] = entry
    } else {
      updated.push(entry)
    }
    update({ queryResults: updated })
  }

  const includedCount = (wizard.queryResults || []).filter(r => r.included).length

  return (
    <>
      <div className="question">Investigate with Marvis</div>
      <div className="question-hint">
        Click <strong>Run</strong> on queries to execute them. Check the ones you want included in the ticket notes.
        {wizard.client && mac && (
          <> Pre-filled for <strong>{wizard.client.username || wizard.client.hostname || mac}</strong> at <strong>{siteName}</strong>.</>
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
          {visibleSuggestions.map((s, i) => (
            <QueryCard
              key={s.troubleshoot_type}
              label={s.label}
              troubleshootType={s.troubleshoot_type}
              mac={mac}
              siteId={siteId}
              siteName={siteName}
              existingResult={wizard.queryResults?.find(r => r.troubleshoot_type === s.troubleshoot_type)}
              onResult={(result, included, displayQuery) => handleResult(i, result, included, displayQuery)}
            />
          ))}
        </div>
      )}

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
