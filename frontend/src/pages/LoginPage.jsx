import { useState } from 'react'
import { auth as authApi } from '../api'

export default function LoginPage({ onSuccess }) {
  const [email, setEmail]         = useState('')
  const [password, setPassword]   = useState('')
  const [mfaCode, setMfaCode]     = useState('')
  const [mfaToken, setMfaToken]   = useState(null)
  const [loading, setLoading]     = useState(false)
  const [error, setError]         = useState(null)

  const handleLogin = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const data = await authApi.login(email, password)
      if (data.mfa_required) {
        setMfaToken(data.mfa_token)
      } else {
        onSuccess({ user: data.user, orgs: data.orgs, org_id: data.org_id })
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleMfa = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const data = await authApi.mfa(mfaCode, mfaToken)
      onSuccess({ user: data.user, orgs: data.orgs, org_id: data.org_id })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <div className="card">
        <div className="logo">📡 Mist Helpdesk</div>
        <div className="logo-sub">Tier 1 / 2 Troubleshooting Tool</div>

        {error && (
          <div className="alert alert-error">
            <span>⚠</span> {error}
          </div>
        )}

        {!mfaToken ? (
          <form onSubmit={handleLogin}>
            <div className="field">
              <label>Mist Email</label>
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="you@company.com"
                required
                autoFocus
              />
            </div>
            <div className="field">
              <label>Password</label>
              <input
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>
            <button className="btn btn-primary btn-full" type="submit" disabled={loading}>
              {loading ? <><span className="spinner" /> Signing in…</> : 'Sign in with Mist'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleMfa}>
            <p style={{ marginBottom: 20 }}>
              Two-factor authentication is required. Enter your verification code.
            </p>
            <div className="field">
              <label>Verification Code</label>
              <input
                type="text"
                value={mfaCode}
                onChange={e => setMfaCode(e.target.value)}
                placeholder="123456"
                maxLength={8}
                autoFocus
                required
              />
            </div>
            <div style={{ display: 'flex', gap: 10 }}>
              <button
                className="btn btn-secondary"
                type="button"
                onClick={() => { setMfaToken(null); setMfaCode(''); setError(null) }}
              >
                Back
              </button>
              <button className="btn btn-primary" type="submit" disabled={loading} style={{ flex: 1 }}>
                {loading ? <><span className="spinner" /> Verifying…</> : 'Verify'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}
