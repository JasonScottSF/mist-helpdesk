import { useState } from 'react'
import { useAuth } from '../App'
import { NEEDS_CLIENT } from '../runbooks'
import IssueStep from '../components/steps/IssueStep'
import ReporterStep from '../components/steps/ReporterStep'
import SiteStep from '../components/steps/SiteStep'
import ClientStep from '../components/steps/ClientStep'
import InvestigateStep from '../components/steps/InvestigateStep'
import NotesStep from '../components/steps/NotesStep'

const STEP_LABELS = ['Issue', 'Details', 'Site', 'Client', 'Investigate', 'Notes']

// Logical step numbers (client step may be skipped)
const STEP_ISSUE      = 0
const STEP_REPORTER   = 1
const STEP_SITE       = 2
const STEP_CLIENT     = 3
const STEP_INVESTIGATE= 4
const STEP_NOTES      = 5

const INITIAL_WIZARD = {
  category: null,
  description: '',
  reporter: '',
  techName: '',
  timeframe: 'today',
  scope: null,        // 'individual' | 'multiple' | 'site'
  site: null,         // { id, name }
  client: null,       // client object from Mist
  suggestions: [],    // from backend
  escalationGuidance: null,
  queryResults: [],   // [{ label, query, result, included }]
}

export default function WizardPage() {
  const { user, handleLogout } = useAuth()
  const [step, setStep]     = useState(STEP_ISSUE)
  const [wizard, setWizard] = useState(INITIAL_WIZARD)

  const update = (patch) => setWizard(w => ({ ...w, ...patch }))

  const needsClient = wizard.scope === 'individual' && NEEDS_CLIENT.includes(wizard.category?.id)

  const nextStep = () => {
    if (step === STEP_SITE && !needsClient) {
      setStep(STEP_INVESTIGATE)
    } else {
      setStep(s => Math.min(s + 1, STEP_NOTES))
    }
  }

  const prevStep = () => {
    if (step === STEP_INVESTIGATE && !needsClient) {
      setStep(STEP_SITE)
    } else {
      setStep(s => Math.max(s - 1, 0))
    }
  }

  const resetWizard = () => {
    setWizard(INITIAL_WIZARD)
    setStep(STEP_ISSUE)
  }

  // Build visible step labels (hide Client if not needed)
  const visibleSteps = needsClient
    ? STEP_LABELS
    : STEP_LABELS.filter(l => l !== 'Client')

  const visibleStepIndex = () => {
    if (!needsClient && step >= STEP_INVESTIGATE) return step - 1
    return step
  }

  return (
    <div className="wizard-layout">
      {/* Header */}
      <div className="header-bar">
        <span className="logo" style={{ marginBottom: 0, fontSize: 16 }}>📡 Mist Helpdesk</span>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <span className="text-sm text-muted">{user?.email}</span>
          <button className="btn btn-ghost btn-sm" onClick={handleLogout}>Sign out</button>
          {step > STEP_ISSUE && (
            <button className="btn btn-secondary btn-sm" onClick={resetWizard}>New ticket</button>
          )}
        </div>
      </div>

      {/* Progress */}
      <div style={{ padding: '16px 24px 0', maxWidth: 780, margin: '0 auto', width: '100%' }}>
        <ProgressBar steps={visibleSteps} current={visibleStepIndex()} />
      </div>

      {/* Step content */}
      <div className="wizard-body">
        <div className="card card-wide">
          {step === STEP_ISSUE && (
            <IssueStep wizard={wizard} update={update} onNext={nextStep} />
          )}
          {step === STEP_REPORTER && (
            <ReporterStep wizard={wizard} update={update} onNext={nextStep} onBack={prevStep} />
          )}
          {step === STEP_SITE && (
            <SiteStep wizard={wizard} update={update} onNext={nextStep} onBack={prevStep} />
          )}
          {step === STEP_CLIENT && needsClient && (
            <ClientStep wizard={wizard} update={update} onNext={nextStep} onBack={prevStep} />
          )}
          {step === STEP_INVESTIGATE && (
            <InvestigateStep wizard={wizard} update={update} onNext={nextStep} onBack={prevStep} />
          )}
          {step === STEP_NOTES && (
            <NotesStep wizard={wizard} onBack={prevStep} onReset={resetWizard} />
          )}
        </div>
      </div>
    </div>
  )
}

function ProgressBar({ steps, current }) {
  return (
    <div className="progress-bar">
      {steps.map((label, i) => (
        <div key={label} style={{ display: 'flex', alignItems: 'center', flex: i < steps.length - 1 ? '1' : 'none' }}>
          <div className={`progress-step ${i === current ? 'active' : i < current ? 'done' : ''}`}>
            <div className="progress-dot">
              {i < current ? '✓' : i + 1}
            </div>
            <span style={{ display: 'none' }}>{label}</span>
          </div>
          {i < steps.length - 1 && (
            <div className={`progress-line ${i < current ? 'done' : ''}`} />
          )}
        </div>
      ))}
    </div>
  )
}
