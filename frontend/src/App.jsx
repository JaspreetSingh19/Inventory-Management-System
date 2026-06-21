/** @file App.jsx - Root shell: sticky dark sidebar + independently scrolling main area. */

import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import Products from './pages/Products'
import Customers from './pages/Customers'
import Orders from './pages/Orders'

export default function App() {
  return (
    <div className="flex h-screen overflow-hidden bg-slate-100">
      <Navbar />
      <main className="flex-1 overflow-y-auto bg-slate-100">
        <div className="max-w-6xl mx-auto px-8 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/products" element={<Products />} />
            <Route path="/customers" element={<Customers />} />
            <Route path="/orders" element={<Orders />} />
          </Routes>
        </div>
      </main>
    </div>
  )
}
