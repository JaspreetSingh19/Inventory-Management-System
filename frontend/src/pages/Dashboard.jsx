/** @file Dashboard.jsx */

import { useQuery } from '@tanstack/react-query'
import { getDashboardSummary } from '../api/dashboard'
import { Package, Users, ShoppingCart, AlertTriangle, CheckCircle2, ArrowUpRight } from 'lucide-react'

function StatCard({ label, value, icon: Icon, iconBg, iconColor, hint }) {
  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm hover:shadow-md transition-shadow duration-200">
      <div className="flex items-start justify-between mb-5">
        <div className={`w-11 h-11 ${iconBg} rounded-xl flex items-center justify-center`}>
          <Icon size={20} className={iconColor} strokeWidth={2} />
        </div>
        <ArrowUpRight size={15} className="text-slate-300 mt-0.5" />
      </div>
      <p className="text-3xl font-black text-slate-900 tabular-nums mb-1">{value ?? '—'}</p>
      <p className="text-sm font-semibold text-slate-500">{label}</p>
      {hint && <p className="text-xs text-slate-400 mt-1">{hint}</p>}
    </div>
  )
}

function StockDot({ qty }) {
  if (qty === 0)
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-red-50 text-red-700 ring-1 ring-inset ring-red-200">
        <span className="w-1.5 h-1.5 rounded-full bg-red-500 shrink-0" />
        Out of stock
      </span>
    )
  return (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 ring-1 ring-inset ring-amber-200">
      <span className="w-1.5 h-1.5 rounded-full bg-amber-500 shrink-0" />
      {qty} remaining
    </span>
  )
}

export default function Dashboard() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['dashboard'],
    queryFn: getDashboardSummary,
  })

  if (isLoading) return <Skeleton />
  if (isError)
    return (
      <div className="flex items-center gap-3 bg-red-50 border border-red-200 text-red-700 rounded-2xl p-5">
        <AlertTriangle size={18} className="shrink-0" />
        <p className="text-sm font-semibold">Failed to load dashboard. Check your connection.</p>
      </div>
    )

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Dashboard</h1>
        <p className="text-slate-500 text-sm mt-1">Your inventory and order overview.</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <StatCard label="Total Products" value={data.total_products} icon={Package}
          iconBg="bg-indigo-50" iconColor="text-indigo-600" hint="Items in catalogue" />
        <StatCard label="Total Customers" value={data.total_customers} icon={Users}
          iconBg="bg-emerald-50" iconColor="text-emerald-600" hint="Registered accounts" />
        <StatCard label="Total Orders" value={data.total_orders} icon={ShoppingCart}
          iconBg="bg-violet-50" iconColor="text-violet-600" hint="Orders placed" />
      </div>

      {/* Low stock */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="flex items-center gap-3 px-6 py-4 border-b border-slate-100">
          <div className="w-9 h-9 bg-amber-50 rounded-xl flex items-center justify-center shrink-0">
            <AlertTriangle size={16} className="text-amber-600" strokeWidth={2} />
          </div>
          <div className="flex-1">
            <p className="text-sm font-bold text-slate-900">Low Stock Alert</p>
            <p className="text-xs text-slate-400 mt-0.5">Products with fewer than 10 units</p>
          </div>
          {data.low_stock_products.length > 0 && (
            <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-red-600 text-white">
              {data.low_stock_products.length} item{data.low_stock_products.length !== 1 ? 's' : ''}
            </span>
          )}
        </div>

        {data.low_stock_products.length === 0 ? (
          <div className="flex flex-col items-center py-14 gap-3">
            <div className="w-14 h-14 bg-emerald-50 rounded-2xl flex items-center justify-center">
              <CheckCircle2 size={26} strokeWidth={1.5} className="text-emerald-500" />
            </div>
            <p className="text-sm font-semibold text-slate-600">All products are well stocked</p>
            <p className="text-xs text-slate-400">No action required</p>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-100">
                <th className="px-6 py-3 text-left text-xs font-bold uppercase tracking-wider text-slate-400">Product</th>
                <th className="px-6 py-3 text-left text-xs font-bold uppercase tracking-wider text-slate-400">SKU</th>
                <th className="px-6 py-3 text-left text-xs font-bold uppercase tracking-wider text-slate-400">Stock</th>
              </tr>
            </thead>
            <tbody>
              {data.low_stock_products.map((p) => (
                <tr key={p.id} className="border-b border-slate-100 last:border-0 hover:bg-slate-50/70 transition-colors">
                  <td className="px-6 py-3.5 font-semibold text-slate-900">{p.name}</td>
                  <td className="px-6 py-3.5">
                    <code className="text-xs bg-slate-100 text-slate-600 px-2 py-1 rounded-md font-mono">{p.sku}</code>
                  </td>
                  <td className="px-6 py-3.5"><StockDot qty={p.quantity} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

function Skeleton() {
  return (
    <div className="space-y-8 animate-pulse">
      <div className="space-y-2">
        <div className="h-7 w-36 bg-slate-200 rounded-lg" />
        <div className="h-4 w-56 bg-slate-100 rounded-lg" />
      </div>
      <div className="grid grid-cols-3 gap-5">
        {[0, 1, 2].map((i) => <div key={i} className="h-36 bg-white rounded-2xl border border-slate-200" />)}
      </div>
      <div className="h-64 bg-white rounded-2xl border border-slate-200" />
    </div>
  )
}
