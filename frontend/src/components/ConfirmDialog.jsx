/** @file ConfirmDialog.jsx - Destructive-action confirm dialog with warning icon and blur backdrop. */

import { AlertTriangle } from 'lucide-react'

export default function ConfirmDialog({ message, onConfirm, onCancel, confirmLabel = 'Delete' }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm overflow-hidden">
        {/* Warning header strip */}
        <div className="h-1.5 bg-gradient-to-r from-red-500 to-rose-600" />

        <div className="p-6">
          <div className="flex items-start gap-4 mb-6">
            <div className="w-11 h-11 bg-red-100 rounded-full flex items-center justify-center shrink-0 mt-0.5">
              <AlertTriangle size={20} className="text-red-600" strokeWidth={2.2} />
            </div>
            <div>
              <p className="font-bold text-slate-900 mb-1.5">Are you sure?</p>
              <p className="text-sm text-slate-500 leading-relaxed">{message}</p>
            </div>
          </div>

          <div className="flex justify-end gap-3">
            <button
              onClick={onCancel}
              className="px-4 py-2.5 text-sm font-medium rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50 hover:border-slate-300 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={onConfirm}
              className="px-5 py-2.5 text-sm font-medium rounded-xl bg-red-600 text-white hover:bg-red-700 shadow-sm shadow-red-200/80 transition-colors"
            >
              {confirmLabel}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
