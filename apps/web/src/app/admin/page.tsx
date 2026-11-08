'use client'

import { useState } from 'react'
import Link from 'next/link'
import { format, subDays, startOfDay, endOfDay, startOfWeek, endOfWeek, startOfMonth, endOfMonth, addDays, isToday, isTomorrow } from 'date-fns'
import { ArrowRight, TrendingUp, TrendingDown, Minus, Calendar, Users, DollarSign, MessageSquare, Clock, AlertTriangle, CheckCircle, XCircle, Loader2, BarChart3, Download, Filter, RefreshCw } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'

// Types
interface MetricCard {
  label: string
  value: string | number
  change?: number
  changeLabel?: string
  icon: React.ReactNode
  color: string
  href?: string
}

interface TimeGrain {
  value: 'today' | 'tomorrow' | '7d' | '30d' | '90d' | 'custom'
  label: string
}

const timeGrains: TimeGrain[] = [
  { value: 'today', label: 'Today' },
  { value: 'tomorrow', label: 'Tomorrow' },
  { value: '7d', label: '7 Days' },
  { value: '30d', label: '30 Days' },
  { value: '90d', label: '90 Days' },
  { value: 'custom', label: 'Custom' },
]

// Mock data - in real app this would come from API
const mockMetrics = {
  today: {
    leads: { new: 3, qualified: 2, unresponded: 1 },
    quotes: { pending: 1, sent: 2, expiring: 1, avgValue: '₹45,000' },
    bookings: { confirmed: 2, pending: 1, completed: 1, utilization: '65%' },
    revenue: { collected: '₹85,000', pipeline: '₹4,50,000', projected: '₹12,00,000' },
    conversations: { unread: 2, overdue: 1, botEscalations: 0, avgResponse: '12 min' },
    channels: { instagram: 2, website: 1, whatsapp: 0, youtube: 0 },
  },
  tomorrow: {
    shoots: 1,
    prepTasks: 2,
    confirmationsNeeded: 1,
  },
  week: {
    pipelineValue: '₹4,50,000',
    utilization: '65%',
    leadsBySource: { instagram: 12, website: 8, whatsapp: 5, referral: 3 },
  },
  month: {
    leadsNew: 47,
    leadsQualified: 31,
    quotesSent: 18,
    bookingsConfirmed: 12,
    revenueCollected: '₹8,90,000',
    conversionRate: '25.5%',
    cac: '₹1,850',
    ltv: '₹1,56,000',
    trends: { leads: 12.3, revenue: 8.7, conversion: -2.1 },
  },
}

