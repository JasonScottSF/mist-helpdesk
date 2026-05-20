// Issue categories matching the backend runbooks.py
export const ISSUE_ICONS = {
  cant_connect:     '📶',
  wifi_slow:        '🐌',
  auth_failed:      '🔐',
  connected_no_net: '🔇',
  port_dead:        '🔌',
  poe_issue:        '⚡',
  switch_down:      '🏢',
  site_wide:        '🌐',
  auth_backend:     '🛡️',
  slow_both:        '📉',
  other:            '❓',
}

// Categories that require a specific client to be identified
export const NEEDS_CLIENT = [
  'cant_connect', 'wifi_slow', 'auth_failed', 'connected_no_net', 'port_dead',
]

// Natural timeframe options
export const TIMEFRAMES = [
  { id: 'today',       label: 'Today' },
  { id: 'this morning', label: 'This morning' },
  { id: 'yesterday',   label: 'Yesterday' },
  { id: 'this week',   label: 'This week' },
  { id: 'in the last hour', label: 'Last hour' },
]
