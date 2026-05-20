import { useState, useEffect, createContext, useContext } from 'react'
import { auth as authApi } from './api'
import LoginPage from './pages/LoginPage'
import OrgPickerPage from './pages/OrgPickerPage'
import WizardPage from './pages/WizardPage'

// ── Auth context ─────────────────────────────────────────────────────────────
export const AuthContext = createContext(null)
export const useAuth = () => useContext(AuthContext)

export default function App() {
  const [authState, setAuthState] = useState({
    status: 'loading', // loading | unauthenticated | needs_org | ready
    user: null,
    orgs: [],
    orgId: null,
  })

  useEffect(() => {
    authApi.me()
      .then(data => {
        if (data.org_id) {
          setAuthState({ status: 'ready', user: data.user, orgs: data.orgs, orgId: data.org_id })
        } else if (data.orgs?.length > 0) {
          setAuthState({ status: 'needs_org', user: data.user, orgs: data.orgs, orgId: null })
        } else {
          setAuthState({ status: 'unauthenticated', user: null, orgs: [], orgId: null })
        }
      })
      .catch(() => setAuthState({ status: 'unauthenticated', user: null, orgs: [], orgId: null }))
  }, [])

  const handleLoginSuccess = ({ user, orgs, org_id }) => {
    if (org_id) {
      setAuthState({ status: 'ready', user, orgs, orgId: org_id })
    } else {
      setAuthState({ status: 'needs_org', user, orgs, orgId: null })
    }
  }

  const handleOrgSelect = (orgId) => {
    setAuthState(s => ({ ...s, status: 'ready', orgId }))
  }

  const handleLogout = async () => {
    await authApi.logout().catch(() => {})
    setAuthState({ status: 'unauthenticated', user: null, orgs: [], orgId: null })
  }

  if (authState.status === 'loading') {
    return (
      <div className="page">
        <span className="spinner" style={{ width: 32, height: 32, borderWidth: 3 }} />
      </div>
    )
  }

  return (
    <AuthContext.Provider value={{ ...authState, handleLogout }}>
      {authState.status === 'unauthenticated' && (
        <LoginPage onSuccess={handleLoginSuccess} />
      )}
      {authState.status === 'needs_org' && (
        <OrgPickerPage orgs={authState.orgs} onSelect={handleOrgSelect} />
      )}
      {authState.status === 'ready' && (
        <WizardPage />
      )}
    </AuthContext.Provider>
  )
}
