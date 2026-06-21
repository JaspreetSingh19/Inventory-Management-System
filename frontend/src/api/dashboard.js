/**
 * @file dashboard.js
 * @description API function for the `/dashboard` resource.
 *
 * @module api/dashboard
 */

import api from './client'

/**
 * Fetch the dashboard summary from the backend.
 *
 * Returns aggregate counts and a list of low-stock products (quantity < 10).
 *
 * @returns {Promise<{
 *   total_products: number,
 *   total_customers: number,
 *   total_orders: number,
 *   low_stock_products: Array<{ id: number, name: string, sku: string, quantity: number }>
 * }>} Resolves to the summary object used by the Dashboard page.
 */
export const getDashboardSummary = () => api.get('/dashboard/summary').then(r => r.data)
