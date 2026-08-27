import { useEffect, useState } from 'react'
import { AlertTriangle, CheckCircle, Clock } from 'lucide-react'

export default function Dashboard() {
    const [stats, setStats] = useState({
        pendingTickets: 0,
        resolvedToday: 0,
        avgResponseTime: "N/A"
    })
    const [recentTickets, setRecentTickets] = useState<any[]>([])

    useEffect(() => {
        const fetchDashboard = async () => {
            try {
                const res = await fetch('http://localhost:8000/api/v1/dashboard')
                if (res.ok) {
                    const data = await res.json()
                    setStats({
                        pendingTickets: data.pending_tickets,
                        resolvedToday: data.resolved_today,
                        avgResponseTime: data.avg_response_time
                    })
                    setRecentTickets(data.recent_tickets)
                }
            } catch (err) {
                console.error("Failed to fetch dashboard", err)
            }
        }
        fetchDashboard()
        const interval = setInterval(fetchDashboard, 10000) // Poll every 10s
        return () => clearInterval(interval)
    }, [])

    return (
        <div className="p-8 max-w-7xl mx-auto">
            <header className="mb-8">
                <h1 className="text-2xl font-bold text-gray-900">Operations Overview</h1>
                <p className="text-gray-500">Welcome back, Admin</p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <StatCard title="Pending Tickets" value={stats.pendingTickets} icon={AlertTriangle} color="text-orange-600" bg="bg-orange-50" />
                <StatCard title="Resolved Today" value={stats.resolvedToday} icon={CheckCircle} color="text-green-600" bg="bg-green-50" />
                <StatCard title="Avg Response" value={stats.avgResponseTime} icon={Clock} color="text-blue-600" bg="bg-blue-50" />
            </div>

            <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center">
                    <h2 className="font-semibold text-gray-900">Recent Incidents</h2>
                    <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">View All</button>
                </div>
                <table className="w-full text-left text-sm">
                    <thead className="bg-gray-50 text-gray-500">
                        <tr>
                            <th className="px-6 py-3 font-medium">Ticket ID</th>
                            <th className="px-6 py-3 font-medium">Title</th>
                            <th className="px-6 py-3 font-medium">Severity</th>
                            <th className="px-6 py-3 font-medium">Status</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {recentTickets.length === 0 ? (
                            <tr><td colSpan={4} className="px-6 py-4 text-center text-gray-400">No tickets found</td></tr>
                        ) : (
                            recentTickets.map(t => (
                                <tr key={t.id} className="hover:bg-gray-50">
                                    <td className="px-6 py-3 font-medium text-gray-900">{t.id.substring(0, 8)}...</td>
                                    <td className="px-6 py-3 text-gray-600">{t.title}</td>
                                    <td className="px-6 py-3">
                                        <span className={`px-2 py-1 rounded text-xs font-medium ${t.severity === 'high' ? 'bg-red-50 text-red-700' :
                                            t.severity === 'medium' ? 'bg-yellow-50 text-yellow-700' : 'bg-blue-50 text-blue-700'
                                            }`}>
                                            {t.severity}
                                        </span>
                                    </td>
                                    <td className="px-6 py-3 text-gray-500">{t.status}</td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    )
}

function StatCard({ title, value, icon: Icon, color, bg }: any) {
    return (
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex items-center space-x-4">
            <div className={`p-3 rounded-lg ${bg} ${color}`}>
                <Icon size={24} />
            </div>
            <div>
                <div className="text-sm text-gray-500 font-medium">{title}</div>
                <div className="text-2xl font-bold text-gray-900">{value}</div>
            </div>
        </div>
    )
}
