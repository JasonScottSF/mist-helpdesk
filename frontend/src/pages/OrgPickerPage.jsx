import { useState } from 'react'
import { auth as authApi } from '../api'

export default function OrgPickerPage({ orgs, onSelect }) {
  const [loading, setLoading] = useState(null)
  const [error, setError]     = useState(null)

  const pick = async (orgId) => {
    setError(null)
    setLoading(orgId)
    try {
      await authApi.selectOrg(orgId)
      onSelect(orgId)
    } catch (err) {
      setError(err.message)
      setLoading(null)
    }
  }

  return (
    <div className="page">
      <div className="card">
        <div className="logo">📡 Mist Helpdesk</div>
        <div className="logo-sub">Select an organisation to continue</div>

        {error && (
          <div className="alert alert-error">
            <span>⚠</span> {error}
          </div>
        )}

        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {orgs.map(org => (
            <button
              key={org.id}
              className="search-list-item"
              style={{ border: '1.5px solid var(--border)', borderRadius: 8, cursor: 'pointer', background: 'var(--card)', width: '100%', textAlign: 'left' }}
              onClick={() => pick(org.id)}
              disabled={loading !== null}
            >
              <span className="sli-icon">🏢</span>
              <div>
                <div className="sli-main">{org.name}</div>
                <div className="sli-sub">{org.id}</div>
              </div>
              {loading === org.id && <span className="spinner" style={{ marginLeft: 'auto' }} />}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
