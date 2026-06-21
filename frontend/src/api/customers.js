/**
 * @file customers.js
 * @description API functions for the `/customers` resource.
 *
 * Each function wraps an Axios call and resolves to the parsed response body,
 * making them directly usable as `queryFn` / `mutationFn` values in
 * TanStack Query hooks.
 *
 * @module api/customers
 */

import api from './client'

/**
 * Fetch all customers, ordered newest first.
 *
 * @returns {Promise<Object[]>} Resolves to an array of customer objects.
 */
export const getCustomers = () => api.get('/customers').then(r => r.data)

/**
 * Fetch a single customer by their primary key.
 *
 * @param {number} id - The customer's primary key.
 * @returns {Promise<Object>} Resolves to the matching customer object.
 */
export const getCustomer = (id) => api.get(`/customers/${id}`).then(r => r.data)

/**
 * Register a new customer.
 *
 * @param {{ full_name: string, email: string, phone: string }} data
 *   Customer fields to create.
 * @returns {Promise<Object>} Resolves to the created customer including its
 *   server-assigned `id` and `created_at`.
 */
export const createCustomer = (data) => api.post('/customers', data).then(r => r.data)

/**
 * Permanently delete a customer record.
 *
 * @param {number} id - Primary key of the customer to delete.
 * @returns {Promise<void>} Resolves when the server returns HTTP 204.
 */
export const deleteCustomer = (id) => api.delete(`/customers/${id}`)
