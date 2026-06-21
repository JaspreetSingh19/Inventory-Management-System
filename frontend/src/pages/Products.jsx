/** @file Products.jsx */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { Plus, Pencil, Trash2, Package, Tag, Hash, DollarSign } from 'lucide-react'
import { getProducts, createProduct, updateProduct, deleteProduct } from '../api/products'
import Modal from '../components/Modal'
import ConfirmDialog from '../components/ConfirmDialog'

const emptyForm = { name: '', sku: '', price: '', quantity: '' }

const labelCls = 'block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5'

function IconInput({ icon: Icon, ...props }) {
  return (
    <div className="relative">
      <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-slate-400">
        <Icon size={14} strokeWidth={2} />
      </div>
      <input
        {...props}
        className="w-full bg-white border border-slate-200 rounded-xl py-2.5 pl-10 pr-4 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all"
      />
    </div>
  )
}

function ProductForm({ initial = emptyForm, onSubmit, onClose, loading }) {
  const [form, setForm] = useState(initial)
  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))
  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit({ ...form, price: parseFloat(form.price), quantity: parseInt(form.quantity, 10) })
  }
  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className={labelCls}>Product Name</label>
        <IconInput icon={Tag} type="text" value={form.name} onChange={set('name')} required placeholder="e.g. Widget Pro" />
      </div>
      <div>
        <label className={labelCls}>SKU / Code</label>
        <IconInput icon={Hash} type="text" value={form.sku} onChange={set('sku')} required placeholder="e.g. WGT-001" />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className={labelCls}>Price ($)</label>
          <IconInput icon={DollarSign} type="number" step="0.01" min="0" value={form.price} onChange={set('price')} required placeholder="0.00" />
        </div>
        <div>
          <label className={labelCls}>Quantity</label>
          <IconInput icon={Package} type="number" min="0" value={form.quantity} onChange={set('quantity')} required placeholder="0" />
        </div>
      </div>
      <div className="flex justify-end gap-3 pt-4 border-t border-slate-100">
        <button type="button" onClick={onClose}
          className="px-4 py-2.5 text-sm font-semibold rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50 transition-colors">
          Cancel
        </button>
        <button type="submit" disabled={loading}
          className="px-5 py-2.5 text-sm font-semibold rounded-xl bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm shadow-indigo-200 disabled:opacity-50 transition-colors">
          {loading ? 'Saving…' : 'Save Product'}
        </button>
      </div>
    </form>
  )
}

function StockBadge({ qty }) {
  if (qty === 0)
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-red-50 text-red-700 ring-1 ring-inset ring-red-200">
        <span className="w-1.5 h-1.5 rounded-full bg-red-500 shrink-0" />Out of stock
      </span>
    )
  if (qty < 10)
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 ring-1 ring-inset ring-amber-200">
        <span className="w-1.5 h-1.5 rounded-full bg-amber-500 shrink-0" />{qty} units
      </span>
    )
  return (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 ring-1 ring-inset ring-emerald-200">
      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0" />{qty} units
    </span>
  )
}

