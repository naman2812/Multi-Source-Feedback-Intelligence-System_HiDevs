import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { LayoutDashboard, MessageSquare, AlertTriangle, Download, RefreshCw, Settings, Search, CheckCircle, Bell } from 'lucide-react';

const COLORS = ['#10b981', '#ef4444', '#64748b'];

export default function App() {
  const [stats, setStats] = useState({ 
    total_feedback: 0, 
    sentiment_distribution: { positive: 0, negative: 0, neutral: 0 }, 
    total_bugs: 0,
    trend_data: []
  });
  const [feedbacks, setFeedbacks] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [forecast, setForecast] = useState([]);
  const [loading, setLoading] = useState(false);
  const [suggestedReplies, setSuggestedReplies] = useState({});
  const [activeTab, setActiveTab] = useState('dashboard');

  const fetchDashboardData = async () => {
    try {
      const statsRes = await fetch('/api/stats');
      if (statsRes.ok) setStats(await statsRes.json());
      
      const feedRes = await fetch('/api/feedback?limit=10');
      if (feedRes.ok) setFeedbacks(await feedRes.json());
      
      const alertRes = await fetch('/api/alerts');
      if (alertRes.ok) setAlerts(await alertRes.json());
      
      const forecastRes = await fetch('/api/forecast');
      if (forecastRes.ok) setForecast((await forecastRes.json()).forecast || []);
    } catch (e) {
      console.log("Using mock data as backend is unavailable");
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleIngest = async (source) => {
    setLoading(true);
    try {
      await fetch(`/api/ingest/${source}`, { method: 'POST' });
      alert(`Ingestion task started in background for ${source}!`);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const handleDownload = () => {
    window.open('/api/report/download', '_blank');
  };

  const handleSuggestReply = async (id) => {
    try {
      const res = await fetch(`/api/feedback/${id}/suggest-response`);
      const data = await res.json();
      setSuggestedReplies(prev => ({...prev, [id]: data.suggested_reply || "Error generating reply"}));
    } catch (e) {
      console.error(e);
    }
  };

  const handleResolve = async (id) => {
    try {
      await fetch(`/api/feedback/${id}/status?status=Resolved`, { method: 'PUT' });
      fetchDashboardData();
    } catch (e) {
      console.error(e);
    }
  };

  const pieData = [
    { name: 'Positive', value: stats.sentiment_distribution.positive },
    { name: 'Negative', value: stats.sentiment_distribution.negative },
    { name: 'Neutral', value: stats.sentiment_distribution.neutral },
  ];

  return (
    <div className="dashboard-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-brand">Feedback IQ</div>
        <nav className="nav-links">
          <a className={`nav-link ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveTab('dashboard')}><LayoutDashboard size={20} /> Dashboard</a>
          <a className={`nav-link ${activeTab === 'all' ? 'active' : ''}`} onClick={() => setActiveTab('all')}><MessageSquare size={20} /> All Feedback</a>
          <a className={`nav-link ${activeTab === 'urgent' ? 'active' : ''}`} onClick={() => setActiveTab('urgent')}><AlertTriangle size={20} /> Urgent Issues</a>
          <a className={`nav-link ${activeTab === 'settings' ? 'active' : ''}`} onClick={() => setActiveTab('settings')}><Settings size={20} /> Settings</a>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {activeTab === 'settings' && (
          <div>
             <header className="header"><h1>Settings</h1></header>
             <p style={{color: 'var(--text-secondary)'}}>System configuration options will appear here.</p>
          </div>
        )}
        
        {activeTab === 'urgent' && (
          <div>
            <header className="header"><h1>Urgent Issues</h1></header>
            <div className="feedback-list">
              {feedbacks.filter((fb: any) => fb.is_urgent).map((fb: any) => (
                <div key={fb.id} className="feedback-item" style={{opacity: fb.status === 'Resolved' ? 0.5 : 1}}>
                  <div className="feedback-content">
                    <p className="feedback-text">{fb.original_text}</p>
                    <div className="feedback-meta">
                      <span style={{textTransform: 'uppercase'}}>{fb.source}</span>
                      <span>Status: <strong>{fb.status}</strong></span>
                      <span className="urgent-tag"><AlertTriangle size={14}/> Urgent Bug</span>
                    </div>
                  </div>
                </div>
              ))}
              {feedbacks.filter((fb: any) => fb.is_urgent).length === 0 && <p>No urgent issues found.</p>}
            </div>
          </div>
        )}
        
        {activeTab === 'all' && (
          <div>
            <header className="header"><h1>All Feedback</h1></header>
            <div className="feedback-list">
              {feedbacks.map((fb: any) => (
                <div key={fb.id} className="feedback-item" style={{opacity: fb.status === 'Resolved' ? 0.5 : 1}}>
                  <div className="feedback-content">
                    <p className="feedback-text">{fb.original_text}</p>
                    <div className="feedback-meta">
                      <span style={{textTransform: 'uppercase'}}>{fb.source}</span>
                      <span>Status: <strong>{fb.status}</strong></span>
                      {fb.is_urgent && <span className="urgent-tag"><AlertTriangle size={14}/> Urgent Bug</span>}
                    </div>
                  </div>
                  <div className={`sentiment-badge badge-${fb.sentiment_label?.toLowerCase()}`}>
                    {fb.sentiment_label}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {activeTab === 'dashboard' && (
        <>
        <header className="header">
          <h1>Overview</h1>
          <div className="actions">
            {alerts.length > 0 && (
              <div style={{display: 'flex', alignItems: 'center', color: 'var(--negative)', marginRight: '1rem', fontWeight: 'bold'}}>
                <Bell size={18} style={{marginRight: '0.5rem'}} className="spin" />
                {alerts.length} New Alerts!
              </div>
            )}
            <button className="btn btn-secondary" onClick={() => handleIngest('playstore')} disabled={loading}>
              <RefreshCw size={18} className={loading ? "spin" : ""} /> Play Store
            </button>
            <button className="btn btn-secondary" onClick={() => handleIngest('appstore')} disabled={loading}>
              <RefreshCw size={18} className={loading ? "spin" : ""} /> App Store
            </button>
            <button className="btn" onClick={handleDownload}>
              <Download size={18} /> Generate Report
            </button>
          </div>
        </header>

        {/* Metrics */}
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-title">Total Feedback</div>
            <div className="metric-value">{stats.total_feedback}</div>
          </div>
          <div className="metric-card">
            <div className="metric-title" style={{color: 'var(--positive)'}}>Positive</div>
            <div className="metric-value">{stats.sentiment_distribution.positive}</div>
          </div>
          <div className="metric-card">
            <div className="metric-title" style={{color: 'var(--negative)'}}>Critical Bugs</div>
            <div className="metric-value">{stats.total_bugs}</div>
          </div>
        </div>

        {/* Charts */}
        <div className="charts-grid">
          <div className="chart-card">
            <div style={{display: 'flex', justifyContent: 'space-between'}}>
              <h3>Sentiment Trends & Forecast</h3>
              {forecast.length > 0 && <span style={{color: 'var(--text-secondary)'}}>AI Forecast: {forecast[0].trend}</span>}
            </div>
            <div style={{ width: '100%', height: 300 }}>
              <ResponsiveContainer>
                <LineChart data={stats.trend_data && stats.trend_data.length > 0 ? stats.trend_data : [{name: 'Mon', positive:0, negative:0, neutral:0}]}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="name" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <RechartsTooltip contentStyle={{backgroundColor: '#1e293b', border: 'none', borderRadius: '8px'}} />
                  <Line type="monotone" dataKey="positive" stroke="#10b981" strokeWidth={3} />
                  <Line type="monotone" dataKey="negative" stroke="#ef4444" strokeWidth={3} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="chart-card">
            <h3>Overall Sentiment</h3>
            <div style={{ width: '100%', height: 300 }}>
              <ResponsiveContainer>
                <PieChart>
                  <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={5} dataKey="value">
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip contentStyle={{backgroundColor: '#1e293b', border: 'none', borderRadius: '8px'}} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Recent Feedback */}
        <div className="feedback-list">
          <h3 style={{marginTop: 0, marginBottom: '1.5rem', fontSize: '1.125rem'}}>Recent Feedback (Team Collaboration)</h3>
          {feedbacks.map((fb: any) => (
            <div key={fb.id} className="feedback-item" style={{opacity: fb.status === 'Resolved' ? 0.5 : 1}}>
              <div className="feedback-content">
                <p className="feedback-text">{fb.original_text}</p>
                <div className="feedback-meta">
                  <span style={{textTransform: 'uppercase'}}>{fb.source}</span>
                  <span>Language: {fb.language}</span>
                  <span>Status: <strong>{fb.status}</strong></span>
                  {fb.is_urgent && <span className="urgent-tag"><AlertTriangle size={14}/> Urgent Bug</span>}
                </div>
                
                {/* Extra Credit Actions */}
                <div style={{marginTop: '1rem', display: 'flex', gap: '1rem'}}>
                  <button className="btn btn-secondary" onClick={() => handleSuggestReply(fb.id)} style={{padding: '0.5rem 1rem', fontSize: '0.875rem'}}>
                    Suggest AI Reply
                  </button>
                  {fb.status !== 'Resolved' && (
                    <button className="btn" onClick={() => handleResolve(fb.id)} style={{background: 'var(--positive)', padding: '0.5rem 1rem', fontSize: '0.875rem'}}>
                      <CheckCircle size={16} /> Mark Resolved
                    </button>
                  )}
                </div>
                {suggestedReplies[fb.id] && (
                  <div className="suggested-reply-box">
                    <p style={{margin: 0}}>{suggestedReplies[fb.id]}</p>
                  </div>
                )}
              </div>
              <div className={`sentiment-badge badge-${fb.sentiment_label?.toLowerCase()}`}>
                {fb.sentiment_label}
              </div>
            </div>
          ))}
          {feedbacks.length === 0 && <p style={{color: 'var(--text-secondary)'}}>No feedback available yet. Click a fetch button above.</p>}
        </div>
        </>
        )}
      </main>
    </div>
  );
}
