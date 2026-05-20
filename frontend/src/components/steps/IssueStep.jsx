import { useState, useEffect } from 'react'
import { marvis as marvisApi } from '../../api'
import { ISSUE_ICONS } from '../../runbooks'

export default function IssueStep({ wizard, update, onNext }) {
  const [categories, setCategories] = useState([])

  useEffect(() => {
    marvisApi.categories().then(d => setCategories(d.categories)).catch(() => {})
  }, [])

  const canNext = wizard.category !== null && wizard.description.trim().length > 0

  return (
    <>
      <div className="question">What's the issue being reported?</div>
      <div className="question-hint">Pick the closest match, then add a brief description.</div>

      <div className="category-grid">
        {categories.map(cat => (
          <button
            key={cat.id}
            className={`category-card ${wizard.category?.id === cat.id ? 'selected' : ''}`}
            onClick={() => update({ category: cat })}
          >
            <div className="cat-icon">{ISSUE_ICONS[cat.id] || '❓'}</div>
            <div className="cat-label">{cat.label}</div>
            <div className="cat-hint">{cat.hint}</div>
          </button>
        ))}
      </div>

      <div className="field">
        <label>Description (in your own words)</label>
        <textarea
          rows={3}
          placeholder="e.g. User says their laptop connects to Wi-Fi but drops every 10 minutes near the 3rd floor conference rooms."
          value={wizard.description}
          onChange={e => update({ description: e.target.value })}
          style={{ resize: 'vertical' }}
        />
      </div>

      <div className="nav-row" style={{ borderTop: 'none', marginTop: 0, paddingTop: 0 }}>
        <button className="btn btn-primary" onClick={onNext} disabled={!canNext}>
          Next →
        </button>
      </div>
    </>
  )
}
