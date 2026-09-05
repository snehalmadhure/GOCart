import { Navigate, Route, Routes } from 'react-router-dom'
import { useCallback, useEffect, useState } from 'react'
import { AppLayout } from './components/layout'
import { Toast } from './components/common'
import PantryPage from './pages/PantryPage'
import PurchasesPage from './pages/PurchasesPage'
import RemindersPage from './pages/RemindersPage'
import ShoppingListPage from './pages/ShoppingListPage'

export default function App() {
 const [toast, setToast] = useState(''); const notify = useCallback(message => setToast(message), [])
 useEffect(() => { if (!toast) return; const timeout = setTimeout(() => setToast(''), 4200); return () => clearTimeout(timeout) }, [toast])
 return <AppLayout><Routes><Route path="/" element={<Navigate to="/pantry" replace />} /><Route path="/pantry" element={<PantryPage />} /><Route path="/purchases" element={<PurchasesPage notify={notify} />} /><Route path="/reminders" element={<RemindersPage notify={notify} />} /><Route path="/shopping-list" element={<ShoppingListPage notify={notify} />} /><Route path="*" element={<Navigate to="/pantry" replace />} /></Routes><Toast toast={toast} onClose={() => setToast('')} /></AppLayout>
}
