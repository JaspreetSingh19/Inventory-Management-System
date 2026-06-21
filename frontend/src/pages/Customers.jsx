/** @file Customers.jsx */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { Plus, Trash2, Users, Mail, Phone, User } from 'lucide-react'
import { getCustomers, createCustomer, deleteCustomer } from '../api/customers'
import Modal from '../components/Modal'
import ConfirmDialog from '../components/ConfirmDialog'

const emptyForm = { full_name: '', email: '', phone: '' }
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

const AVATAR_COLORS = [
  'bg-indigo-100 text-indigo-700',
  'bg-emerald-100 text-emerald-700',
  'bg-violet-100 text-violet-700',
  'bg-rose-100 text-rose-700',
  'bg-amber-100 text-amber-700',
  'bg-sky-100 text-sky-700',
  'bg-pink-100 text-pink-700',
]

function Avatar({ name, size = 'sm' }) {
  const initials = name.split(' ').slice(0, 2).map((w) => w[0]?.toUpperCase() ?? '').join('')
  const color = AVATAR_COLORS[name.charCodeAt(0) % AVATAR_COLORS.length]
  const cls = size === 'lg' ? 'w-10 h-10 text-sm' : 'w-9 h-9 text-xs'
  return (
    <div className={`${cls} ${color} rounded-full flex items-center justify-center font-bold shrink-0`}>
      {initials}
    </div>
  )
}

function CustomerForm({ onSubmit, onClose, loading }) {
  const [form, setForm] = useState(emptyForm)
  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))
  return (
    <form onSubmit={(e) => { e.preventDefault(); onSubmit(form) }} className="space-y-4">
      <div>
        <label className={labelCls}>Full Name</label>
        <IconInput icon={User} type="text" value={form.full_name} onChange={set('full_name')} required placeholder="Jane Doe" />
      </div>
      <div>
        <label className={labelCls}>Email Address</label>
        <IconInput icon={Mail} type="email" value={form.email} onChange={set('email')} required placeholder="jane@example.com" />
      </div>
      <div>
        <label className={labelCls}>Phone Number</label>
        <IconInput icon={Phone} type="tel" value={form.phone} onChange={set('phone')} required placeholder="+1 555 0100" />
      </div>
      <div className="flex justify-end gap-3 pt-4 border-t border-slate-100">
        <button type="button" onClick={onClose}
          className="px-4 py-2.5 text-sm font-semibold rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50 transition-colors">
          Cancel
        </button>
        <button type="submit" disabled={loading}
          className="px-5 py-2.5 text-sm font-semibold rounded-xl bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm shadow-indigo-200 disabled:opacity-50 transition-colors">
          {loading ? 'Saving…' : 'Add Customer'}
        </button>
      </div>
    </form>
  )
}

export default function Customers() {
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [toDelete, setToDelete] = useState(null)

  const { data = [], isLoading } = useQuery({ queryKey: ['customers'], queryFn: getCustomers })
  const invalidate = () => qc.invalidateQueries({ queryKey: ['customers'] })

  const createM = useMutation({
    mutationFn: createCustomer,
    onSuccess: () => { toast.success('Customer added'); setShowForm(false); invalidate() },
    onError: (e) => toast.error(e.response?.data?.detail || 'Error creating customer'),
  })
  const deleteM = useMutation({
    mutationFn: deleteCustomer,
    onSuccess: () => { toast.success('Customer removed'); setToDelete(null); invalidate() },
    onError: (e) => toast.error(e.response?.data?.detail || 'Error deleting customer'),
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Customers</h1>
          <p className="text-slate-500 text-sm mt-1">
            {data.length} registered customer{data.length !== 1 ? 's' : ''}
          </p>
        </div>
        <button onClick={() => setShowForm(true)}
          className="flex items-center gap-2 bg-indigo-600 text-white px-5 py-2.5 rounded-xl text-sm font-semibold hover:bg-indigo-700 shadow-sm shadow-indigo-200 transition-colors">
          <Plus size={16} strokeWidth={2.5} /> Add Customer
        </button>
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="animate-pulse divide-y divide-slate-100">
            {[0, 1, 2, 3].map((i) => (
              <div key={i} className="flex items-center gap-4 px-6 py-4">
                <div className="w-9 h-9 bg-slate-100 rounded-full shrink-0" />
                <div className="flex-1 h-4 bg-slate-100 rounded-md" />
                <div className="w-48 h-4 bg-slate-100 rounded-md" />
                <div className="w-32 h-4 bg-slate-100 rounded-md" />
              </div>
            ))}
          </div>
        ) : data.length === 0 ? (
          <div className="flex flex-col items-center py-20 gap-3 text-center px-4">
            <div className="w-14 h-14 bg-slate-100 rounded-2xl flex items-center justify-center">
              <Users size={24} strokeWidth={1.5} className="text-slate-400" />
            </div>
            <p className="text-sm font-bold text-slate-700">No customers yet</p>
            <p className="text-xs text-slate-400">Add your first customer to get started.</p>
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-100 bg-slate-50/70">
                <th className="px-6 py-3.5 text-left text-xs font-bold uppercase tracking-wider text-slate-400">Customer</th>
                <th className="px-6 py-3.5 text-left text-xs font-bold uppercase tracking-wider text-slate-400">Email</th>
                <th className="px-6 py-3.5 text-left text-xs font-bold uppercase tracking-wider text-slate-400">Phone</th>
                <th className="px-6 py-3.5" />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {data.map((c) => (
                <tr key={c.id} className="hover:bg-slate-50/60 transition-colors group">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <Avatar name={c.full_name} />
                      <span className="text-sm font-semibold text-slate-900">{c.full_name}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <Mail size={13} className="text-slate-400 shrink-0" />
                      <span className="text-sm text-slate-600">{c.email}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <Phone size={13} className="text-slate-400 shrink-0" />
                      <span className="text-sm text-slate-600 font-mono text-xs tracking-wide">{c.phone}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex justify-end">
                      <button onClick={() => setToDelete(c)}
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
        <Modal title="New Customer" onClose={() => setShowForm(false)}>
          <CustomerForm onClose={() => setShowForm(false)} onSubmit={createM.mutate} loading={createM.isPending} />
        </Modal>
      )}
      {toDelete && (
        <ConfirmDialog
          message={`${toDelete.full_name}'s account will be permanently deleted.`}
          onConfirm={() => deleteM.mutate(toDelete.id)}
          onCancel={() => setToDelete(null)}
        />
      )}
    </div>
  )
}
