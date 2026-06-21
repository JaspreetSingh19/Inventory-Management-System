/**
 * @file orders.js
 * @description API functions for the `/orders` resource.
 *
 * Each function wraps an Axios call and resolves to the parsed response body,
 * making them directly usable as `queryFn` / `mutationFn` values in
 * TanStack Query hooks.
 *
 * @module api/orders
 */

import api from './client'

/**
 * Fetch all orders with nested customer and line-item details, newest first.
 *
 * @returns {Promise<Object[]>} Resolves to an array of order objects, each
 *   containing a `customer` object and an `items` array.
 */
export const getOrders = () => api.get('/orders').then(r => r.data)

/**
 * Fetch a single order by its primary key.
 *
 * @param {number} id - The order's primary key.
 * @returns {Promise<Object>} Resolves to the matching order with nested
 *   customer and item details.
 */
export const getOrder = (id) => api.get(`/orders/${id}`).then(r => r.data)

/**
 * Place a new order.
 *
 * The backend validates stock availability, decrements inventory, and
 * calculates `total_amount` automatically.
 *
 * @param {{ customer_id: number, items: Array<{ product_id: number, quantity: number }> }} data
 *   The customer and the list of line items to order.
 * @returns {Promise<Object>} Resolves to the created order with full nested details.
 */
export const createOrder = (data) => api.post('/orders', data).then(r => r.data)

/**
 * Cancel an order and restore the reserved inventory stock.
 *
 * @param {number} id - Primary key of the order to cancel.
 * @returns {Promise<void>} Resolves when the server returns HTTP 204.
 */
export const deleteOrder = (id) => api.delete(`/orders/${id}`)
