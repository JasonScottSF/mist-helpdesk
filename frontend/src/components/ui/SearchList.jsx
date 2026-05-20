import { useState } from 'react'

export default function SearchList({
  items,
  selected,
  onSelect,
  renderItem,
  placeholder = 'Search…',
  getKey      = item => item.id || item.mac || JSON.stringify(item),
  filterFn    = (item, q) => JSON.stringify(item).toLowerCase().includes(q.toLowerCase()),
}) {
  const [query, setQuery] = useState('')

  const filtered = query
    ? items.filter(item => filterFn(item, query))
    : items

  return (
    <div>
      <div className="search-wrapper" style={{ marginBottom: 8 }}>
        <span className="search-icon">🔍</span>
        <input
          type="search"
          placeholder={placeholder}
          value={query}
          onChange={e => setQuery(e.target.value)}
        />
      </div>
      <div className="search-list">
        {filtered.length === 0 ? (
          <div className="search-list-empty">
            {query ? `No results for "${query}"` : 'No items found'}
          </div>
        ) : (
          filtered.map(item => {
            const { icon, main, sub } = renderItem(item)
            const key = getKey(item)
            const isSelected = selected && getKey(selected) === key
            return (
              <div
                key={key}
                className={`search-list-item ${isSelected ? 'selected' : ''}`}
                onClick={() => onSelect(item)}
              >
                <span className="sli-icon">{icon}</span>
                <div>
                  <div className="sli-main">{main}</div>
                  {sub && <div className="sli-sub">{sub}</div>}
                </div>
                {isSelected && <span style={{ marginLeft: 'auto', color: 'var(--green)', fontWeight: 700 }}>✓</span>}
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
