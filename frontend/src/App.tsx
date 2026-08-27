import { useState } from 'react'
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, MessageSquare, FileText, Upload } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import Chat from './pages/Chat'
import DocsUpload from './pages/DocsUpload'

function NavLink({ to, icon: Icon, children }: any) {
    const location = useLocation();
    const isActive = location.pathname === to;
    return (
        <Link
            to={to}
            className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${isActive ? 'bg-blue-50 text-blue-600' : 'text-gray-600 hover:bg-gray-50'}`}
        >
            <Icon size={20} />
            <span className="font-medium">{children}</span>
        </Link>
    )
}

function Layout({ children }: any) {
    return (
        <div className="flex h-screen bg-gray-50">
            {/* Sidebar */}
            <div className="w-64 bg-white border-r border-gray-200 p-6 flex flex-col">
                <div className="flex items-center space-x-3 mb-10">
                    <div className="h-8 w-8 bg-blue-600 rounded-lg flex items-center justify-center">
                        <span className="text-white font-bold">AO</span>
                    </div>
                    <h1 className="text-xl font-bold text-gray-900">Ops Copilot</h1>
                </div>

                <nav className="space-y-1 flex-1">
                    <NavLink to="/" icon={LayoutDashboard}>Dashboard</NavLink>
                    <NavLink to="/chat" icon={MessageSquare}>Copilot Chat</NavLink>
                    <NavLink to="/upload" icon={Upload}>Upload Docs</NavLink>
                </nav>

                <div className="pt-6 border-t border-gray-100">
                    <div className="flex items-center space-x-3 text-sm text-gray-500">
                        <div className="h-2 w-2 bg-green-500 rounded-full"></div>
                        <span>System Operational</span>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 overflow-auto">
                {children}
            </div>
        </div>
    )
}

function App() {
    return (
        <BrowserRouter>
            <Layout>
                <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/chat" element={<Chat />} />
                    <Route path="/upload" element={<DocsUpload />} />
                </Routes>
            </Layout>
        </BrowserRouter>
    )
}

export default App
