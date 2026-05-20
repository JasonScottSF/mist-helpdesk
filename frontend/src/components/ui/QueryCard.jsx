import { useState } from 'react'
import { marvis as marvisApi } from '../../api'

function formatResult(result) {
  if (!result) return ''
  if (typeof result === 'string') return result
  if (result.response) return result.response
  if (result.text)     return result.text
  if (result.message)  return result.message
  return JSON.stringify(result, null, 2)
}

export default function QueryCard({ label, query, existingResult, onResult }) {
  const [running, setRunning]   = useState(false)
  const [result, setResult]     = useState(existingResult?.result || null)
  const [included, setIncluded] = useState(existingResult?.included ?? false)
  const [error, setError]       = useState(null)

  const run = async () => {
    setRunning(true)
    setError(null)
    try {
      const data = await marvisApi.query(query)
      setResult(data)
      setIncluded(true)
      onResult(data, true)
    } catch (err) {
      setError(err.message)
    } finally {
      setRunning(false)
    }
  }

  const toggle = (checked) => {
    setIncluded(checked)
    onResult(result, checked)
  }

  const hasResult = result !== null

  return (
    <div className={`query-card ${hasResult ? 'has-result' : ''}`}>
      <div className="query-card-header">
        <div className="query-info">
          <div className="query-label">{label}</div>
          <div className="query-text">{query}</div>
        </div>
        <button
          className={`btn-run ${running ? 'running' : ''}`}
          onClick={run}
          disabled={running}
        >
          {running ? <span className="spinner" style={{ width: 12, height: 12, borderWidth: 2 }} /> : hasResult ? 'Re-run' : 'Run'}
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
              id={`include-${query}`}
              checked={included}
              onChange={e => toggle(e.target.checked)}
            />
            <label htmlFor={`include-${query}`} style={{ textTransform: 'none', letterSpacing: 0, color: 'var(--text-muted)', fontSize: 13, fontWeight: 400 }}>
              Include in ticket notes
            </label>
          </div>
        </>
      )}
    </div>
  )
}
