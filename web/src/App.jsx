import React, { useState, useMemo } from 'react';
import {
  Activity, Award, Shield, Target, Flame, Users, FileText, CheckCircle2,
  ChevronRight, ArrowUpRight, ArrowDownRight, Search, BarChart3, Crosshair,
  TrendingUp, Compass, Sliders, ExternalLink, HelpCircle
} from 'lucide-react';
import {
  ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  Radar, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, PieChart, Pie, Cell,
  ScatterChart, Scatter, ZAxis
} from 'recharts';

import top10Batters from './data/top_10_batters.json';
import top10Bowlers from './data/top_10_bowlers.json';
import allBatters from './data/all_batters.json';
import allBowlers from './data/all_bowlers.json';
import summaryKpis from './data/summary_kpis.json';
import matchEvidence from './data/match_evidence.json';
import modelMetrics from './data/model_metrics.json';
import sensitivity from './data/sensitivity.json';

const NAV_ITEMS = [
  { id: 'overview', label: '1. Executive Overview', icon: Activity },
  { id: 'pressure', label: '2. Pressure Intelligence', icon: Flame },
  { id: 'batters', label: '3. Top Batters', icon: Award },
  { id: 'bowlers', label: '4. Top Bowlers', icon: Crosshair },
  { id: 'player', label: '5. Player Deep Dive', icon: Users },
  { id: 'h2h', label: '6. Head-to-Head', icon: Sliders },
  { id: 'evidence', label: '7. Match Evidence', icon: FileText }
];