export default function Products() {
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState(null)
  const [toDelete, setToDelete] = useState(null)

  const { data = [], isLoading } = useQuery({ queryKey: ['products'], queryFn: getProducts })
  const invalidate = () => qc.invalidateQueries({ queryKey: ['products'] })

  const createM = useMutation({
    mutationFn: createProduct,
    onSuccess: () => { toast.success('Product created'); setShowForm(false); invalidate() },
    onError: (e) => toast.error(e.response?.data?.detail || 'Error creating product'),
  })
  const updateM = useMutation({
    mutationFn: ({ id, data }) => updateProduct(id, data),
    onSuccess: () => { toast.success('Product updated'); setEditing(null); invalidate() },
    onError: (e) => toast.error(e.response?.data?.detail || 'Error updating product'),
  })
  const deleteM = useMutation({
    mutationFn: deleteProduct,
    onSuccess: () => { toast.success('Product deleted'); setToDelete(null); invalidate() },
    onError: (e) => toast.error(e.response?.data?.detail || 'Error deleting product'),
  })

  const lowCount = data.filter((p) => p.quantity < 10).length

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Products</h1>
          <p className="text-slate-500 text-sm mt-1">
            {data.length} item{data.length !== 1 ? 's' : ''} in catalogue
            {lowCount > 0 && <span className="ml-2 text-amber-600 font-medium">· {lowCount} low stock</span>}
          </p>
        </div>
        <button onClick={() => setShowForm(true)}
          className="flex items-center gap-2 bg-indigo-600 text-white px-5 py-2.5 rounded-xl text-sm font-semibold hover:bg-indigo-700 shadow-sm shadow-indigo-200 transition-colors">
          <Plus size={16} strokeWidth={2.5} /> Add Product
        </button>
      </div>

      {/* Table card */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
        {isLoading ? <TableSkeleton /> : data.length === 0 ? (
          <EmptyState icon={Package} title="No products yet" sub="Add your first product to start managing your catalogue." />
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-100 bg-slate-50/70">
                <th className="px-6 py-3.5 text-left text-xs font-bold uppercase tracking-wider text-slate-400">Name</th>
                <th className="px-6 py-3.5 text-left text-xs font-bold uppercase tracking-wider text-slate-400">SKU</th>
                <th className="px-6 py-3.5 text-left text-xs font-bold uppercase tracking-wider text-slate-400">Price</th>
                <th className="px-6 py-3.5 text-left text-xs font-bold uppercase tracking-wider text-slate-400">Stock</th>
                <th className="px-6 py-3.5" />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {data.map((p) => (
                <tr key={p.id} className="hover:bg-slate-50/60 transition-colors group">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-slate-100 rounded-lg flex items-center justify-center shrink-0">
                        <Package size={14} className="text-slate-500" strokeWidth={1.8} />
                      </div>
                      <span className="text-sm font-semibold text-slate-900">{p.name}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <code className="text-xs bg-slate-100 text-slate-600 px-2 py-1 rounded-md font-mono tracking-wide">{p.sku}</code>
                  </td>
                  <td className="px-6 py-4 text-sm font-bold text-slate-800">${parseFloat(p.price).toFixed(2)}</td>
                  <td className="px-6 py-4"><StockBadge qty={p.quantity} /></td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-1 justify-end">
                      <button onClick={() => setEditing(p)}
                        className="h-8 w-8 flex items-center justify-center rounded-lg text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors">
                        <Pencil size={13} strokeWidth={2} />
                      </button>
                      <button onClick={() => setToDelete(p)}
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
        <Modal title="New Product" onClose={() => setShowForm(false)}>
          <ProductForm onClose={() => setShowForm(false)} onSubmit={createM.mutate} loading={createM.isPending} />
        </Modal>
      )}
      {editing && (
        <Modal title="Edit Product" onClose={() => setEditing(null)}>
          <ProductForm
            initial={{ name: editing.name, sku: editing.sku, price: editing.price, quantity: editing.quantity }}
            onClose={() => setEditing(null)}
            onSubmit={(data) => updateM.mutate({ id: editing.id, data })}
            loading={updateM.isPending}
          />
        </Modal>
      )}
      {toDelete && (
        <ConfirmDialog
          message={`"${toDelete.name}" will be permanently removed from your catalogue.`}
          onConfirm={() => deleteM.mutate(toDelete.id)}
          onCancel={() => setToDelete(null)}
        />
      )}
    </div>
  )
}

function EmptyState({ icon: Icon, title, sub }) {
  return (
    <div className="flex flex-col items-center py-20 gap-3 text-center px-4">
      <div className="w-14 h-14 bg-slate-100 rounded-2xl flex items-center justify-center">
        <Icon size={24} strokeWidth={1.5} className="text-slate-400" />
      </div>
      <p className="text-sm font-bold text-slate-700">{title}</p>
      <p className="text-xs text-slate-400 max-w-xs">{sub}</p>
    </div>
  )
}

function TableSkeleton() {
  return (
    <div className="animate-pulse divide-y divide-slate-100">
      {[0, 1, 2, 3, 4].map((i) => (
        <div key={i} className="flex items-center gap-4 px-6 py-4">
          <div className="w-8 h-8 bg-slate-100 rounded-lg shrink-0" />
          <div className="flex-1 h-4 bg-slate-100 rounded-md" />
          <div className="w-20 h-6 bg-slate-100 rounded-md" />
          <div className="w-16 h-4 bg-slate-100 rounded-md" />
          <div className="w-24 h-6 bg-slate-100 rounded-full ml-auto" />
        </div>
      ))}
    </div>
  )
}
