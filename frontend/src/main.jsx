/**
 * @file main.jsx
 * @description React application entry point.
 *
 * Bootstraps the React tree with the following global providers:
 * - **QueryClientProvider** — TanStack Query context for all data-fetching
 *   hooks (`useQuery`, `useMutation`).  Queries are considered fresh for
 *   30 seconds (`staleTime`) and retry once on failure.
 * - **BrowserRouter** — React Router context enabling client-side navigation.
 * - **Toaster** — react-hot-toast notification container rendered at the
 *   top-right of the viewport.
 *
 * The root `<App />` component is wrapped in `<StrictMode>` to surface
 * potential issues during development.
 */

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import './index.css'
import App from './App.jsx'

/**
 * Global TanStack Query client.
 *
 * - `staleTime: 30_000` — cached data is reused for 30 s before a background
 *   refetch is triggered, reducing unnecessary network requests.
 * - `retry: 1` — failed queries are retried once before surfacing an error.
 *
 * @type {QueryClient}
 */
const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 30_000, retry: 1 } },
})

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
        <Toaster position="top-right" />
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>,
)
