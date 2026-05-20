export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/v1'
const TOKEN_KEY = 'phlow_access_token'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
}

function buildAuthHeaders(extra = {}) {
  const headers = { ...extra }
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`
  return headers
}

export async function apiFetch(path, options = {}) {
  const isFormData = options.body instanceof FormData
  const headers = { ...(options.headers || {}) }

  if (!isFormData && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json'
  }

  const token = getToken()
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  })

  const text = await res.text()
  const data = text ? JSON.parse(text) : null

  if (!res.ok) {
    throw new Error(data?.detail || 'Request failed')
  }

  return data
}

export async function apiFetchBlob(path, options = {}) {
  const headers = buildAuthHeaders(options.headers || {})
  const res = await fetch(`${API_BASE_URL}${path}`, { ...options, headers })
  if (!res.ok) {
    let detail = 'Request failed'
    try {
      const data = await res.json()
      detail = data?.detail || detail
    } catch (_err) {
      // non-JSON body
    }
    const error = new Error(detail)
    error.status = res.status
    throw error
  }
  return res.blob()
}

export async function apiFetchBlobWithHeaders(path, options = {}) {
  const headers = buildAuthHeaders(options.headers || {})
  const res = await fetch(`${API_BASE_URL}${path}`, { ...options, headers })
  if (!res.ok) {
    let detail = 'Request failed'
    try {
      const data = await res.json()
      detail = data?.detail || detail
    } catch (_err) {
      // non-JSON body
    }
    const error = new Error(detail)
    error.status = res.status
    throw error
  }
  return {
    blob: await res.blob(),
    headers: res.headers,
  }
}

export async function loadAuthorizedObjectUrl(path) {
  const blob = await apiFetchBlob(path)
  return URL.createObjectURL(blob)
}
