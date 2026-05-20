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
  if (!r.ok) throw new Error(data.detail || `HTTP ${r.status}`)
  return data
}

const get  = (path)        => request('GET',  path)
const post = (path, body)  => request('POST', path, body)

export const auth = {
  login:     (email, password) => post('/auth/login',  { email, password }),
  mfa:       (code, token)     => post('/auth/mfa',    { code, token }),
  selectOrg: (org_id)          => post('/auth/org',    { org_id }),
  me:        ()                => get('/auth/me'),
  logout:    ()                => post('/auth/logout'),
}

export const sites = {
  list: () => get('/sites'),
}

export const clients = {
  wireless: (siteId) => get(`/clients/${siteId}/wireless`),
  wired:    (siteId) => get(`/clients/${siteId}/wired`),
}

export const marvis = {
  query:       (query)       => post('/marvis/query',       { query }),
  suggestions: (params)      => post('/marvis/suggestions', params),
  categories:  ()            => get('/marvis/categories'),
}