export default function AdminDashboard() {
  const [timeGrain, setTimeGrain] = useState<'today' | 'tomorrow' | '7d' | '30d' | '90d' | 'custom'>('today')
  const [isLoading, setIsLoading] = useState(false)

  const refreshData = async () => {
    setIsLoading(true)
    await new Promise(r => setTimeout(r, 500))
    setIsLoading(false)
  }

  const getMetricCards = () => {
    const m = mockMetrics[timeGrain as keyof typeof mockMetrics] as any
    if (!m) return []

    switch (timeGrain) {
      case 'today':
        return [
          { label: 'New Leads', value: m.leads.new, change: 12, icon: Users, color: 'bg-blue-500', href: '/admin/leads?filter=today' },
          { label: 'Qualified', value: m.leads.qualified, change: 8, icon: CheckCircle, color: 'bg-green-500' },
          { label: 'Unresponded (>2h)', value: m.leads.unresponded, change: -5, icon: Clock, color: 'bg-red-500', href: '/admin/leads?filter=unresponded' },
          { label: 'Quotes Pending', value: m.quotes.pending, icon: DollarSign, color: 'bg-yellow-500', href: '/admin/quotes?status=pending' },
          { label: 'Quotes Sent', value: m.quotes.sent, change: 15, icon: ArrowRight, color: 'bg-blue-500' },
          { label: 'Expiring Today', value: m.quotes.expiring, icon: AlertTriangle, color: 'bg-orange-500' },
          { label: 'Confirmed Shoots', value: m.bookings.confirmed, change: 10, icon: Calendar, color: 'bg-green-500', href: '/admin/bookings?date=today' },
          { label: 'Revenue Collected', value: m.revenue.collected, change: 22, icon: DollarSign, color: 'bg-emerald-500' },
          { label: 'Pipeline Value', value: m.revenue.pipeline, change: 5, icon: TrendingUp, color: 'bg-purple-500' },
          { label: 'Unread Messages', value: m.conversations.unread, change: -3, icon: MessageSquare, color: 'bg-pink-500', href: '/admin/conversations?filter=unread' },
          { label: 'Overdue Followups', value: m.conversations.overdue, icon: Clock, color: 'bg-red-500' },
          { label: 'Avg Response', value: m.conversations.avgResponse, change: -8, icon: Clock, color: 'bg-gray-500' },
        ]
      case 'tomorrow':
        return [
          { label: 'Shoots Tomorrow', value: m.shoots, icon: Calendar, color: 'bg-blue-500' },
          { label: 'Prep Tasks', value: m.prepTasks, icon: CheckCircle, color: 'bg-yellow-500' },
          { label: 'Confirmations Needed', value: m.confirmationsNeeded, icon: AlertTriangle, color: 'bg-red-500' },
        ]
      case '7d':
        return [
          { label: 'Week Pipeline', value: m.pipelineValue, change: 8, icon: TrendingUp, color: 'bg-purple-500' },
          { label: 'Utilization', value: m.utilization, change: 3, icon: BarChart3, color: 'bg-blue-500' },
          { label: 'Instagram Leads', value: m.leadsBySource.instagram, change: 15, icon: Users, color: 'bg-pink-500' },
          { label: 'Website Leads', value: m.leadsBySource.website, change: 5, icon: Globe, color: 'bg-blue-500' },
          { label: 'WhatsApp Leads', value: m.leadsBySource.whatsapp, change: 20, icon: MessageSquare, color: 'bg-green-500' },
          { label: 'Referral Leads', value: m.leadsBySource.referral, change: -10, icon: Users, color: 'bg-orange-500' },
        ]
      case '30d':
      case '90d':
        return [
          { label: 'New Leads', value: m.leadsNew, change: m.trends.leads, icon: Users, color: 'bg-blue-500' },
          { label: 'Qualified Leads', value: m.leadsQualified, change: 8, icon: CheckCircle, color: 'bg-green-500' },
          { label: 'Quotes Sent', value: m.quotesSent, change: 12, icon: DollarSign, color: 'bg-yellow-500' },
          { label: 'Bookings', value: m.bookingsConfirmed, change: 15, icon: Calendar, color: 'bg-purple-500' },
          { label: 'Revenue', value: m.revenueCollected, change: m.trends.revenue, icon: TrendingUp, color: 'bg-emerald-500' },
          { label: 'Conversion', value: m.conversionRate, change: m.trends.conversion, icon: BarChart3, color: 'bg-orange-500' },
          { label: 'CAC', value: m.cac, change: -5, icon: DollarSign, color: 'bg-red-500' },
          { label: 'LTV', value: m.ltv, change: 8, icon: TrendingUp, color: 'bg-green-500' },
        ]
      default:
        return []
    }
  }

  const MetricCardComponent = ({ metric }: { metric: MetricCard & { change?: number } }) => (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-500 truncate">{metric.label}</p>
            <div className="flex items-baseline gap-2 mt-1">
              <p className="text-2xl font-bold text-gray-900">{metric.value}</p>
              {metric.change !== undefined && (
                <span className={`flex items-center gap-1 text-sm font-medium ${metric.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {metric.change >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                  <span>{Math.abs(metric.change)}%</span>
                </span>
              )}
            </div>
          </div>
          <div className={`p-3 rounded-xl ${metric.color}`}>
            {metric.icon}
          </div>
        </div>
        {metric.href && (
          <Link
            href={metric.href}
            className="mt-4 block text-sm font-medium text-pink-600 hover:text-pink-700 flex items-center gap-1"
          >
            View details
            <ArrowRight className="w-4 h-4" />
          </Link>
        )}
      </CardContent>
    </Card>
  )

  // Today/Tomorrow specific content
  const renderTodayView = () => (
    <div className="space-y-6">
      {/* Today's Shoots */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Calendar className="w-5 h-5 text-pink-500" />
            Today's Shoots
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-pink-500 to-red-500 flex items-center justify-center text-white font-bold">MP</div>
                <div>
                  <p className="font-medium">Priya Sharma - Full Marriage</p>
                  <p className="text-sm text-gray-500">Farmhouse X, Shamirpet • 9:00 AM - 5:00 PM</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="secondary">Ramu + Venkatesh</Badge>
                <Badge variant="default">Confirmed</Badge>
              </div>
            </div>
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-bold">RS</div>
                <div>
                  <p className="font-medium">Rajesh & Sunita - Maternity</p>
                  <p className="text-sm text-gray-500">Studio Main • 11:00 AM - 1:00 PM</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="secondary">Ramu</Badge>
                <Badge variant="default">Confirmed</Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <Link href="/admin/leads/new" className="p-4 border border-gray-200 rounded-lg hover:border-pink-300 hover:bg-pink-50 transition-colors text-center">
              <Users className="w-6 h-6 text-pink-500 mx-auto mb-2" />
              <p className="text-sm font-medium">New Lead</p>
            </Link>
            <Link href="/admin/quotes/new" className="p-4 border border-gray-200 rounded-lg hover:border-pink-300 hover:bg-pink-50 transition-colors text-center">
              <DollarSign className="w-6 h-6 text-pink-500 mx-auto mb-2" />
              <p className="text-sm font-medium">Create Quote</p>
            </Link>
            <Link href="/admin/bookings/new" className="p-4 border border-gray-200 rounded-lg hover:border-pink-300 hover:bg-pink-50 transition-colors text-center">
              <Calendar className="w-6 h-6 text-pink-500 mx-auto mb-2" />
              <p className="text-sm font-medium">Schedule Shoot</p>
            </Link>
            <Link href="/admin/conversations" className="p-4 border border-gray-200 rounded-lg hover:border-pink-300 hover:bg-pink-50 transition-colors text-center">
              <MessageSquare className="w-6 h-6 text-pink-500 mx-auto mb-2" />
              <p className="text-sm font-medium">Conversations</p>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )

  const renderTomorrowView = () => (
    <div className="space-y-6">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Calendar className="w-5 h-5 text-blue-500" />
            Tomorrow's Schedule
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="p-4 bg-blue-50 border-l-4 border-blue-500 rounded-r-lg">
              <p className="font-medium">Anjali & Rohit - Baby Shower</p>
              <p className="text-sm text-gray-500">10:00 AM - 2:00 PM • Adithya assigned</p>
              <p className="text-sm text-gray-500 mt-1">Prep: Props, backdrop, lighting check</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Prep Tasks</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              <li className="flex items-center gap-2 text-sm"><CheckCircle className="w-4 h-4 text-green-500" /> Charge all batteries</li>
              <li className="flex items-center gap-2 text-sm"><CheckCircle className="w-4 h-4 text-green-500" /> Format memory cards</li>
              <li className="flex items-center gap-2 text-sm"><Clock className="w-4 h-4 text-yellow-500" /> Pack backup lighting kit</li>
              <li className="flex items-center gap-2 text-sm"><Clock className="w-4 h-4 text-yellow-500" /> Confirm venue address with client</li>
            </ul>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Client Confirmations Needed</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              <li className="flex items-center gap-2 text-sm">
                <AlertTriangle className="w-4 h-4 text-yellow-500" />
                Anjali - Final timeline approval
              </li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  )

  const renderWeekView = () => (
    <div className="space-y-6">
      {/* Calendar Heatmap */}
      <Card>
        <CardHeader>
          <CardTitle>This Week's Calendar</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-7 gap-1">
            {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, i) => (
              <div key={day} className="text-center text-xs font-medium text-gray-500 pb-2">{day}</div>
            ))}
            {/* Empty cells for days before 1st */}
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={`empty-${i}`} className="aspect-square" />
            ))}
            {/* Days 1-7 */}
            {Array.from({ length: 7 }).map((_, i) => {
              const day = i + 1
              const hasBooking = [1, 3, 5].includes(day)
              const hasMultiple = day === 5
              return (
                <div
                  key={day}
                  className={`aspect-square rounded-lg flex items-center justify-center text-sm font-medium ${
                    hasBooking
                      ? hasMultiple
                        ? 'bg-pink-500 text-white'
                        : 'bg-pink-100 text-pink-700'
                      : 'bg-gray-50 text-gray-400'
                  }`}
                >
                  {day}
                </div>
              )
            })}
          </div>
          <div className="mt-4 flex items-center gap-4 text-sm text-gray-500">
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-pink-500" /> Booking</span>
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-pink-100" /> Multiple</span>
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-gray-50" /> Free</span>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Pipeline Value</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-purple-600">₹4,50,000</p>
            <p className="text-sm text-green-600">+8% vs last week</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Utilization</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-blue-600">65%</p>
            <p className="text-sm text-green-600">+3% vs last week</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Leads This Week</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-pink-600">28</p>
            <p className="text-sm text-gray-500">Instagram: 12 • Web: 8 • WA: 5 • Ref: 3</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )

  const renderMonthView = () => (
    <div className="space-y-6">
      {/* Trend Charts would go here - using recharts in real implementation */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {getMetricCards().map((metric, i) => (
          <MetricCardComponent key={i} metric={metric as any} />
        ))}
      </div>

      {/* Trends Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            Monthly Trends
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-6">
            <div>
              <p className="text-sm text-gray-500">Leads (MoM)</p>
              <p className="text-2xl font-bold text-green-600 flex items-center gap-1">
                <TrendingUp className="w-5 h-5" /> +12.3%
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Revenue (MoM)</p>
              <p className="text-2xl font-bold text-green-600 flex items-center gap-1">
                <TrendingUp className="w-5 h-5" /> +8.7%
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Conversion (MoM)</p>
              <p className="text-2xl font-bold text-red-600 flex items-center gap-1">
                <TrendingDown className="w-5 h-5" /> -2.1%
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500">
            {timeGrain === 'today' && "Today's operational overview"}
            {timeGrain === 'tomorrow' && "Tomorrow's preparation view"}
            {timeGrain === '7d' && 'This week\'s tactical snapshot'}
            {timeGrain === '30d' && 'This month\'s strategic metrics'}
            {timeGrain === '90d' && 'Quarterly performance trends'}
            {timeGrain === 'custom' && 'Custom date range'}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Select value={timeGrain} onValueChange={setTimeGrain}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Time" />
            </SelectTrigger>
            <SelectContent>
              {timeGrains.map((g) => (
                <SelectItem key={g.value} value={g.value}>{g.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button variant="outline" size="sm" onClick={refreshData} disabled={isLoading}>
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </Button>
          <Button variant="outline" size="sm">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 mb-6">
        {getMetricCards().map((metric, i) => (
          <MetricCardComponent key={i} metric={metric as any} />
        ))}
      </div>

      {/* Time-grain specific content */}
      {timeGrain === 'today' && renderTodayView()}
      {timeGrain === 'tomorrow' && renderTomorrowView()}
      {timeGrain === '7d' && renderWeekView()}
      {timeGrain === '30d' && renderMonthView()}
      {timeGrain === '90d' && renderMonthView()}
      {timeGrain === 'custom' && (
        <Card>
          <CardContent className="py-12 text-center">
            <Calendar className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">Custom date range picker coming soon</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

// Need to import Globe icon
import { Globe } from 'lucide-react'