const COLORS = {
  blue: '#38bdf8',
  red: '#f87171',
  green: '#4ade80',
  amber: '#fbbf24',
  purple: '#a855f7',
  slate: '#64748b'
};

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  
  // Player Intelligence State
  const [playerRole, setPlayerRole] = useState('batter');
  const [selectedPlayerName, setSelectedPlayerName] = useState('Naman Dhir');
  
  // Head to Head State
  const [h2hRole, setH2hRole] = useState('batter');
  const [h2hP1, setH2hP1] = useState('Naman Dhir');
  const [h2hP2, setH2hP2] = useState('Ashutosh Sharma');

  // Search Filter
  const [searchQuery, setSearchQuery] = useState('');

  // Selected player object
  const currentPlayer = useMemo(() => {
    if (playerRole === 'batter') {
      return allBatters.find(p => p.striker_name === selectedPlayerName) || top10Batters[0];
    } else {
      return allBowlers.find(p => p.bowler_name === selectedPlayerName) || top10Bowlers[0];
    }
  }, [playerRole, selectedPlayerName]);

  // H2H player objects
  const player1Obj = useMemo(() => {
    if (h2hRole === 'batter') {
      return allBatters.find(p => p.striker_name === h2hP1) || top10Batters[0];
    } else {
      return allBowlers.find(p => p.bowler_name === h2hP1) || top10Bowlers[0];
    }
  }, [h2hRole, h2hP1]);

  const player2Obj = useMemo(() => {
    if (h2hRole === 'batter') {
      return allBatters.find(p => p.striker_name === h2hP2) || top10Batters[1];
    } else {
      return allBowlers.find(p => p.bowler_name === h2hP2) || top10Bowlers[1];
    }
  }, [h2hRole, h2hP2]);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#090d16] text-slate-100 font-sans">
      
      {/* SIDEBAR NAVIGATION */}
      <aside className="w-64 flex-shrink-0 bg-[#0f172a] border-r border-slate-800 flex flex-col justify-between">
        <div>
          {/* Logo */}
          <div className="p-5 border-b border-slate-800 flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center font-extrabold text-white shadow-lg shadow-cyan-500/20">
              🏏
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight text-white flex items-center gap-1.5">
                PRESSURE<span className="text-cyan-400">IQ</span>
              </h1>
              <p className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">SupeRR Selector Season 2</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-3 space-y-1">
            {NAV_ITEMS.map(item => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                    isActive
                      ? 'bg-blue-600/20 text-cyan-400 border border-blue-500/30 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Sidebar Footer Info */}
        <div className="p-4 border-t border-slate-800/80 bg-slate-900/40 text-[11px] text-slate-400 space-y-1.5">
          <div className="flex justify-between items-center text-slate-300 font-medium">
            <span>Data Scope</span>
            <span className="text-cyan-400 font-semibold">2022–2026</span>
          </div>
          <div className="flex justify-between items-center">
            <span>Matches Evaluated</span>
            <span className="text-slate-200">837</span>
          </div>
          <div className="flex justify-between items-center">
            <span>Validation</span>
            <span className="text-emerald-400 font-semibold">0% Leakage</span>
          </div>
          <div className="pt-2">
            <div className="inline-block w-full text-center py-1.5 rounded-md bg-slate-800 text-slate-300 hover:text-white transition font-medium border border-slate-700/60">
              PDF Report Generated (13p)
            </div>
          </div>
        </div>
      </aside>

      {/* MAIN CONTENT AREA */}
      <main className="flex-1 flex flex-col overflow-hidden">
        
        {/* Top Header */}
        <header className="h-16 px-8 border-b border-slate-800/80 bg-[#0c1222] flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-white tracking-tight">
              {NAV_ITEMS.find(n => n.id === activeTab)?.label}
            </h2>
            <p className="text-xs text-slate-400">Context-Aware Cricket Pressure & Player Reliability Engine</p>
          </div>

          <div className="flex items-center gap-3">
            <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              Live Analytical Dataset
            </span>
            <span className="text-xs text-slate-400 bg-slate-800/80 px-3 py-1 rounded-md border border-slate-700/60">
              Format: IPL + T20I
            </span>
          </div>
        </header>

        {/* Body Content */}
        <div className="flex-1 overflow-y-auto p-8 space-y-6">

          {/* ================================================================= */}
          {/* TAB 1: EXECUTIVE OVERVIEW */}
          {/* ================================================================= */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* KPI CARDS */}
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                  <span className="text-xs text-slate-400 font-medium">Matches Analyzed</span>
                  <div className="text-2xl font-bold text-cyan-400 mt-1">837</div>
                  <span className="text-[11px] text-slate-500">IPL & T20I (2022–26)</span>
                </div>
                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                  <span className="text-xs text-slate-400 font-medium">Deliveries Evaluated</span>
                  <div className="text-2xl font-bold text-white mt-1">193,988</div>
                  <span className="text-[11px] text-slate-500">100% Pre-Delivery State</span>
                </div>
                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                  <span className="text-xs text-slate-400 font-medium">Eligible Batters</span>
                  <div className="text-2xl font-bold text-blue-400 mt-1">198</div>
                  <span className="text-[11px] text-slate-500">≥75 Pressure Deliveries</span>
                </div>
                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                  <span className="text-xs text-slate-400 font-medium">Eligible Bowlers</span>
                  <div className="text-2xl font-bold text-rose-400 mt-1">267</div>
                  <span className="text-[11px] text-slate-500">≥60 Pressure Deliveries</span>
                </div>
                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                  <span className="text-xs text-slate-400 font-medium">Validation Leakage</span>
                  <div className="text-2xl font-bold text-emerald-400 mt-1">0.0%</div>
                  <span className="text-[11px] text-slate-500">GroupKFold by Match</span>
                </div>
              </div>

              {/* TOP 10 SUMMARY TABLES */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                
                {/* Batters */}
                <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-base font-bold text-white flex items-center gap-2">
                      <Award className="w-5 h-5 text-cyan-400" />
                      Top 10 Batters Under Pressure
                    </h3>
                    <button onClick={() => setActiveTab('batters')} className="text-xs text-cyan-400 hover:underline flex items-center gap-1">
                      View all 198 <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full text-xs text-left">
                      <thead className="bg-slate-800/60 text-slate-300 font-semibold uppercase text-[10px]">
                        <tr>
                          <th className="p-2">Rank</th>
                          <th className="p-2">Player</th>
                          <th className="p-2 text-right">Rating</th>
                          <th className="p-2 text-right">Press SR</th>
                          <th className="p-2 text-right">Δ SR</th>
                          <th className="p-2 text-right">90% CI</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800">
                        {top10Batters.map(b => (
                          <tr key={b.striker_id} className="hover:bg-slate-800/30 transition">
                            <td className="p-2 font-bold text-cyan-400">#{b.rank}</td>
                            <td className="p-2 font-semibold text-white">{b.striker_name}</td>
                            <td className="p-2 text-right font-bold text-cyan-300">{b.final_rating.toFixed(2)}</td>
                            <td className="p-2 text-right text-slate-200">{b.pressure_strike_rate.toFixed(1)}</td>
                            <td className={`p-2 text-right font-medium ${b.adj_delta_sr >= 0 ? 'text-emerald-400' : 'text-slate-400'}`}>
                              {b.adj_delta_sr > 0 ? `+${b.adj_delta_sr.toFixed(1)}` : b.adj_delta_sr.toFixed(1)}
                            </td>
                            <td className="p-2 text-right text-slate-400">[{b.ci_lower.toFixed(1)}, {b.ci_upper.toFixed(1)}]</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Bowlers */}
                <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-base font-bold text-white flex items-center gap-2">
                      <Crosshair className="w-5 h-5 text-rose-400" />
                      Top 10 Bowlers Under Pressure
                    </h3>
                    <button onClick={() => setActiveTab('bowlers')} className="text-xs text-rose-400 hover:underline flex items-center gap-1">
                      View all 267 <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full text-xs text-left">
                      <thead className="bg-slate-800/60 text-slate-300 font-semibold uppercase text-[10px]">
                        <tr>
                          <th className="p-2">Rank</th>
                          <th className="p-2">Bowler</th>
                          <th className="p-2 text-right">Rating</th>
                          <th className="p-2 text-right">Press Econ</th>
                          <th className="p-2 text-right">Wickets</th>
                          <th className="p-2 text-right">90% CI</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800">
                        {top10Bowlers.map(b => (
                          <tr key={b.bowler_id} className="hover:bg-slate-800/30 transition">
                            <td className="p-2 font-bold text-rose-400">#{b.rank}</td>
                            <td className="p-2 font-semibold text-white">{b.bowler_name}</td>
                            <td className="p-2 text-right font-bold text-rose-300">{b.final_rating.toFixed(2)}</td>
                            <td className="p-2 text-right text-slate-200">{b.pressure_economy.toFixed(2)}</td>
                            <td className="p-2 text-right text-amber-400 font-semibold">{b.pressure_wickets}</td>
                            <td className="p-2 text-right text-slate-400">[{b.ci_lower.toFixed(1)}, {b.ci_upper.toFixed(1)}]</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

              </div>

              {/* PRESSURE TIER & TOURNAMENT CHARTS */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
                  <h4 className="text-sm font-bold text-white mb-3">Pressure Category Distribution</h4>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={[
                        { name: 'Low (<35)', Batting: summaryKpis.batting_tiers.low, Bowling: summaryKpis.bowling_tiers.low },
                        { name: 'Moderate (35-60)', Batting: summaryKpis.batting_tiers.moderate, Bowling: summaryKpis.bowling_tiers.moderate },
                        { name: 'High (60-80)', Batting: summaryKpis.batting_tiers.high, Bowling: summaryKpis.bowling_tiers.high },
                        { name: 'Extreme (≥80)', Batting: summaryKpis.batting_tiers.extreme, Bowling: summaryKpis.bowling_tiers.extreme }
                      ]}>
                        <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
                        <YAxis stroke="#64748b" fontSize={11} />
                        <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f1f5f9' }} />
                        <Legend />
                        <Bar dataKey="Batting" fill="#38bdf8" radius={[4, 4, 0, 0]} />
                        <Bar dataKey="Bowling" fill="#f87171" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
                  <h4 className="text-sm font-bold text-white mb-3">Dominant Batting Pressure Scenarios</h4>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={[
                            { name: 'Normal', value: summaryKpis.dominant_batting_scenarios.Normal || 132610 },
                            { name: 'Run Chase', value: summaryKpis.dominant_batting_scenarios['Run Chase'] || 28410 },
                            { name: 'Collapse', value: summaryKpis.dominant_batting_scenarios.Collapse || 18450 },
                            { name: 'Survival', value: summaryKpis.dominant_batting_scenarios.Survival || 8920 },
                            { name: 'Momentum Deficit', value: summaryKpis.dominant_batting_scenarios['Momentum Deficit'] || 5598 }
                          ]}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={90}
                          paddingAngle={3}
                          dataKey="value"
                        >
                          <Cell fill="#334155" />
                          <Cell fill="#38bdf8" />
                          <Cell fill="#f97316" />
                          <Cell fill="#ef4444" />
                          <Cell fill="#a855f7" />
                        </Pie>
                        <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f1f5f9' }} />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>

            </div>
          )}

          {/* ================================================================= */}
          {/* TAB 2: PRESSURE INTELLIGENCE */}
          {/* ================================================================= */}
          {activeTab === 'pressure' && (
            <div className="space-y-6">
              <div className="p-6 rounded-xl bg-slate-900 border border-slate-800">
                <h3 className="text-base font-bold text-white mb-2">The Six Context-Aware Pressure Scenarios</h3>
                <p className="text-xs text-slate-400 mb-6 leading-relaxed">
                  PRESSUREIQ evaluates match difficulty strictly before each delivery outcome is known. Pressure is decoupled between batting and bowling, and evaluated across both innings.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 rounded-lg bg-slate-800/40 border border-slate-700/60">
                    <span className="text-xs font-bold text-amber-400 uppercase tracking-wider">Scenario A</span>
                    <h4 className="text-sm font-bold text-white mt-1">Batting Collapse Pressure</h4>
                    <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                      Triggered by rapid fall of wickets (w12, w18), top order depletion, and 1st innings par score deficits. Identifies batters who anchor or counterattack under crisis.
                    </p>
                  </div>

                  <div className="p-4 rounded-lg bg-slate-800/40 border border-slate-700/60">
                    <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider">Scenario B</span>
                    <h4 className="text-sm font-bold text-white mt-1">Run Chase Steepness</h4>
                    <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                      Evaluated in 2nd innings via required run rate (RRR), RRR - CRR differential, and dwindling ball resources relative to wickets in hand.
                    </p>
                  </div>

                  <div className="p-4 rounded-lg bg-slate-800/40 border border-slate-700/60">
                    <span className="text-xs font-bold text-rose-400 uppercase tracking-wider">Scenario C</span>
                    <h4 className="text-sm font-bold text-white mt-1">Lower-Order Survival</h4>
                    <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                      Measures batting position ≥ 7 or ≥ 6 wickets down while significant overs remain, preventing early team termination.
                    </p>
                  </div>

                  <div className="p-4 rounded-lg bg-slate-800/40 border border-slate-700/60">
                    <span className="text-xs font-bold text-rose-400 uppercase tracking-wider">Scenario D</span>
                    <h4 className="text-sm font-bold text-white mt-1">Opposition Aggression (Bowling)</h4>
                    <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                      Bowler facing an opposition scoring at 10–14+ RPO over recent deliveries, consecutive boundaries, and large active partnerships.
                    </p>
                  </div>

                  <div className="p-4 rounded-lg bg-slate-800/40 border border-slate-700/60">
                    <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider">Scenario E</span>
                    <h4 className="text-sm font-bold text-white mt-1">Defensive Bowling Leverage</h4>
                    <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                      Defending tight margins in 2nd innings death overs where required runs approximately match balls remaining.
                    </p>
                  </div>

                  <div className="p-4 rounded-lg bg-slate-800/40 border border-slate-700/60">
                    <span className="text-xs font-bold text-purple-400 uppercase tracking-wider">Scenario F</span>
                    <h4 className="text-sm font-bold text-white mt-1">Momentum Shifts</h4>
                    <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                      Clustering of dot balls (3+ consecutive dots), acute scoring deceleration, and turning-point phases across both innings.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* ================================================================= */}
          {/* TAB 3: TOP BATTERS */}
          {/* ================================================================= */}
          {activeTab === 'batters' && (
            <div className="space-y-6">
              <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
                <div className="flex flex-col md:flex-row items-center justify-between gap-4 mb-4">
                  <div>
                    <h3 className="text-base font-bold text-white">All Eligible Batters Under Pressure</h3>
                    <p className="text-xs text-slate-400">Filterable by player name. Min 75 pressure balls faced, min 20 normal balls baseline.</p>
                  </div>
                  <div className="relative w-72">
                    <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
                    <input
                      type="text"
                      placeholder="Search player..."
                      value={searchQuery}
                      onChange={e => setSearchQuery(e.target.value)}
                      className="w-full pl-9 pr-3 py-1.5 rounded-lg bg-slate-800 text-xs text-white placeholder-slate-400 border border-slate-700 focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                </div>

                <div className="overflow-x-auto max-h-[500px]">
                  <table className="w-full text-xs text-left">
                    <thead className="bg-slate-800 text-slate-300 font-semibold uppercase text-[10px] sticky top-0 z-10">
                      <tr>
                        <th className="p-2.5">Rank</th>
                        <th className="p-2.5">Player</th>
                        <th className="p-2.5 text-right">Rating</th>
                        <th className="p-2.5 text-right">Press SR</th>
                        <th className="p-2.5 text-right">Norm SR</th>
                        <th className="p-2.5 text-right">Δ SR</th>
                        <th className="p-2.5 text-right">Impact</th>
                        <th className="p-2.5 text-right">Resilience</th>
                        <th className="p-2.5 text-right">Consistency</th>
                        <th className="p-2.5 text-right">Confidence</th>
                        <th className="p-2.5 text-right">Collapse</th>
                        <th className="p-2.5 text-right">Balls</th>
                        <th className="p-2.5 text-right">Runs</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                      {allBatters
                        .filter(b => b.striker_name.toLowerCase().includes(searchQuery.toLowerCase()))
                        .map(b => (
                          <tr key={b.striker_id} className="hover:bg-slate-800/40 transition">
                            <td className="p-2.5 font-bold text-cyan-400">#{b.rank}</td>
                            <td className="p-2.5 font-semibold text-white">{b.striker_name}</td>
                            <td className="p-2.5 text-right font-bold text-cyan-300">{b.final_rating.toFixed(2)}</td>
                            <td className="p-2.5 text-right text-slate-200">{b.pressure_strike_rate.toFixed(1)}</td>
                            <td className="p-2.5 text-right text-slate-400">{b.normal_strike_rate.toFixed(1)}</td>
                            <td className={`p-2.5 text-right font-medium ${b.adj_delta_sr >= 0 ? 'text-emerald-400' : 'text-slate-400'}`}>
                              {b.adj_delta_sr > 0 ? `+${b.adj_delta_sr.toFixed(1)}` : b.adj_delta_sr.toFixed(1)}
                            </td>
                            <td className="p-2.5 text-right text-slate-300">{b.impact_score.toFixed(1)}</td>
                            <td className="p-2.5 text-right text-slate-300">{b.resilience_score.toFixed(1)}</td>
                            <td className="p-2.5 text-right text-slate-300">{b.consistency_score.toFixed(1)}</td>
                            <td className="p-2.5 text-right text-slate-300">{b.sample_confidence_score.toFixed(1)}</td>
                            <td className="p-2.5 text-right text-slate-300">{b.collapse_resistance_score.toFixed(1)}</td>
                            <td className="p-2.5 text-right text-slate-400">{b.pressure_balls_faced}</td>
                            <td className="p-2.5 text-right text-slate-400">{b.pressure_runs}</td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* ================================================================= */}
          {/* TAB 4: TOP BOWLERS */}
          {/* ================================================================= */}
          {activeTab === 'bowlers' && (
            <div className="space-y-6">
              <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
                <div className="flex flex-col md:flex-row items-center justify-between gap-4 mb-4">
                  <div>
                    <h3 className="text-base font-bold text-white">All Eligible Bowlers Under Pressure</h3>
                    <p className="text-xs text-slate-400">Filterable by bowler name. Min 60 pressure legal balls bowled, min 20 normal balls baseline.</p>
                  </div>
                  <div className="relative w-72">
                    <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
                    <input
                      type="text"
                      placeholder="Search bowler..."
                      value={searchQuery}
                      onChange={e => setSearchQuery(e.target.value)}
                      className="w-full pl-9 pr-3 py-1.5 rounded-lg bg-slate-800 text-xs text-white placeholder-slate-400 border border-slate-700 focus:outline-none focus:border-rose-500"
                    />
                  </div>
                </div>

                <div className="overflow-x-auto max-h-[500px]">
                  <table className="w-full text-xs text-left">
                    <thead className="bg-slate-800 text-slate-300 font-semibold uppercase text-[10px] sticky top-0 z-10">
                      <tr>
                        <th className="p-2.5">Rank</th>
                        <th className="p-2.5">Bowler</th>
                        <th className="p-2.5 text-right">Rating</th>
                        <th className="p-2.5 text-right">Press Econ</th>
                        <th className="p-2.5 text-right">Norm Econ</th>
                        <th className="p-2.5 text-right">Δ Econ</th>
                        <th className="p-2.5 text-right">Impact</th>
                        <th className="p-2.5 text-right">Resilience</th>
                        <th className="p-2.5 text-right">Consistency</th>
                        <th className="p-2.5 text-right">Confidence</th>
                        <th className="p-2.5 text-right">Aggression Res.</th>
                        <th className="p-2.5 text-right">Balls</th>
                        <th className="p-2.5 text-right">Wickets</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                      {allBowlers
                        .filter(b => b.bowler_name.toLowerCase().includes(searchQuery.toLowerCase()))
                        .map(b => (
                          <tr key={b.bowler_id} className="hover:bg-slate-800/40 transition">
                            <td className="p-2.5 font-bold text-rose-400">#{b.rank}</td>
                            <td className="p-2.5 font-semibold text-white">{b.bowler_name}</td>
                            <td className="p-2.5 text-right font-bold text-rose-300">{b.final_rating.toFixed(2)}</td>
                            <td className="p-2.5 text-right text-slate-200">{b.pressure_economy.toFixed(2)}</td>
                            <td className="p-2.5 text-right text-slate-400">{b.normal_economy.toFixed(2)}</td>
                            <td className={`p-2.5 text-right font-medium ${b.adj_delta_econ >= 0 ? 'text-emerald-400' : 'text-slate-400'}`}>
                              {b.adj_delta_econ > 0 ? `+${b.adj_delta_econ.toFixed(2)}` : b.adj_delta_econ.toFixed(2)}
                            </td>
                            <td className="p-2.5 text-right text-slate-300">{b.impact_score.toFixed(1)}</td>
                            <td className="p-2.5 text-right text-slate-300">{b.resilience_score.toFixed(1)}</td>
                            <td className="p-2.5 text-right text-slate-300">{b.consistency_score.toFixed(1)}</td>
                            <td className="p-2.5 text-right text-slate-300">{b.sample_confidence_score.toFixed(1)}</td>
                            <td className="p-2.5 text-right text-slate-300">{b.aggression_resistance_score.toFixed(1)}</td>
                            <td className="p-2.5 text-right text-slate-400">{b.pressure_legal_balls}</td>
                            <td className="p-2.5 text-right text-amber-400 font-bold">{b.pressure_wickets}</td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* ================================================================= */}
          {/* TAB 5: INDIVIDUAL PLAYER INTELLIGENCE */}
          {/* ================================================================= */}
          {activeTab === 'player' && (
            <div className="space-y-6">
              <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
                <div className="flex flex-col md:flex-row items-center justify-between gap-4 mb-6">
                  <div className="flex items-center gap-4">
                    <div className="flex rounded-lg bg-slate-800 p-1 border border-slate-700">
                      <button
                        onClick={() => { setPlayerRole('batter'); setSelectedPlayerName('Naman Dhir'); }}
                        className={`px-3 py-1 rounded text-xs font-semibold ${playerRole === 'batter' ? 'bg-cyan-500 text-white' : 'text-slate-400'}`}
                      >
                        Batters
                      </button>
                      <button
                        onClick={() => { setPlayerRole('bowler'); setSelectedPlayerName('Matheesha Pathirana'); }}
                        className={`px-3 py-1 rounded text-xs font-semibold ${playerRole === 'bowler' ? 'bg-rose-500 text-white' : 'text-slate-400'}`}
                      >
                        Bowlers
                      </button>
                    </div>

                    <select
                      value={selectedPlayerName}
                      onChange={e => setSelectedPlayerName(e.target.value)}
                      className="px-3 py-1.5 rounded-lg bg-slate-800 text-xs text-white border border-slate-700 focus:outline-none"
                    >
                      {(playerRole === 'batter' ? allBatters : allBowlers).map(p => (
                        <option key={p.striker_id || p.bowler_id} value={p.striker_name || p.bowler_name}>
                          #{p.rank} {p.striker_name || p.bowler_name} (Rating: {p.final_rating.toFixed(1)})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-400">Rank:</span>
                    <span className="text-base font-bold text-cyan-400">#{currentPlayer.rank}</span>
                    <span className="text-xs text-slate-400 ml-3">Final Rating:</span>
                    <span className="text-base font-bold text-white">{currentPlayer.final_rating.toFixed(2)}</span>
                  </div>
                </div>

                {/* Radar Chart & Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
                  <div className="h-72">
                    <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2 text-center">Five Reliability Dimensions</h4>
                    <ResponsiveContainer width="100%" height="100%">
                      <RadarChart data={[
                        { subject: 'Impact', value: currentPlayer.impact_score },
                        { subject: 'Resilience', value: currentPlayer.resilience_score },
                        { subject: 'Consistency', value: currentPlayer.consistency_score },
                        { subject: 'Confidence', value: currentPlayer.sample_confidence_score },
                        { subject: playerRole === 'batter' ? 'Collapse Res.' : 'Aggression Res.', value: currentPlayer.collapse_resistance_score || currentPlayer.aggression_resistance_score }
                      ]}>
                        <PolarGrid stroke="#334155" />
                        <PolarAngleAxis dataKey="subject" stroke="#94a3b8" fontSize={11} />
                        <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#475569" />
                        <Radar name={selectedPlayerName} dataKey="value" stroke={playerRole === 'batter' ? '#38bdf8' : '#f87171'} fill={playerRole === 'batter' ? '#38bdf8' : '#f87171'} fillOpacity={0.4} />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="space-y-3">
                    <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Performance Diagnostic</h4>
                    <div className="grid grid-cols-2 gap-3 text-xs">
                      <div className="p-3 rounded-lg bg-slate-800/60 border border-slate-700/60">
                        <span className="text-slate-400">{playerRole === 'batter' ? 'Pressure Strike Rate' : 'Pressure Economy'}</span>
                        <div className="text-lg font-bold text-white mt-1">
                          {playerRole === 'batter' ? currentPlayer.pressure_strike_rate.toFixed(1) : currentPlayer.pressure_economy.toFixed(2)}
                        </div>
                        <span className="text-[11px] text-slate-500">Normal: {playerRole === 'batter' ? currentPlayer.normal_strike_rate.toFixed(1) : currentPlayer.normal_economy.toFixed(2)}</span>
                      </div>

                      <div className="p-3 rounded-lg bg-slate-800/60 border border-slate-700/60">
                        <span className="text-slate-400">Resilience Delta</span>
                        <div className={`text-lg font-bold mt-1 ${(currentPlayer.adj_delta_sr || currentPlayer.adj_delta_econ) >= 0 ? 'text-emerald-400' : 'text-slate-300'}`}>
                          {playerRole === 'batter'
                            ? (currentPlayer.adj_delta_sr >= 0 ? `+${currentPlayer.adj_delta_sr.toFixed(1)}` : currentPlayer.adj_delta_sr.toFixed(1))
                            : (currentPlayer.adj_delta_econ >= 0 ? `+${currentPlayer.adj_delta_econ.toFixed(2)}` : currentPlayer.adj_delta_econ.toFixed(2))
                          }
                        </div>
                        <span className="text-[11px] text-slate-500">Shrunk Baseline Diff</span>
                      </div>

                      <div className="p-3 rounded-lg bg-slate-800/60 border border-slate-700/60">
                        <span className="text-slate-400">{playerRole === 'batter' ? 'Pressure Deliveries' : 'Pressure Legal Deliveries'}</span>
                        <div className="text-lg font-bold text-cyan-400 mt-1">
                          {currentPlayer.pressure_balls_faced || currentPlayer.pressure_legal_balls}
                        </div>
                        <span className="text-[11px] text-slate-500">Across {currentPlayer.pressure_matches} matches</span>
                      </div>

                      <div className="p-3 rounded-lg bg-slate-800/60 border border-slate-700/60">
                        <span className="text-slate-400">90% Bootstrap CI</span>
                        <div className="text-lg font-bold text-amber-400 mt-1">
                          [{currentPlayer.ci_lower.toFixed(1)}, {currentPlayer.ci_upper.toFixed(1)}]
                        </div>
                        <span className="text-[11px] text-slate-500">500 match resamples</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* ================================================================= */}
          {/* TAB 6: HEAD-TO-HEAD COMPARISON */}
          {/* ================================================================= */}
          {activeTab === 'h2h' && (
            <div className="space-y-6">
              <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-base font-bold text-white">Compare Two Players Under Pressure</h3>
                  <div className="flex rounded-lg bg-slate-800 p-1 border border-slate-700">
                    <button
                      onClick={() => { setH2hRole('batter'); setH2hP1('Naman Dhir'); setH2hP2('Ashutosh Sharma'); }}
                      className={`px-3 py-1 rounded text-xs font-semibold ${h2hRole === 'batter' ? 'bg-cyan-500 text-white' : 'text-slate-400'}`}
                    >
                      Batters
                    </button>
                    <button
                      onClick={() => { setH2hRole('bowler'); setH2hP1('Matheesha Pathirana'); setH2hP2('Jasprit Bumrah'); }}
                      className={`px-3 py-1 rounded text-xs font-semibold ${h2hRole === 'bowler' ? 'bg-rose-500 text-white' : 'text-slate-400'}`}
                    >
                      Bowlers
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div>
                    <label className="text-xs text-slate-400 mb-1 block">Player A</label>
                    <select
                      value={h2hP1}
                      onChange={e => setH2hP1(e.target.value)}
                      className="w-full px-3 py-2 rounded-lg bg-slate-800 text-xs text-white border border-slate-700 focus:outline-none"
                    >
                      {(h2hRole === 'batter' ? allBatters : allBowlers).map(p => (
                        <option key={p.striker_id || p.bowler_id} value={p.striker_name || p.bowler_name}>
                          #{p.rank} {p.striker_name || p.bowler_name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="text-xs text-slate-400 mb-1 block">Player B</label>
                    <select
                      value={h2hP2}
                      onChange={e => setH2hP2(e.target.value)}
                      className="w-full px-3 py-2 rounded-lg bg-slate-800 text-xs text-white border border-slate-700 focus:outline-none"
                    >
                      {(h2hRole === 'batter' ? allBatters : allBowlers).map(p => (
                        <option key={p.striker_id || p.bowler_id} value={p.striker_name || p.bowler_name}>
                          #{p.rank} {p.striker_name || p.bowler_name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Radar Overlay */}
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart data={[
                      { subject: 'Impact', [h2hP1]: player1Obj.impact_score, [h2hP2]: player2Obj.impact_score },
                      { subject: 'Resilience', [h2hP1]: player1Obj.resilience_score, [h2hP2]: player2Obj.resilience_score },
                      { subject: 'Consistency', [h2hP1]: player1Obj.consistency_score, [h2hP2]: player2Obj.consistency_score },
                      { subject: 'Confidence', [h2hP1]: player1Obj.sample_confidence_score, [h2hP2]: player2Obj.sample_confidence_score },
                      { subject: h2hRole === 'batter' ? 'Collapse Res.' : 'Aggression Res.', [h2hP1]: player1Obj.collapse_resistance_score || player1Obj.aggression_resistance_score, [h2hP2]: player2Obj.collapse_resistance_score || player2Obj.aggression_resistance_score }
                    ]}>
                      <PolarGrid stroke="#334155" />
                      <PolarAngleAxis dataKey="subject" stroke="#94a3b8" fontSize={11} />
                      <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#475569" />
                      <Radar name={h2hP1} dataKey={h2hP1} stroke="#38bdf8" fill="#38bdf8" fillOpacity={0.3} />
                      <Radar name={h2hP2} dataKey={h2hP2} stroke="#f43f5e" fill="#f43f5e" fillOpacity={0.3} />
                      <Legend />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>

                {/* Side by side comparison table */}
                <div className="mt-6 overflow-x-auto">
                  <table className="w-full text-xs text-left">
                    <thead className="bg-slate-800 text-slate-300 font-semibold uppercase text-[10px]">
                      <tr>
                        <th className="p-2.5">Metric</th>
                        <th className="p-2.5 text-cyan-400 font-bold">{h2hP1}</th>
                        <th className="p-2.5 text-rose-400 font-bold">{h2hP2}</th>
                        <th className="p-2.5 text-right">Advantage</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                      <tr>
                        <td className="p-2.5 text-slate-400">Overall Rank</td>
                        <td className="p-2.5 font-bold text-white">#{player1Obj.rank}</td>
                        <td className="p-2.5 font-bold text-white">#{player2Obj.rank}</td>
                        <td className="p-2.5 text-right font-semibold text-emerald-400">
                          {player1Obj.rank < player2Obj.rank ? h2hP1 : h2hP2}
                        </td>
                      </tr>
                      <tr>
                        <td className="p-2.5 text-slate-400">Final Rating</td>
                        <td className="p-2.5 font-bold text-white">{player1Obj.final_rating.toFixed(2)}</td>
                        <td className="p-2.5 font-bold text-white">{player2Obj.final_rating.toFixed(2)}</td>
                        <td className="p-2.5 text-right font-semibold text-emerald-400">
                          {player1Obj.final_rating > player2Obj.final_rating ? h2hP1 : h2hP2}
                        </td>
                      </tr>
                      <tr>
                        <td className="p-2.5 text-slate-400">{h2hRole === 'batter' ? 'Pressure Strike Rate' : 'Pressure Economy'}</td>
                        <td className="p-2.5 font-bold text-white">{h2hRole === 'batter' ? player1Obj.pressure_strike_rate.toFixed(1) : player1Obj.pressure_economy.toFixed(2)}</td>
                        <td className="p-2.5 font-bold text-white">{h2hRole === 'batter' ? player2Obj.pressure_strike_rate.toFixed(1) : player2Obj.pressure_economy.toFixed(2)}</td>
                        <td className="p-2.5 text-right font-semibold text-emerald-400">
                          {h2hRole === 'batter'
                            ? (player1Obj.pressure_strike_rate > player2Obj.pressure_strike_rate ? h2hP1 : h2hP2)
                            : (player1Obj.pressure_economy < player2Obj.pressure_economy ? h2hP1 : h2hP2)
                          }
                        </td>
                      </tr>
                      <tr>
                        <td className="p-2.5 text-slate-400">Resilience Delta</td>
                        <td className="p-2.5 font-bold text-white">{h2hRole === 'batter' ? player1Obj.adj_delta_sr.toFixed(1) : player1Obj.adj_delta_econ.toFixed(2)}</td>
                        <td className="p-2.5 font-bold text-white">{h2hRole === 'batter' ? player2Obj.adj_delta_sr.toFixed(1) : player2Obj.adj_delta_econ.toFixed(2)}</td>
                        <td className="p-2.5 text-right font-semibold text-emerald-400">
                          {(h2hRole === 'batter' ? player1Obj.adj_delta_sr : player1Obj.adj_delta_econ) > (h2hRole === 'batter' ? player2Obj.adj_delta_sr : player2Obj.adj_delta_econ) ? h2hP1 : h2hP2}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* ================================================================= */}
          {/* TAB 7: MATCH EVIDENCE & EXPLAINABILITY */}
          {/* ================================================================= */}
          {activeTab === 'evidence' && (
            <div className="space-y-6">
              <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
                <h3 className="text-base font-bold text-white mb-1">Delivery-Level Explainability Audit</h3>
                <p className="text-xs text-slate-400 mb-4">
                  Inspect actual match deliveries where top ranked players outperformed situational expectations.
                </p>

                <div className="overflow-x-auto max-h-[500px]">
                  <table className="w-full text-xs text-left">
                    <thead className="bg-slate-800 text-slate-300 font-semibold uppercase text-[10px] sticky top-0 z-10">
                      <tr>
                        <th className="p-2.5">Match ID</th>
                        <th className="p-2.5">Format</th>
                        <th className="p-2.5">Over</th>
                        <th className="p-2.5">Striker</th>
                        <th className="p-2.5">Bowler</th>
                        <th className="p-2.5 text-right">Pressure Score</th>
                        <th className="p-2.5 text-right">Scenario</th>
                        <th className="p-2.5 text-right">Actual Runs</th>
                        <th className="p-2.5 text-right">Expected Runs</th>
                        <th className="p-2.5 text-right">Impact</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                      {matchEvidence.slice(0, 50).map((row, idx) => (
                        <tr key={idx} className="hover:bg-slate-800/40 transition">
                          <td className="p-2.5 text-slate-400">#{row.match_id}</td>
                          <td className="p-2.5 font-medium text-cyan-400">{row.format_type}</td>
                          <td className="p-2.5 text-slate-300">Ov {row.overid}.{row.over_ball_num}</td>
                          <td className="p-2.5 font-semibold text-white">{row.striker_name}</td>
                          <td className="p-2.5 text-slate-300">{row.bowler_name}</td>
                          <td className="p-2.5 text-right font-bold text-amber-400">{row.batting_pressure_score || row.bowling_pressure_score}</td>
                          <td className="p-2.5 text-right text-slate-300">{row.dominant_batting_scenario || row.dominant_bowling_scenario}</td>
                          <td className="p-2.5 text-right font-bold text-white">{row.batter_runs || row.bowler_runs_conceded}</td>
                          <td className="p-2.5 text-right text-slate-400">{(row.exp_batter_runs || row.exp_bowler_runs).toFixed(2)}</td>
                          <td className={`p-2.5 text-right font-bold ${(row.batting_impact || row.bowling_impact) >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                            {(row.batting_impact || row.bowling_impact).toFixed(2)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

        </div>
      </main>

    </div>
  );
}
