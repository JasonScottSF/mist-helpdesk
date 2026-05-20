import { useState, useEffect } from 'react'
import { clients as clientsApi } from '../../api'
import SearchList from '../ui/SearchList'

function clientLabel(c) {
  return c.username || c.hostname || c.mac || 'Unknown'
}

function clientSub(c) {
  const parts = []
  if (c.ip)           parts.push(c.ip)
  if (c.ssid)         parts.push(c.ssid)
  if (c.mac)          parts.push(c.mac)
  if (c.os || c.family) parts.push([c.family, c.os].filter(Boolean).join(' '))
  return parts.join(' · ')
}

function clientIcon(c) {
  const os = (c.os || c.family || '').toLowerCase()
  if (os.includes('iphone') || os.includes('ios'))  return '📱'
  if (os.includes('android'))                        return '📱'
  if (os.includes('mac') || os.includes('apple'))    return '💻'
  if (os.includes('window'))                         return '🖥️'
  if (os.includes('linux'))                          return '🖥️'
  if (c.mac)                                         return '🔌'
  return '💻'
}

export default function ClientStep({ wizard, update, onNext, onBack }) {
  const [wireless, setWireless] = useState([])
  const [wired, setWired]       = useState([])
  const [loading, setLoading]   = useState(true)
  const [error, setError]       = useState(null)
  const [tab, setTab]           = useState('wireless')

  useEffect(() => {
    if (!wizard.site) return
    Promise.all([
      clientsApi.wireless(wizard.site.id).then(d => setWireless(d.clients)),
      clientsApi.wired(wizard.site.id).then(d => setWired(d.clients)).catch(() => {}),
    ])
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [wizard.site?.id])

  const items = tab === 'wireless' ? wireless : wired

  return (
    <>
      <div className="question">Which device are we looking at?</div>
      <div className="question-hint">
        Showing clients currently connected at <strong>{wizard.site?.name}</strong>.
        Search by name, username, or MAC.
      </div>

      {error && <div className="alert alert-error"><span>⚠</span> {error}</div>}

      {wizard.client && (
        <div className="alert alert-info" style={{ marginBottom: 16 }}>
          <span>✓</span>
          <div>
            <strong>Selected:</strong> {clientLabel(wizard.client)}
            {wizard.client.ip && <> · {wizard.client.ip}</>}
            {wizard.client.mac && <> · {wizard.client.mac}</>}
          </div>
        </div>
      )}

      <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
        <button
          className={`btn btn-sm ${tab === 'wireless' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setTab('wireless')}
        >
          📶 Wi-Fi ({wireless.length})
        </button>
        <button
          className={`btn btn-sm ${tab === 'wired' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setTab('wired')}
        >
          🔌 Wired ({wired.length})
        </button>
      </div>

      {loading ? (
        <div style={{ padding: 24, textAlign: 'center' }}><span className="spinner" /></div>
      ) : (
        <SearchList
          items={items}
          selected={wizard.client}
          onSelect={c => update({ client: c })}
          renderItem={c => ({
            icon: clientIcon(c),
            main: clientLabel(c),
            sub: clientSub(c),
          })}
          placeholder="Search by name, username, or MAC…"
          getKey={c => c.mac || JSON.stringify(c)}
          filterFn={(c, q) => {
            const s = q.toLowerCase()
            return (
              (c.username || '').toLowerCase().includes(s) ||
              (c.hostname  || '').toLowerCase().includes(s) ||
              (c.mac       || '').toLowerCase().includes(s) ||
              (c.ip        || '').toLowerCase().includes(s)
            )
          }}
        />
      )}

      <div className="nav-row">
        <button className="btn btn-secondary" onClick={onBack}>← Back</button>
        <button className="btn btn-ghost btn-sm" onClick={onNext} style={{ marginRight: 'auto' }}>
          Skip (no specific client)
        </button>
        <button className="btn btn-primary" onClick={onNext} disabled={!wizard.client}>
          Next →
        </button>
      </div>
    </>
  )
}
