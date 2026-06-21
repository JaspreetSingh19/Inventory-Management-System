/**
 * @file client.js
 * @description Configured Axios instance shared by all API modules.
 *
 * The base URL is resolved from the `VITE_API_URL` environment variable at
 * build time, falling back to `http://localhost:8000` for local development.
 * All API functions in the `api/` directory import this instance so that the
 * backend URL is configured in exactly one place.
 *
 * @module api/client
 */

import axios from 'axios'

/**
 * Pre-configured Axios instance for the Inventory & Order Management API.
 *
 * @type {import('axios').AxiosInstance}
 *
 * @example
 * import api from './client'
 * const products = await api.get('/products').then(r => r.data)
 */
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
})

export default api
