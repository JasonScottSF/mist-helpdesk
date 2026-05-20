import { useState } from 'react'
import { marvis as marvisApi } from '../../api'

const TYPE_LABELS = {
  client:   (mac, _site)  => `Client diagnostic — ${mac}`,
  wireless: (_mac, site)  => `Site wireless health — ${site}`,
  wired:    (_mac, site)  => `Site wired health — ${site}`,
  wan:      (_mac, site)  => `WAN / gateway health — ${site}`,
}

function buildDisplayQuery(type, mac, siteName) {
  const fn = TYPE_LABELS[type]
  return fn ? fn(mac || 'unknown', siteName || 'unknown') : type
}

function formatResult(result) {
  if (!result) return ''
  if (typeof result === 'string') return result
  // Mist insights/troubleshoot: {data: {results: [{category, text}]}}
  const rows = result?.data?.results
  if (Array.isArray(rows)) {
    if (rows.length === 0) return 'No issues found.'
    return rows.map(r => r.category ? `[${r.category}]\n${r.text}` : r.text).join('\n\n')
  }
  if (result.text)     return result.text
  if (result.response) return result.response
  if (result.message)  return result.message
  return JSON.stringify(result, null, 2)
}

export default function QueryCard({ label, troubleshootType, mac, siteId, siteName, existingResult, onResult }) {
  const displayQuery = buildDisplayQuery(troubleshootType, mac, siteName)

  const [running, setRunning]   = useState(false)
  const [result, setResult]     = useState(existingResult?.result || null)
  const [included, setIncluded] = useState(existingResult?.included ?? false)
  const [error, setError]       = useState(null)

  const run = async () => {
    setRunning(true)
    setError(null)
    try {
      const data = await marvisApi.query({
        troubleshoot_type: troubleshootType,
        mac:     troubleshootType === 'client' ? mac     : undefined,
        site_id: troubleshootType !== 'client' ? siteId  : undefined,
      })
      setResult(data)
      setIncluded(true)
      onResult(data, true, displayQuery)
    } catch (err) {
      setError(err.message)
    } finally {
      setRunning(false)
    }
  }

  const toggle = (checked) => {
    setIncluded(checked)
    onResult(result, checked, displayQuery)
  }

  const hasResult = result !== null

  return (
    <div className={`query-card ${hasResult ? 'has-result' : ''}`}>
      <div className="query-card-header">
        <div className="query-info">
          <div className="query-label">{label}</div>
          <div className="query-text">{displayQuery}</div>
        </div>
        <button
          className={`btn-run ${running ? 'running' : ''}`}
          onClick={run}
          disabled={running}
        >
          {running
            ? <span className="spinner" style={{ width: 12, height: 12, borderWidth: 2 }} />
            : hasResult ? 'Re-run' : 'Run'}
        </button>
      </div>

      {error && (
        <div style={{ padding: '8px 16px', background: 'var(--red-light)', color: 'var(--red)', fontSize: 13 }}>
          ⚠ {error}
        </div>
      )}

      {hasResult && (
        <>
          <div className="query-result">{formatResult(result)}</div>
          <div className="query-result-footer">
            <input
              type="checkbox"
              id={`include-${troubleshootType}`}
              checked={included}
              onChange={e => toggle(e.target.checked)}
            />
            <label htmlFor={`include-${troubleshootType}`} style={{ textTransform: 'none', letterSpacing: 0, color: 'var(--text-muted)', fontSize: 13, fontWeight: 400 }}>
              Include in ticket notes
            </label>
          </div>
        </>
      )}
    </div>
  )
}
