/**
 * @file products.js
 * @description API functions for the `/products` resource.
 *
 * Each function wraps an Axios call and resolves to the parsed response body,
 * making them directly usable as `queryFn` / `mutationFn` values in
 * TanStack Query hooks.
 *
 * @module api/products
 */

import api from './client'

/**
 * Fetch all products, ordered newest first.
 *
 * @returns {Promise<Object[]>} Resolves to an array of product objects.
 */
export const getProducts = () => api.get('/products').then(r => r.data)

/**
 * Fetch a single product by its primary key.
 *
 * @param {number} id - The product's primary key.
 * @returns {Promise<Object>} Resolves to the matching product object.
 */
export const getProduct = (id) => api.get(`/products/${id}`).then(r => r.data)

/**
 * Create a new product.
 *
 * @param {{ name: string, sku: string, price: number, quantity: number }} data
 *   Product fields to create.
 * @returns {Promise<Object>} Resolves to the created product including its
 *   server-assigned `id` and `created_at`.
 */
export const createProduct = (data) => api.post('/products', data).then(r => r.data)

/**
 * Update one or more fields of an existing product.
 *
 * @param {number} id - Primary key of the product to update.
 * @param {Partial<{ name: string, sku: string, price: number, quantity: number }>} data
 *   Only the fields provided will be changed (partial update).
 * @returns {Promise<Object>} Resolves to the updated product object.
 */
export const updateProduct = (id, data) => api.put(`/products/${id}`, data).then(r => r.data)

/**
 * Permanently delete a product.
 *
 * @param {number} id - Primary key of the product to delete.
 * @returns {Promise<void>} Resolves when the server returns HTTP 204.
 */
export const deleteProduct = (id) => api.delete(`/products/${id}`)
