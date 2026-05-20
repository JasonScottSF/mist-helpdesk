const BASE = '/api'

async function request(method, path, body) {
  const opts = {
    method,
    credentials: 'include',
    headers: {},
  }
  if (body !== undefined) {
    opts.headers['Content-Type'] = 'application/json'
    opts.body = JSON.stringify(body)
  }
  const r = await fetch(`${BASE}${path}`, opts)
  const data = await r.json()
  if (!r.ok) {
    const detail = data.detail
    const msg = typeof detail === 'string' ? detail : JSON.stringify(detail) || `HTTP ${r.status}`
    throw new Error(msg)
  }
  return data
}

const get  = (path)        => request('GET',  path)
const post = (path, body)  => request('POST', path, body)

export const auth = {
  clouds:    ()                      => get('/auth/clouds'),
  login:     (email, password, cloud) => post('/auth/login',  { email, password, cloud }),
  mfa:       (code, mfa_token)       => post('/auth/mfa',     { code, mfa_token }),
  selectOrg: (org_id)                => post('/auth/org',     { org_id }),
  me:        ()                      => get('/auth/me'),
  logout:    ()                      => post('/auth/logout'),
}

export const sites = {
  list: () => get('/sites'),
}

export const clients = {
  wireless: (siteId) => get(`/clients/${siteId}/wireless`),
  wired:    (siteId) => get(`/clients/${siteId}/wired`),
}

export const marvis = {
  query:       (query)  => post('/marvis/query',       { query }),
  suggestions: (params) => post('/marvis/suggestions', params),
  categories:  ()       => get('/marvis/categories'),
}
