/** @file Orders.jsx */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { Plus, Trash2, Eye, X, ShoppingCart, User, DollarSign, Receipt } from 'lucide-react'
import { getOrders, createOrder, deleteOrder } from '../api/orders'
import { getCustomers } from '../api/customers'
import { getProducts } from '../api/products'
import Modal from '../components/Modal'
import ConfirmDialog from '../components/ConfirmDialog'

const labelCls = 'block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5'

const inputCls = 'w-full bg-white border border-slate-200 rounded-xl py-2.5 pl-10 pr-4 text-sm text-slate-900 focus:outline-none focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all appearance-none'

const AVATAR_COLORS = [
  'bg-indigo-100 text-indigo-700',
  'bg-emerald-100 text-emerald-700',
  'bg-violet-100 text-violet-700',
  'bg-rose-100 text-rose-700',
  'bg-amber-100 text-amber-700',
]

function MiniAvatar({ name }) {
  const initials = name.split(' ').slice(0, 2).map((w) => w[0]?.toUpperCase() ?? '').join('')
  const color = AVATAR_COLORS[name.charCodeAt(0) % AVATAR_COLORS.length]
  return (
    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${color}`}>
      {initials}
    </div>
  )
}

function OrderForm({ onSubmit, onClose, loading, customers, products }) {
  const [customerId, setCustomerId] = useState('')
  const [items, setItems] = useState([{ product_id: '', quantity: 1 }])

  const addItem = () => setItems((i) => [...i, { product_id: '', quantity: 1 }])
  const removeItem = (idx) => setItems((i) => i.filter((_, j) => j !== idx))
  const setItem = (idx, key, val) =>
    setItems((i) => i.map((item, j) => (j === idx ? { ...item, [key]: val } : item)))

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit({
      customer_id: parseInt(customerId, 10),
      items: items.map((it) => ({ product_id: parseInt(it.product_id, 10), quantity: parseInt(it.quantity, 10) })),
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div>
        <label className={labelCls}>Customer</label>
        <div className="relative">
          <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-slate-400">
            <User size={14} strokeWidth={2} />
          </div>
          <select value={customerId} onChange={(e) => setCustomerId(e.target.value)} required className={inputCls}>
            <option value="">Select a customer…</option>
            {customers.map((c) => (
              <option key={c.id} value={c.id}>{c.full_name} — {c.email}</option>
            ))}
          </select>
        </div>
      </div>

      <div>
        <div className="flex items-center justify-between mb-2.5">
          <label className={labelCls}>Order Items</label>
          <button type="button" onClick={addItem}
            className="flex items-center gap-1.5 text-xs font-semibold text-indigo-600 hover:text-indigo-800 transition-colors">
            <Plus size={12} strokeWidth={2.5} /> Add item
          </button>
        </div>
        <div className="space-y-2">
          {items.map((item, idx) => (
            <div key={idx} className="flex gap-2 items-center p-3 bg-slate-50 rounded-xl border border-slate-200">
              <select
                value={item.product_id}
                onChange={(e) => setItem(idx, 'product_id', e.target.value)}
                required
                className="flex-1 bg-white border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition-all"
              >
                <option value="">Select product…</option>
                {products.map((p) => (
                  <option key={p.id} value={p.id}>{p.name} — {p.quantity} in stock</option>
                ))}
              </select>
              <input
                type="number" min="1" value={item.quantity}
                onChange={(e) => setItem(idx, 'quantity', e.target.value)}
                required placeholder="Qty"
                className="w-20 bg-white border border-slate-200 rounded-lg px-3 py-2 text-sm text-center focus:outline-none focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition-all font-semibold"
              />
              {items.length > 1 && (
                <button type="button" onClick={() => removeItem(idx)}
                  className="w-8 h-8 flex items-center justify-center rounded-lg text-slate-400 hover:text-red-500 hover:bg-red-50 transition-colors shrink-0">
                  <X size={14} strokeWidth={2} />
                </button>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="flex justify-end gap-3 pt-4 border-t border-slate-100">
        <button type="button" onClick={onClose}
          className="px-4 py-2.5 text-sm font-semibold rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50 transition-colors">
          Cancel
        </button>
        <button type="submit" disabled={loading}
          className="px-5 py-2.5 text-sm font-semibold rounded-xl bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm shadow-indigo-200 disabled:opacity-50 transition-colors">
          {loading ? 'Placing…' : 'Place Order'}
        </button>
      </div>
    </form>
  )
}

function OrderDetail({ order, onClose }) {
  const total = parseFloat(order.total_amount)
  return (
    <Modal title={`Order #${String(order.id).padStart(4, '0')}`} onClose={onClose} maxWidth="max-w-xl">
      <div className="space-y-5">
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
            <p className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Customer</p>
            <p className="text-sm font-bold text-slate-900">{order.customer.full_name}</p>
            <p className="text-xs text-slate-500 mt-0.5">{order.customer.email}</p>
          </div>
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
            <p className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Date</p>
            <p className="text-sm font-bold text-slate-900">
              {new Date(order.created_at).toLocaleDateString('en-US', { dateStyle: 'long' })}
            </p>
            <p className="text-xs text-slate-500 mt-0.5">{order.items.length} item{order.items.length !== 1 ? 's' : ''}</p>
          </div>
        </div>

        <div className="border border-slate-200 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200">
                <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wider text-slate-400">Product</th>
                <th className="px-4 py-3 text-center text-xs font-bold uppercase tracking-wider text-slate-400">Qty</th>
                <th className="px-4 py-3 text-right text-xs font-bold uppercase tracking-wider text-slate-400">Unit</th>
                <th className="px-4 py-3 text-right text-xs font-bold uppercase tracking-wider text-slate-400">Total</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {order.items.map((item) => (
                <tr key={item.id} className="hover:bg-slate-50/60">
                  <td className="px-4 py-3.5 text-sm font-semibold text-slate-900">{item.product.name}</td>
                  <td className="px-4 py-3.5 text-center">
                    <span className="inline-flex items-center justify-center w-7 h-7 bg-slate-100 rounded-full text-xs font-bold text-slate-700">
                      {item.quantity}
                    </span>
                  </td>
                  <td className="px-4 py-3.5 text-right text-sm text-slate-500">${parseFloat(item.unit_price).toFixed(2)}</td>
                  <td className="px-4 py-3.5 text-right text-sm font-bold text-slate-900">
                    ${(item.quantity * parseFloat(item.unit_price)).toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="flex items-center justify-between bg-slate-900 rounded-xl px-5 py-4">
          <div className="flex items-center gap-2 text-slate-400">
            <Receipt size={15} />
            <span className="text-sm font-semibold text-white">Order Total</span>
          </div>
          <span className="text-xl font-black text-white tabular-nums">${total.toFixed(2)}</span>
        </div>
      </div>
    </Modal>
  )
}

export default function Orders() {
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [viewing, setViewing] = useState(null)
  const [toDelete, setToDelete] = useState(null)

  const { data: orders = [], isLoading } = useQuery({ queryKey: ['orders'], queryFn: getOrders })
  const { data: customers = [] } = useQuery({ queryKey: ['customers'], queryFn: getCustomers })
  const { data: products = [] } = useQuery({ queryKey: ['products'], queryFn: getProducts })

  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ['orders'] })
    qc.invalidateQueries({ queryKey: ['products'] })
    qc.invalidateQueries({ queryKey: ['dashboard'] })
  }

  const createM = useMutation({
    mutationFn: createOrder,
    onSuccess: () => { toast.success('Order placed'); setShowForm(false); invalidate() },
    onError: (e) => toast.error(e.response?.data?.detail || 'Error placing order'),
  })
  const deleteM = useMutation({
    mutationFn: deleteOrder,
    onSuccess: () => { toast.success('Order cancelled'); setToDelete(null); invalidate() },
    onError: (e) => toast.error(e.response?.data?.detail || 'Error cancelling order'),
  })

  const totalRevenue = orders.reduce((s, o) => s + parseFloat(o.total_amount), 0)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Orders</h1>
          <p className="text-slate-500 text-sm mt-1">
            {orders.length} order{orders.length !== 1 ? 's' : ''}
            {orders.length > 0 && (
              <span className="ml-2 text-emerald-600 font-semibold">· ${totalRevenue.toFixed(2)} revenue</span>
            )}
          </p>
        </div>
        <button onClick={() => setShowForm(true)}
          className="flex items-center gap-2 bg-indigo-600 text-white px-5 py-2.5 rounded-xl text-sm font-semibold hover:bg-indigo-700 shadow-sm shadow-indigo-200 transition-colors">
          <Plus size={16} strokeWidth={2.5} /> New Order
        </button>
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="animate-pulse divide-y divide-slate-100">
            {[0, 1, 2, 3].map((i) => (
              <div key={i} className="flex items-center gap-4 px-6 py-4">
                <div className="w-16 h-6 bg-slate-100 rounded-lg" />
                <div className="w-8 h-8 bg-slate-100 rounded-full shrink-0" />
                <div className="flex-1 h-4 bg-slate-100 rounded-md" />
                <div className="w-20 h-6 bg-slate-100 rounded-full" />
                <div className="w-20 h-4 bg-slate-100 rounded-md ml-auto" />
              </div>
            ))}
          </div>
        ) : orders.length === 0 ? (
          <div className="flex flex-col items-center py-20 gap-3 text-center px-4">
            <div className="w-14 h-14 bg-slate-100 rounded-2xl flex items-center justify-center">
              <ShoppingCart size={24} strokeWidth={1.5} className="text-slate-400" />
            </div>
            <p className="text-sm font-bold text-slate-700">No orders yet</p>
            <p className="text-xs text-slate-400">Place your first order to get started.</p>
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-100 bg-slate-50/70">
                <th className="px-6 py-3.5 text-left text-xs font-bold uppercase tracking-wider text-slate-400">Order</th>
                <th className="px-6 py-3.5 text-left text-xs font-bold uppercase tracking-wider text-slate-400">Customer</th>
                <th className="px-6 py-3.5 text-left text-xs font-bold uppercase tracking-wider text-slate-400">Items</th>
                <th className="px-6 py-3.5 text-left text-xs font-bold uppercase tracking-wider text-slate-400">Total</th>
                <th className="px-6 py-3.5 text-left text-xs font-bold uppercase tracking-wider text-slate-400">Date</th>
                <th className="px-6 py-3.5" />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {orders.map((o) => (
                <tr key={o.id} className="hover:bg-slate-50/60 transition-colors">
                  <td className="px-6 py-4">
                    <span className="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-bold bg-slate-900 text-white font-mono tracking-widest">
                      #{String(o.id).padStart(4, '0')}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2.5">
                      <MiniAvatar name={o.customer.full_name} />
                      <span className="text-sm font-semibold text-slate-900">{o.customer.full_name}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 ring-1 ring-inset ring-slate-200">
                      {o.items.length} item{o.items.length !== 1 ? 's' : ''}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-1">
                      <DollarSign size={13} className="text-emerald-600" strokeWidth={2.5} />
                      <span className="text-sm font-black text-slate-900 tabular-nums">{parseFloat(o.total_amount).toFixed(2)}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-500">
                    {new Date(o.created_at).toLocaleDateString('en-US', { dateStyle: 'medium' })}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-1 justify-end">
                      <button onClick={() => setViewing(o)} title="View order"
                        className="h-8 w-8 flex items-center justify-center rounded-lg text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors">
                        <Eye size={13} strokeWidth={2} />
                      </button>
                      <button onClick={() => setToDelete(o)} title="Cancel order"
                        className="h-8 w-8 flex items-center justify-center rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors">
                        <Trash2 size={13} strokeWidth={2} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showForm && (
        <Modal title="Place New Order" onClose={() => setShowForm(false)}>
          <OrderForm onClose={() => setShowForm(false)} onSubmit={createM.mutate} loading={createM.isPending} customers={customers} products={products} />
        </Modal>
      )}
      {viewing && <OrderDetail order={viewing} onClose={() => setViewing(null)} />}
      {toDelete && (
        <ConfirmDialog
          message={`Cancel Order #${String(toDelete.id).padStart(4, '0')}? All stock will be restored.`}
          confirmLabel="Cancel Order"
          onConfirm={() => deleteM.mutate(toDelete.id)}
          onCancel={() => setToDelete(null)}
        />
      )}
    </div>
  )
}
