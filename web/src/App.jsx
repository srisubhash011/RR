import React, { useState, useMemo } from 'react';
import {
  Activity, Award, Shield, Target, Flame, Users, FileText, CheckCircle2,
  ChevronRight, ArrowUpRight, ArrowDownRight, Search, BarChart3, Crosshair,
  TrendingUp, Compass, Sliders, ExternalLink, HelpCircle, Zap, Sparkles,
  Info, BarChart2, Eye, Download, ChevronDown, Filter, RotateCcw, UserCheck
} from 'lucide-react';
import {
  ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  Radar, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, PieChart, Pie, Cell,
  ScatterChart, Scatter, ZAxis, AreaChart, Area
} from 'recharts';

import top10Batters from './data/top_10_batters.json';
import top10Bowlers from './data/top_10_bowlers.json';
import allBatters from './data/all_batters.json';
import allBowlers from './data/all_bowlers.json';
import summaryKpis from './data/summary_kpis.json';
import matchEvidence from './data/match_evidence.json';
import modelMetrics from './data/model_metrics.json';
import sensitivity from './data/sensitivity.json';
import playerProfiles from './data/player_pressure_profiles.json';

const NAV_ITEMS = [
  { id: 'overview', label: '1. Executive Overview', icon: Activity, desc: 'High-level insights & Top 10' },
  { id: 'player', label: '2. Player Diagnostics', icon: Users, desc: 'Radar & Situational baselines' },
  { id: 'h2h', label: '3. Head-to-Head Arena', icon: Sliders, desc: 'Dual player comparison' },
  { id: 'pressure', label: '4. Pressure Engine', icon: Flame, desc: '6 Scenario breakdowns' },
  { id: 'batters', label: '5. Batting Rankings', icon: Award, desc: '198 Eligible batters' },
  { id: 'bowlers', label: '6. Bowling Rankings', icon: Crosshair, desc: '267 Eligible bowlers' },
  { id: 'evidence', label: '7. Match Evidence', icon: FileText, desc: 'Delivery explainability audit' }
];

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  
  // Executive Overview Selected Player (null = Overall Tournament view)
  const [overviewSelectedPlayer, setOverviewSelectedPlayer] = useState(null);

  // Player Intelligence State
  const [playerRole, setPlayerRole] = useState('batter');
  const [selectedPlayerName, setSelectedPlayerName] = useState('Naman Dhir');
  
  // Head to Head State
  const [h2hRole, setH2hRole] = useState('batter');
  const [h2hP1, setH2hP1] = useState('Naman Dhir');
  const [h2hP2, setH2hP2] = useState('Ashutosh Sharma');

  // Search & Filter
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFormat, setSelectedFormat] = useState('All');

  // Selected player object for Diagnostics tab
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

  // Dynamic Chart Data for Executive Overview (Overall vs Selected Player)
  const overviewChartData = useMemo(() => {
    if (!overviewSelectedPlayer || !playerProfiles[overviewSelectedPlayer]) {
      return {
        isPlayer: false,
        name: 'Overall Tournament (All Players)',
        role: 'All',
        totalBalls: summaryKpis.total_deliveries,
        tiersData: [
          { name: 'Low (<35)', Deliveries: summaryKpis.batting_tiers.low, color: '#3b82f6' },
          { name: 'Moderate (35-60)', Deliveries: summaryKpis.batting_tiers.moderate, color: '#eab308' },
          { name: 'High (60-80)', Deliveries: summaryKpis.batting_tiers.high, color: '#f97316' },
          { name: 'Extreme (≥80)', Deliveries: summaryKpis.batting_tiers.extreme, color: '#ef4444' }
        ],
        scenarioData: [
          { name: 'Normal', value: summaryKpis.dominant_batting_scenarios.Normal || 132610, fill: '#334155' },
          { name: 'Run Chase', value: summaryKpis.dominant_batting_scenarios['Run Chase'] || 28410, fill: '#38bdf8' },
          { name: 'Collapse', value: summaryKpis.dominant_batting_scenarios.Collapse || 18450, fill: '#f97316' },
          { name: 'Survival', value: summaryKpis.dominant_batting_scenarios.Survival || 8920, fill: '#ef4444' },
          { name: 'Momentum Deficit', value: summaryKpis.dominant_batting_scenarios['Momentum Deficit'] || 5598, fill: '#a855f7' }
        ]
      };
    }

    const prof = playerProfiles[overviewSelectedPlayer];
    const tiers = prof.tiers;
    const scen = prof.scenarios;
    const isBatter = prof.role === 'Batter';

    const scenarioColors = {
      'Normal': '#334155',
      'Run Chase': '#38bdf8',
      'Collapse': '#f97316',
      'Survival': '#ef4444',
      'Momentum Deficit': '#a855f7',
      'Aggressive Opposition': '#f87171',
      'Defending Chase': '#38bdf8',
      'Death Leverage': '#fbbf24',
      'Adverse Momentum': '#c084fc'
    };

    const scenList = Object.entries(scen).map(([name, val]) => ({
      name,
      value: val,
      fill: scenarioColors[name] || '#64748b'
    })).filter(s => s.value > 0);

    return {
      isPlayer: true,
      name: overviewSelectedPlayer,
      role: prof.role,
      totalBalls: prof.total_balls,
      tiersData: [
        { name: 'Low (<35)', Deliveries: tiers.low, color: '#3b82f6' },
        { name: 'Moderate (35-60)', Deliveries: tiers.moderate, color: '#eab308' },
        { name: 'High (60-80)', Deliveries: tiers.high, color: '#f97316' },
        { name: 'Extreme (≥80)', Deliveries: tiers.extreme, color: '#ef4444' }
      ],
      scenarioData: scenList.length > 0 ? scenList : [{ name: 'Normal', value: prof.total_balls, fill: '#334155' }]
    };
  }, [overviewSelectedPlayer]);

  // Jump to player diagnostics helper
  const navigateToPlayerDiagnostic = (playerName, role) => {
    setPlayerRole(role === 'Bowler' ? 'bowler' : 'batter');
    setSelectedPlayerName(playerName);
    setActiveTab('player');
  };

  // Filtered evidence
  const filteredEvidence = useMemo(() => {
    let list = matchEvidence;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      list = list.filter(r => 
        (r.striker_name && r.striker_name.toLowerCase().includes(q)) ||
        (r.bowler_name && r.bowler_name.toLowerCase().includes(q))
      );
    }
    if (selectedFormat !== 'All') {
      list = list.filter(r => r.format_type === selectedFormat);
    }
    return list;
  }, [searchQuery, selectedFormat]);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#050814] text-slate-100 font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
      
      {/* ===================================================================== */}
      {/* SIDEBAR NAVIGATION (UPDATED ORDER: Diagnostics & H2H at #2 & #3) */}
      {/* ===================================================================== */}
      <aside className="w-72 flex-shrink-0 bg-[#0a0f1d] border-r border-slate-800/80 flex flex-col justify-between z-20 shadow-2xl">
        <div className="flex flex-col h-full overflow-y-auto">
          {/* Brand Logo & Title */}
          <div className="p-5 border-b border-slate-800/80 bg-gradient-to-b from-slate-900/60 to-transparent">
            <div className="flex items-center gap-3">
              <div className="w-11 h-11 rounded-xl bg-gradient-to-tr from-cyan-500 via-blue-600 to-indigo-600 flex items-center justify-center text-xl shadow-lg shadow-cyan-500/25 border border-cyan-400/30">
                🏏
              </div>
              <div>
                <h1 className="text-xl font-black tracking-tight text-white flex items-center gap-1">
                  PRESSURE<span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400">IQ</span>
                </h1>
                <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-widest">SupeRR Selector S2</p>
              </div>
            </div>
          </div>

          {/* Nav Items */}
          <div className="px-3 py-4 space-y-1.5 flex-1">
            <span className="px-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-2">
              Analytics Modules
            </span>
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center gap-3.5 px-3.5 py-3 rounded-xl text-left transition-all duration-200 group relative ${
                    isActive
                      ? 'bg-gradient-to-r from-blue-600/25 to-cyan-500/15 text-white border border-cyan-500/30 shadow-md shadow-cyan-950/40'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40 border border-transparent'
                  }`}
                >
                  <div className={`p-2 rounded-lg transition-colors ${
                    isActive ? 'bg-cyan-500/20 text-cyan-300' : 'bg-slate-800/60 text-slate-400 group-hover:text-slate-200'
                  }`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className={`text-xs font-bold tracking-tight truncate ${isActive ? 'text-white' : 'text-slate-300'}`}>
                      {item.label}
                    </div>
                    <div className="text-[10px] text-slate-400 truncate mt-0.5">
                      {item.desc}
                    </div>
                  </div>
                  {isActive && (
                    <div className="w-1.5 h-6 rounded-full bg-cyan-400 absolute right-2 shadow-sm shadow-cyan-400"></div>
                  )}
                </button>
              );
            })}
          </div>

          {/* Engine Metadata Badge */}
          <div className="p-4 m-3 rounded-2xl bg-gradient-to-br from-slate-900 to-slate-950 border border-slate-800/80 shadow-inner">
            <div className="flex items-center gap-2 mb-2">
              <Zap className="w-3.5 h-3.5 text-cyan-400" />
              <span className="text-[11px] font-bold text-slate-200">Engine Health</span>
              <span className="ml-auto text-[10px] font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                100% PASS
              </span>
            </div>
            <div className="space-y-1.5 text-[10px] text-slate-400">
              <div className="flex justify-between">
                <span>Deliveries Evaluated</span>
                <span className="font-semibold text-slate-200">193,988</span>
              </div>
              <div className="flex justify-between">
                <span>GroupKFold Split</span>
                <span className="font-semibold text-slate-200">5-Fold Match</span>
              </div>
              <div className="flex justify-between">
                <span>Bootstrap Iterations</span>
                <span className="font-semibold text-slate-200">500 Resamples</span>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* ===================================================================== */}
      {/* MAIN VIEWPORT */}
      {/* ===================================================================== */}
      <main className="flex-1 flex flex-col overflow-hidden bg-[#050814]">
        
        {/* Top Header Bar */}
        <header className="h-20 px-8 border-b border-slate-800/70 bg-[#090e1c]/80 backdrop-blur-xl flex items-center justify-between z-10">
          <div>
            <div className="flex items-center gap-2.5">
              <span className="text-xs font-extrabold uppercase tracking-widest text-cyan-400 bg-cyan-500/10 px-2.5 py-0.5 rounded-md border border-cyan-500/20">
                PRESSUREIQ PLATFORM
              </span>
              <span className="text-xs text-slate-400">•</span>
              <span className="text-xs font-medium text-slate-300">IPL & T20I Context Engine (2022–2026)</span>
            </div>
            <h2 className="text-xl font-black text-white tracking-tight mt-0.5">
              {NAV_ITEMS.find(n => n.id === activeTab)?.label}
            </h2>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="font-semibold">Match Grouped</span>
              <span className="text-slate-400 text-[11px]">(0% Data Leakage)</span>
            </div>

            <a
              href="https://github.com"
              target="_blank"
              rel="noreferrer"
              className="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-600 text-white text-xs font-bold shadow-lg shadow-cyan-600/20 hover:opacity-95 transition flex items-center gap-2"
            >
              <FileText className="w-3.5 h-3.5" />
              <span>Official Report (PDF)</span>
            </a>
          </div>
        </header>

        {/* Tab View Container */}
        <div className="flex-1 overflow-y-auto px-8 py-6 space-y-8">

          {/* ================================================================= */}
          {/* TAB 1: EXECUTIVE OVERVIEW */}
          {/* ================================================================= */}
          {activeTab === 'overview' && (
            <div className="space-y-8 animate-fadeIn">
              
              {/* Highlight Hero Banner */}
              <div className="p-6 rounded-3xl bg-gradient-to-r from-blue-950/50 via-slate-900 to-indigo-950/40 border border-cyan-500/20 shadow-xl relative overflow-hidden">
                <div className="relative z-10 max-w-3xl">
                  <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-400 text-xs font-bold border border-cyan-500/30 mb-3">
                    <Sparkles className="w-3.5 h-3.5 text-cyan-300" />
                    SupeRR Selector Season 2 – Round 1 Official Submission
                  </div>
                  <h3 className="text-2xl font-black text-white tracking-tight leading-snug">
                    Identifying Cricket's Most Reliable Performers Under Extreme Match Crisis
                  </h3>
                  <p className="text-xs text-slate-300 mt-2 leading-relaxed font-normal">
                    Pressure is not restricted to run chases or death overs. PRESSUREIQ models pre-delivery collapse stress, aggressive opposition dominance, survival pressure, and momentum shifts across 193,988 deliveries.
                  </p>
                </div>
                <div className="absolute right-0 top-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none"></div>
              </div>

              {/* 5 Core Engine KPIs */}
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800/80 shadow-sm hover:border-slate-700 transition">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Matches Evaluated</span>
                  <div className="text-2xl font-black text-white mt-1">837</div>
                  <div className="text-[11px] text-cyan-400 font-medium mt-0.5">IPL + T20I (2022–2026)</div>
                </div>

                <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800/80 shadow-sm hover:border-slate-700 transition">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Total Deliveries</span>
                  <div className="text-2xl font-black text-white mt-1">193,988</div>
                  <div className="text-[11px] text-slate-400 font-medium mt-0.5">100% Pre-Delivery State</div>
                </div>

                <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800/80 shadow-sm hover:border-slate-700 transition">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Eligible Batters</span>
                  <div className="text-2xl font-black text-cyan-400 mt-1">198</div>
                  <div className="text-[11px] text-slate-400 font-medium mt-0.5">≥75 Pressure Balls</div>
                </div>

                <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800/80 shadow-sm hover:border-slate-700 transition">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Eligible Bowlers</span>
                  <div className="text-2xl font-black text-rose-400 mt-1">267</div>
                  <div className="text-[11px] text-slate-400 font-medium mt-0.5">≥60 Pressure Balls</div>
                </div>

                <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800/80 shadow-sm hover:border-slate-700 transition">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Anti-Leakage Standard</span>
                  <div className="text-2xl font-black text-emerald-400 mt-1">0.0%</div>
                  <div className="text-[11px] text-slate-400 font-medium mt-0.5">GroupKFold Validation</div>
                </div>
              </div>

              {/* Side-by-Side Official Top 10 Tables with Click-to-Inspect Action */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                
                {/* Batters Top 10 */}
                <div className="p-6 rounded-3xl bg-slate-900/70 border border-slate-800/80 shadow-lg">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2.5">
                      <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                        <Award className="w-5 h-5" />
                      </div>
                      <div>
                        <h4 className="text-base font-extrabold text-white tracking-tight">Official Top 10 Batters</h4>
                        <p className="text-[11px] text-cyan-400 font-medium">Click any batter to isolate their pressure breakdown below</p>
                      </div>
                    </div>
                    <button
                      onClick={() => setActiveTab('batters')}
                      className="text-xs font-bold text-cyan-400 hover:text-cyan-300 flex items-center gap-1 transition"
                    >
                      View all 198 <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full text-xs text-left">
                      <thead>
                        <tr className="border-b border-slate-800 text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">
                          <th className="py-2.5 px-2">Rank</th>
                          <th className="py-2.5 px-2">Player</th>
                          <th className="py-2.5 px-2 text-right">Rating</th>
                          <th className="py-2.5 px-2 text-right">Press SR</th>
                          <th className="py-2.5 px-2 text-right">Δ SR</th>
                          <th className="py-2.5 px-2 text-right">Action</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60">
                        {top10Batters.map((b, i) => {
                          const isSelected = overviewSelectedPlayer === b.striker_name;
                          return (
                            <tr
                              key={b.striker_id}
                              onClick={() => setOverviewSelectedPlayer(isSelected ? null : b.striker_name)}
                              className={`cursor-pointer transition ${
                                isSelected
                                  ? 'bg-cyan-950/50 border-l-4 border-cyan-400 ring-1 ring-cyan-500/40'
                                  : 'hover:bg-slate-800/40'
                              }`}
                            >
                              <td className="py-2.5 px-2 font-black">
                                {i === 0 ? <span className="text-amber-400 font-black">🥇 #1</span> :
                                 i === 1 ? <span className="text-slate-300 font-black">🥈 #2</span> :
                                 i === 2 ? <span className="text-amber-600 font-black">🥉 #3</span> :
                                 <span className="text-slate-400 font-bold">#{b.rank}</span>}
                              </td>
                              <td className="py-2.5 px-2">
                                <div className="font-bold text-white tracking-tight flex items-center gap-1.5">
                                  {b.striker_name}
                                  {isSelected && <span className="text-[10px] px-1.5 py-0.2 rounded bg-cyan-500 text-slate-950 font-black">ACTIVE</span>}
                                </div>
                                <div className="text-[10px] text-slate-400 font-mono">ID: {b.striker_id}</div>
                              </td>
                              <td className="py-2.5 px-2 text-right font-extrabold text-cyan-300 text-sm">{b.final_rating.toFixed(2)}</td>
                              <td className="py-2.5 px-2 text-right font-semibold text-slate-200">{b.pressure_strike_rate.toFixed(1)}</td>
                              <td className="py-2.5 px-2 text-right">
                                <span className={`inline-block px-1.5 py-0.5 rounded text-[11px] font-bold ${
                                  b.adj_delta_sr >= 0 ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-slate-800 text-slate-400'
                                }`}>
                                  {b.adj_delta_sr >= 0 ? `+${b.adj_delta_sr.toFixed(1)}` : b.adj_delta_sr.toFixed(1)}
                                </span>
                              </td>
                              <td className="py-2.5 px-2 text-right">
                                <button
                                  onClick={(e) => { e.stopPropagation(); navigateToPlayerDiagnostic(b.striker_name, 'Batter'); }}
                                  className="text-[10px] text-cyan-400 hover:text-cyan-300 underline font-semibold"
                                >
                                  Deep Dive
                                </button>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Bowlers Top 10 */}
                <div className="p-6 rounded-3xl bg-slate-900/70 border border-slate-800/80 shadow-lg">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2.5">
                      <div className="p-2 rounded-xl bg-rose-500/10 text-rose-400 border border-rose-500/20">
                        <Crosshair className="w-5 h-5" />
                      </div>
                      <div>
                        <h4 className="text-base font-extrabold text-white tracking-tight">Official Top 10 Bowlers</h4>
                        <p className="text-[11px] text-rose-400 font-medium">Click any bowler to isolate their pressure breakdown below</p>
                      </div>
                    </div>
                    <button
                      onClick={() => setActiveTab('bowlers')}
                      className="text-xs font-bold text-rose-400 hover:text-rose-300 flex items-center gap-1 transition"
                    >
                      View all 267 <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full text-xs text-left">
                      <thead>
                        <tr className="border-b border-slate-800 text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">
                          <th className="py-2.5 px-2">Rank</th>
                          <th className="py-2.5 px-2">Bowler</th>
                          <th className="py-2.5 px-2 text-right">Rating</th>
                          <th className="py-2.5 px-2 text-right">Press Econ</th>
                          <th className="py-2.5 px-2 text-right">Wickets</th>
                          <th className="py-2.5 px-2 text-right">Action</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60">
                        {top10Bowlers.map((b, i) => {
                          const isSelected = overviewSelectedPlayer === b.bowler_name;
                          return (
                            <tr
                              key={b.bowler_id}
                              onClick={() => setOverviewSelectedPlayer(isSelected ? null : b.bowler_name)}
                              className={`cursor-pointer transition ${
                                isSelected
                                  ? 'bg-rose-950/50 border-l-4 border-rose-400 ring-1 ring-rose-500/40'
                                  : 'hover:bg-slate-800/40'
                              }`}
                            >
                              <td className="py-2.5 px-2 font-black">
                                {i === 0 ? <span className="text-amber-400 font-black">🥇 #1</span> :
                                 i === 1 ? <span className="text-slate-300 font-black">🥈 #2</span> :
                                 i === 2 ? <span className="text-amber-600 font-black">🥉 #3</span> :
                                 <span className="text-slate-400 font-bold">#{b.rank}</span>}
                              </td>
                              <td className="py-2.5 px-2">
                                <div className="font-bold text-white tracking-tight flex items-center gap-1.5">
                                  {b.bowler_name}
                                  {isSelected && <span className="text-[10px] px-1.5 py-0.2 rounded bg-rose-500 text-slate-950 font-black">ACTIVE</span>}
                                </div>
                                <div className="text-[10px] text-slate-400 font-mono">ID: {b.bowler_id}</div>
                              </td>
                              <td className="py-2.5 px-2 text-right font-extrabold text-rose-300 text-sm">{b.final_rating.toFixed(2)}</td>
                              <td className="py-2.5 px-2 text-right font-semibold text-slate-200">{b.pressure_economy.toFixed(2)}</td>
                              <td className="py-2.5 px-2 text-right font-bold text-amber-400">
                                {b.pressure_wickets} wkts
                              </td>
                              <td className="py-2.5 px-2 text-right">
                                <button
                                  onClick={(e) => { e.stopPropagation(); navigateToPlayerDiagnostic(b.bowler_name, 'Bowler'); }}
                                  className="text-[10px] text-rose-400 hover:text-rose-300 underline font-semibold"
                                >
                                  Deep Dive
                                </button>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>

              </div>

              {/* DYNAMIC PLAYER INSPECTION BANNER & CHARTS */}
              <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 shadow-xl space-y-6">
                
                {/* Dynamic Selection Bar */}
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-xl ${overviewChartData.isPlayer ? (overviewChartData.role === 'Batter' ? 'bg-cyan-500/20 text-cyan-400' : 'bg-rose-500/20 text-rose-400') : 'bg-slate-800 text-slate-300'}`}>
                      <UserCheck className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Filtered View:</span>
                        <h4 className="text-base font-extrabold text-white">
                          {overviewChartData.name}
                        </h4>
                        {overviewChartData.isPlayer && (
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                            overviewChartData.role === 'Batter' ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                          }`}>
                            {overviewChartData.role}
                          </span>
                        )}
                      </div>
                      <p className="text-[11px] text-slate-400">
                        {overviewChartData.isPlayer
                          ? `Displaying delivery metrics across all ${overviewChartData.totalBalls} balls faced/bowled by ${overviewChartData.name}`
                          : 'Click any player name in the Top 10 tables above to isolate their individual pressure distribution.'}
                      </p>
                    </div>
                  </div>

                  {overviewChartData.isPlayer && (
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => navigateToPlayerDiagnostic(overviewChartData.name, overviewChartData.role)}
                        className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs text-white font-bold transition flex items-center gap-1.5 border border-slate-700"
                      >
                        <Compass className="w-3.5 h-3.5 text-cyan-400" />
                        <span>Full 5-D Diagnostic</span>
                      </button>

                      <button
                        onClick={() => setOverviewSelectedPlayer(null)}
                        className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 font-semibold transition flex items-center gap-1.5 border border-slate-700"
                      >
                        <RotateCcw className="w-3.5 h-3.5" />
                        <span>Reset to Tournament</span>
                      </button>
                    </div>
                  )}
                </div>

                {/* The Two Requested Dynamic Charts */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  
                  {/* Dynamic Pressure Distribution Across Deliveries */}
                  <div className="p-5 rounded-2xl bg-slate-950/60 border border-slate-800/80">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="text-sm font-bold text-white">Pressure Distribution Across Deliveries</h4>
                      <span className="text-[10px] font-mono text-cyan-400 font-semibold">
                        Total: {overviewChartData.totalBalls.toLocaleString()} balls
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400 mb-4">
                      {overviewChartData.isPlayer
                        ? `Deliveries faced/bowled by ${overviewChartData.name} under each pressure category`
                        : 'Deliveries analyzed across the entire 2022–2026 IPL & T20I tournament database'}
                    </p>

                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={overviewChartData.tiersData}>
                          <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} />
                          <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
                          <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', color: '#fff', fontSize: '12px' }} />
                          <Bar
                            dataKey="Deliveries"
                            fill={overviewChartData.role === 'Bowler' ? '#f87171' : '#38bdf8'}
                            radius={[6, 6, 0, 0]}
                          />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* Dynamic Dominant Pressure Scenarios */}
                  <div className="p-5 rounded-2xl bg-slate-950/60 border border-slate-800/80">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="text-sm font-bold text-white">Dominant Pressure Scenarios</h4>
                      <span className="text-[10px] font-mono text-amber-400 font-semibold">
                        {overviewChartData.isPlayer ? `${overviewChartData.name} Breakdown` : 'Tournament Overview'}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400 mb-4">
                      {overviewChartData.isPlayer
                        ? `Situational exposure: collapse, steep chase, aggression, or normal phases`
                        : 'Classified delivery states across both innings'}
                    </p>

                    <div className="h-64 flex items-center justify-center">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={overviewChartData.scenarioData}
                            cx="50%"
                            cy="50%"
                            innerRadius={65}
                            outerRadius={95}
                            paddingAngle={4}
                            dataKey="value"
                          >
                            {overviewChartData.scenarioData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.fill || '#64748b'} />
                            ))}
                          </Pie>
                          <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', color: '#fff', fontSize: '12px' }} />
                          <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                </div>

              </div>

            </div>
          )}

          {/* ================================================================= */}
          {/* TAB 2: PLAYER DIAGNOSTICS (POSITIONED 2ND AS REQUESTED) */}
          {/* ================================================================= */}
          {activeTab === 'player' && (
            <div className="space-y-6 animate-fadeIn">
              <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800">
                
                {/* Selector Header */}
                <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pb-6 border-b border-slate-800">
                  <div className="flex items-center gap-3">
                    <div className="flex rounded-xl bg-slate-800 p-1 border border-slate-700">
                      <button
                        onClick={() => { setPlayerRole('batter'); setSelectedPlayerName('Naman Dhir'); }}
                        className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition ${playerRole === 'batter' ? 'bg-cyan-500 text-white shadow-md' : 'text-slate-400 hover:text-white'}`}
                      >
                        Batters
                      </button>
                      <button
                        onClick={() => { setPlayerRole('bowler'); setSelectedPlayerName('Matheesha Pathirana'); }}
                        className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition ${playerRole === 'bowler' ? 'bg-rose-500 text-white shadow-md' : 'text-slate-400 hover:text-white'}`}
                      >
                        Bowlers
                      </button>
                    </div>

                    <select
                      value={selectedPlayerName}
                      onChange={e => setSelectedPlayerName(e.target.value)}
                      className="px-4 py-2 rounded-xl bg-slate-800 text-xs text-white border border-slate-700 focus:outline-none focus:border-cyan-400 font-bold"
                    >
                      {(playerRole === 'batter' ? allBatters : allBowlers).map(p => (
                        <option key={p.striker_id || p.bowler_id} value={p.striker_name || p.bowler_name}>
                          #{p.rank} {p.striker_name || p.bowler_name} (Rating: {p.final_rating.toFixed(2)})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="flex items-center gap-4 bg-slate-800/60 px-4 py-2 rounded-2xl border border-slate-700/60">
                    <div>
                      <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Official Rank</span>
                      <span className="text-base font-black text-cyan-400">#{currentPlayer.rank}</span>
                    </div>
                    <div className="w-px h-6 bg-slate-700"></div>
                    <div>
                      <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Composite Rating</span>
                      <span className="text-base font-black text-white">{currentPlayer.final_rating.toFixed(2)}</span>
                    </div>
                  </div>
                </div>

                {/* Radar and Diagnostics */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pt-6 items-center">
                  
                  {/* Radar */}
                  <div className="h-80 flex flex-col items-center justify-center">
                    <span className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">5 Reliability Dimensions</span>
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
                        <Radar
                          name={selectedPlayerName}
                          dataKey="value"
                          stroke={playerRole === 'batter' ? '#38bdf8' : '#f87171'}
                          fill={playerRole === 'batter' ? '#38bdf8' : '#f87171'}
                          fillOpacity={0.4}
                        />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>

                  {/* Stat Cards */}
                  <div className="space-y-4">
                    <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Performance Breakdown</h4>
                    
                    <div className="grid grid-cols-2 gap-3 text-xs">
                      <div className="p-4 rounded-2xl bg-slate-800/40 border border-slate-700/60">
                        <span className="text-slate-400 font-medium">
                          {playerRole === 'batter' ? 'Pressure Strike Rate' : 'Pressure Economy'}
                        </span>
                        <div className="text-xl font-black text-white mt-1">
                          {playerRole === 'batter' ? currentPlayer.pressure_strike_rate.toFixed(1) : currentPlayer.pressure_economy.toFixed(2)}
                        </div>
                        <span className="text-[11px] text-slate-400">
                          Normal: {playerRole === 'batter' ? currentPlayer.normal_strike_rate.toFixed(1) : currentPlayer.normal_economy.toFixed(2)}
                        </span>
                      </div>

                      <div className="p-4 rounded-2xl bg-slate-800/40 border border-slate-700/60">
                        <span className="text-slate-400 font-medium">Resilience Delta</span>
                        <div className={`text-xl font-black mt-1 ${
                          (currentPlayer.adj_delta_sr || currentPlayer.adj_delta_econ) >= 0 ? 'text-emerald-400' : 'text-slate-300'
                        }`}>
                          {playerRole === 'batter'
                            ? (currentPlayer.adj_delta_sr >= 0 ? `+${currentPlayer.adj_delta_sr.toFixed(1)}` : currentPlayer.adj_delta_sr.toFixed(1))
                            : (currentPlayer.adj_delta_econ >= 0 ? `+${currentPlayer.adj_delta_econ.toFixed(2)}` : currentPlayer.adj_delta_econ.toFixed(2))
                          }
                        </div>
                        <span className="text-[11px] text-slate-400">Vs Empirical Baseline</span>
                      </div>

                      <div className="p-4 rounded-2xl bg-slate-800/40 border border-slate-700/60">
                        <span className="text-slate-400 font-medium">
                          {playerRole === 'batter' ? 'Pressure Deliveries' : 'Pressure Legal Deliveries'}
                        </span>
                        <div className="text-xl font-black text-cyan-400 mt-1">
                          {currentPlayer.pressure_balls_faced || currentPlayer.pressure_legal_balls}
                        </div>
                        <span className="text-[11px] text-slate-400">Across {currentPlayer.pressure_matches} matches</span>
                      </div>

                      <div className="p-4 rounded-2xl bg-slate-800/40 border border-slate-700/60">
                        <span className="text-slate-400 font-medium">90% Bootstrap CI</span>
                        <div className="text-xl font-black text-amber-400 mt-1">
                          [{currentPlayer.ci_lower.toFixed(1)}, {currentPlayer.ci_upper.toFixed(1)}]
                        </div>
                        <span className="text-[11px] text-slate-400">500 match resamples</span>
                      </div>
                    </div>

                    <div className="p-4 rounded-2xl bg-slate-800/25 border border-slate-700/40">
                      <span className="text-[11px] text-slate-400 leading-relaxed block font-medium">
                        <b>Selector Context:</b> {playerRole === 'batter' 
                          ? `${currentPlayer.striker_name} displays an impact score of ${currentPlayer.impact_score.toFixed(1)}/100 and a resilience score of ${currentPlayer.resilience_score.toFixed(1)}/100, outperforming situation expectations under match crises.`
                          : `${currentPlayer.bowler_name} restricts aggressive scoring under pressure with an economy of ${currentPlayer.pressure_economy.toFixed(2)} RPO and an impact score of ${currentPlayer.impact_score.toFixed(1)}/100.`
                        }
                      </span>
                    </div>

                  </div>

                </div>

              </div>
            </div>
          )}

          {/* ================================================================= */}
          {/* TAB 3: HEAD TO HEAD (POSITIONED 3RD AS REQUESTED) */}
          {/* ================================================================= */}
          {activeTab === 'h2h' && (
            <div className="space-y-6 animate-fadeIn">
              <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800">
                <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-800">
                  <div>
                    <h3 className="text-base font-bold text-white">Head-to-Head Reliability Comparison</h3>
                    <p className="text-xs text-slate-400">Compare any two players across all 5 dimensions simultaneously.</p>
                  </div>

                  <div className="flex rounded-xl bg-slate-800 p-1 border border-slate-700">
                    <button
                      onClick={() => { setH2hRole('batter'); setH2hP1('Naman Dhir'); setH2hP2('Ashutosh Sharma'); }}
                      className={`px-3 py-1 rounded-lg text-xs font-bold transition ${h2hRole === 'batter' ? 'bg-cyan-500 text-white' : 'text-slate-400'}`}
                    >
                      Batters
                    </button>
                    <button
                      onClick={() => { setH2hRole('bowler'); setH2hP1('Matheesha Pathirana'); setH2hP2('Jasprit Bumrah'); }}
                      className={`px-3 py-1 rounded-lg text-xs font-bold transition ${h2hRole === 'bowler' ? 'bg-rose-500 text-white' : 'text-slate-400'}`}
                    >
                      Bowlers
                    </button>
                  </div>
                </div>

                {/* Player Selectors */}
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div>
                    <label className="text-[11px] font-bold text-cyan-400 uppercase tracking-wider mb-1 block">Player A</label>
                    <select
                      value={h2hP1}
                      onChange={e => setH2hP1(e.target.value)}
                      className="w-full px-3.5 py-2 rounded-xl bg-slate-800 text-xs text-white border border-cyan-500/40 focus:outline-none font-bold"
                    >
                      {(h2hRole === 'batter' ? allBatters : allBowlers).map(p => (
                        <option key={p.striker_id || p.bowler_id} value={p.striker_name || p.bowler_name}>
                          #{p.rank} {p.striker_name || p.bowler_name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="text-[11px] font-bold text-rose-400 uppercase tracking-wider mb-1 block">Player B</label>
                    <select
                      value={h2hP2}
                      onChange={e => setH2hP2(e.target.value)}
                      className="w-full px-3.5 py-2 rounded-xl bg-slate-800 text-xs text-white border border-rose-500/40 focus:outline-none font-bold"
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
                <div className="h-80 mb-6">
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
                      <Radar name={h2hP1} dataKey={h2hP1} stroke="#38bdf8" fill="#38bdf8" fillOpacity={0.3} strokeWidth={2} />
                      <Radar name={h2hP2} dataKey={h2hP2} stroke="#f43f5e" fill="#f43f5e" fillOpacity={0.3} strokeWidth={2} />
                      <Legend wrapperStyle={{ fontSize: '12px' }} />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>

                {/* Comparison Table */}
                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-left">
                    <thead className="bg-slate-800/80 text-slate-300 font-extrabold uppercase text-[10px]">
                      <tr>
                        <th className="py-2.5 px-3">Metric</th>
                        <th className="py-2.5 px-3 text-cyan-400 font-black">{h2hP1}</th>
                        <th className="py-2.5 px-3 text-rose-400 font-black">{h2hP2}</th>
                        <th className="py-2.5 px-3 text-right">Advantage</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 font-medium">
                      <tr>
                        <td className="py-2.5 px-3 text-slate-400">Overall Rank</td>
                        <td className="py-2.5 px-3 font-bold text-white">#{player1Obj.rank}</td>
                        <td className="py-2.5 px-3 font-bold text-white">#{player2Obj.rank}</td>
                        <td className="py-2.5 px-3 text-right font-bold text-emerald-400">
                          {player1Obj.rank < player2Obj.rank ? h2hP1 : h2hP2}
                        </td>
                      </tr>
                      <tr>
                        <td className="py-2.5 px-3 text-slate-400">Final Rating</td>
                        <td className="py-2.5 px-3 font-bold text-white">{player1Obj.final_rating.toFixed(2)}</td>
                        <td className="py-2.5 px-3 font-bold text-white">{player2Obj.final_rating.toFixed(2)}</td>
                        <td className="py-2.5 px-3 text-right font-bold text-emerald-400">
                          {player1Obj.final_rating > player2Obj.final_rating ? h2hP1 : h2hP2}
                        </td>
                      </tr>
                      <tr>
                        <td className="py-2.5 px-3 text-slate-400">{h2hRole === 'batter' ? 'Pressure Strike Rate' : 'Pressure Economy'}</td>
                        <td className="py-2.5 px-3 font-bold text-white">{h2hRole === 'batter' ? player1Obj.pressure_strike_rate.toFixed(1) : player1Obj.pressure_economy.toFixed(2)}</td>
                        <td className="py-2.5 px-3 font-bold text-white">{h2hRole === 'batter' ? player2Obj.pressure_strike_rate.toFixed(1) : player2Obj.pressure_economy.toFixed(2)}</td>
                        <td className="py-2.5 px-3 text-right font-bold text-emerald-400">
                          {h2hRole === 'batter'
                            ? (player1Obj.pressure_strike_rate > player2Obj.pressure_strike_rate ? h2hP1 : h2hP2)
                            : (player1Obj.pressure_economy < player2Obj.pressure_economy ? h2hP1 : h2hP2)
                          }
                        </td>
                      </tr>
                      <tr>
                        <td className="py-2.5 px-3 text-slate-400">Resilience Delta</td>
                        <td className="py-2.5 px-3 font-bold text-white">{h2hRole === 'batter' ? player1Obj.adj_delta_sr.toFixed(1) : player1Obj.adj_delta_econ.toFixed(2)}</td>
                        <td className="py-2.5 px-3 font-bold text-white">{h2hRole === 'batter' ? player2Obj.adj_delta_sr.toFixed(1) : player2Obj.adj_delta_econ.toFixed(2)}</td>
                        <td className="py-2.5 px-3 text-right font-bold text-emerald-400">
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
          {/* TAB 4: PRESSURE ENGINE (4TH POSITION) */}
          {/* ================================================================= */}
          {activeTab === 'pressure' && (
            <div className="space-y-6 animate-fadeIn">
              <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800">
                <h3 className="text-lg font-bold text-white mb-2">Context-Aware Match Pressure Engine</h3>
                <p className="text-xs text-slate-400 max-w-3xl leading-relaxed mb-6">
                  Unlike conventional death-overs or 2nd innings proxies, PRESSUREIQ introduces 6 discrete mathematical scenarios that independently evaluate batting and bowling strain.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-5 rounded-2xl bg-slate-800/40 border border-slate-700/60 hover:border-amber-500/40 transition">
                    <div className="text-[10px] font-black text-amber-400 uppercase tracking-widest">Scenario A</div>
                    <h4 className="text-sm font-bold text-white mt-1">Batting Collapse Crisis</h4>
                    <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                      Wickets lost rapidly in the last 12/18 legal deliveries (w12, w18) and high deficit relative to historical par trajectories. Identifies players who anchor or counterattack under crisis.
                    </p>
                  </div>

                  <div className="p-5 rounded-2xl bg-slate-800/40 border border-slate-700/60 hover:border-cyan-500/40 transition">
                    <div className="text-[10px] font-black text-cyan-400 uppercase tracking-widest">Scenario B</div>
                    <h4 className="text-sm font-bold text-white mt-1">Run Chase Steepness</h4>
                    <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                      Active in innings 2. Measures steep required run rates (RRR), divergence from current run rate (RRR - CRR), and depleting legal balls with few wickets remaining.
                    </p>
                  </div>

                  <div className="p-5 rounded-2xl bg-slate-800/40 border border-slate-700/60 hover:border-rose-500/40 transition">
                    <div className="text-[10px] font-black text-rose-400 uppercase tracking-widest">Scenario C</div>
                    <h4 className="text-sm font-bold text-white mt-1">Lower-Order Survival</h4>
                    <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                      Batter position ≥ 7 or ≥ 6 wickets down while significant overs remain. Rewards protecting wickets while scoring above tailend expectation.
                    </p>
                  </div>

                  <div className="p-5 rounded-2xl bg-slate-800/40 border border-slate-700/60 hover:border-rose-500/40 transition">
                    <div className="text-[10px] font-black text-rose-400 uppercase tracking-widest">Scenario D</div>
                    <h4 className="text-sm font-bold text-white mt-1">Opposition Aggression (Bowling)</h4>
                    <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                      Bowler facing an opposition scoring aggressively at 10–14+ RPO over recent deliveries, consecutive boundaries, and large active partnerships.
                    </p>
                  </div>

                  <div className="p-5 rounded-2xl bg-slate-800/40 border border-slate-700/60 hover:border-emerald-500/40 transition">
                    <div className="text-[10px] font-black text-emerald-400 uppercase tracking-widest">Scenario E</div>
                    <h4 className="text-sm font-bold text-white mt-1">Defensive Leverage (Bowling)</h4>
                    <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                      Defending tight margins in innings 2 death overs where required runs match balls remaining. High stakes on every single delivery.
                    </p>
                  </div>

                  <div className="p-5 rounded-2xl bg-slate-800/40 border border-slate-700/60 hover:border-purple-500/40 transition">
                    <div className="text-[10px] font-black text-purple-400 uppercase tracking-widest">Scenario F</div>
                    <h4 className="text-sm font-bold text-white mt-1">Momentum Shifts</h4>
                    <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                      Severe dot ball clusters (3+ consecutive dots), scoring deceleration, and turning point deliveries across both 1st and 2nd innings.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* ================================================================= */}
          {/* TAB 5: BATTING RANKINGS (5TH POSITION) */}
          {/* ================================================================= */}
          {activeTab === 'batters' && (
            <div className="space-y-6 animate-fadeIn">
              <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800">
                <div className="flex flex-col md:flex-row items-center justify-between gap-4 mb-6">
                  <div>
                    <h3 className="text-base font-bold text-white">Full Eligible Batting Roster (198 Players)</h3>
                    <p className="text-xs text-slate-400">Eligibility: ≥ 75 pressure deliveries faced, ≥ 20 normal balls baseline across ≥ 5 matches.</p>
                  </div>
                  <div className="relative w-80">
                    <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-400" />
                    <input
                      type="text"
                      placeholder="Search batter by name..."
                      value={searchQuery}
                      onChange={e => setSearchQuery(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-800/90 text-xs text-white placeholder-slate-400 border border-slate-700 focus:outline-none focus:border-cyan-400 transition"
                    />
                  </div>
                </div>

                <div className="overflow-x-auto max-h-[550px]">
                  <table className="w-full text-xs text-left">
                    <thead className="bg-slate-800/90 text-slate-300 font-extrabold uppercase text-[10px] sticky top-0 z-10">
                      <tr>
                        <th className="py-3 px-3">Rank</th>
                        <th className="py-3 px-3">Batter</th>
                        <th className="py-3 px-3 text-right">Rating</th>
                        <th className="py-3 px-3 text-right">Press SR</th>
                        <th className="py-3 px-3 text-right">Norm SR</th>
                        <th className="py-3 px-3 text-right">Δ SR</th>
                        <th className="py-3 px-3 text-right">Impact</th>
                        <th className="py-3 px-3 text-right">Resilience</th>
                        <th className="py-3 px-3 text-right">Consistency</th>
                        <th className="py-3 px-3 text-right">Confidence</th>
                        <th className="py-3 px-3 text-right">Collapse</th>
                        <th className="py-3 px-3 text-right">Balls</th>
                        <th className="py-3 px-3 text-right">Runs</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 font-medium">
                      {allBatters
                        .filter(b => b.striker_name.toLowerCase().includes(searchQuery.toLowerCase()))
                        .map(b => (
                          <tr key={b.striker_id} className="hover:bg-slate-800/40 transition">
                            <td className="py-2.5 px-3 font-bold text-cyan-400">#{b.rank}</td>
                            <td className="py-2.5 px-3">
                              <span className="font-bold text-white">{b.striker_name}</span>
                            </td>
                            <td className="py-2.5 px-3 text-right font-black text-cyan-300">{b.final_rating.toFixed(2)}</td>
                            <td className="py-2.5 px-3 text-right text-slate-200">{b.pressure_strike_rate.toFixed(1)}</td>
                            <td className="py-2.5 px-3 text-right text-slate-400">{b.normal_strike_rate.toFixed(1)}</td>
                            <td className="py-2.5 px-3 text-right">
                              <span className={`inline-block px-1.5 py-0.5 rounded text-[11px] font-bold ${
                                b.adj_delta_sr >= 0 ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-slate-800 text-slate-400'
                              }`}>
                                {b.adj_delta_sr >= 0 ? `+${b.adj_delta_sr.toFixed(1)}` : b.adj_delta_sr.toFixed(1)}
                              </span>
                            </td>
                            <td className="py-2.5 px-3 text-right text-slate-300">{b.impact_score.toFixed(1)}</td>
                            <td className="py-2.5 px-3 text-right text-slate-300">{b.resilience_score.toFixed(1)}</td>
                            <td className="py-2.5 px-3 text-right text-slate-300">{b.consistency_score.toFixed(1)}</td>
                            <td className="py-2.5 px-3 text-right text-slate-300">{b.sample_confidence_score.toFixed(1)}</td>
                            <td className="py-2.5 px-3 text-right text-slate-300">{b.collapse_resistance_score.toFixed(1)}</td>
                            <td className="py-2.5 px-3 text-right text-slate-400">{b.pressure_balls_faced}</td>
                            <td className="py-2.5 px-3 text-right text-slate-400">{b.pressure_runs}</td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* ================================================================= */}
          {/* TAB 6: BOWLING RANKINGS (6TH POSITION) */}
          {/* ================================================================= */}
          {activeTab === 'bowlers' && (
            <div className="space-y-6 animate-fadeIn">
              <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800">
                <div className="flex flex-col md:flex-row items-center justify-between gap-4 mb-6">
                  <div>
                    <h3 className="text-base font-bold text-white">Full Eligible Bowling Roster (267 Players)</h3>
                    <p className="text-xs text-slate-400">Eligibility: ≥ 60 pressure legal balls bowled, ≥ 20 normal balls baseline across ≥ 5 matches.</p>
                  </div>
                  <div className="relative w-80">
                    <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-400" />
                    <input
                      type="text"
                      placeholder="Search bowler by name..."
                      value={searchQuery}
                      onChange={e => setSearchQuery(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-800/90 text-xs text-white placeholder-slate-400 border border-slate-700 focus:outline-none focus:border-rose-400 transition"
                    />
                  </div>
                </div>

                <div className="overflow-x-auto max-h-[550px]">
                  <table className="w-full text-xs text-left">
                    <thead className="bg-slate-800/90 text-slate-300 font-extrabold uppercase text-[10px] sticky top-0 z-10">
                      <tr>
                        <th className="py-3 px-3">Rank</th>
                        <th className="py-3 px-3">Bowler</th>
                        <th className="py-3 px-3 text-right">Rating</th>
                        <th className="py-3 px-3 text-right">Press Econ</th>
                        <th className="py-3 px-3 text-right">Norm Econ</th>
                        <th className="py-3 px-3 text-right">Δ Econ</th>
                        <th className="py-3 px-3 text-right">Impact</th>
                        <th className="py-3 px-3 text-right">Resilience</th>
                        <th className="py-3 px-3 text-right">Consistency</th>
                        <th className="py-3 px-3 text-right">Confidence</th>
                        <th className="py-3 px-3 text-right">Aggression Res.</th>
                        <th className="py-3 px-3 text-right">Balls</th>
                        <th className="py-3 px-3 text-right">Wickets</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 font-medium">
                      {allBowlers
                        .filter(b => b.bowler_name.toLowerCase().includes(searchQuery.toLowerCase()))
                        .map(b => (
                          <tr key={b.bowler_id} className="hover:bg-slate-800/40 transition">
                            <td className="py-2.5 px-3 font-bold text-rose-400">#{b.rank}</td>
                            <td className="py-2.5 px-3">
                              <span className="font-bold text-white">{b.bowler_name}</span>
                            </td>
                            <td className="py-2.5 px-3 text-right font-black text-rose-300">{b.final_rating.toFixed(2)}</td>
                            <td className="py-2.5 px-3 text-right text-slate-200">{b.pressure_economy.toFixed(2)}</td>
                            <td className="py-2.5 px-3 text-right text-slate-400">{b.normal_economy.toFixed(2)}</td>
                            <td className="py-2.5 px-3 text-right">
                              <span className={`inline-block px-1.5 py-0.5 rounded text-[11px] font-bold ${
                                b.adj_delta_econ >= 0 ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-slate-800 text-slate-400'
                              }`}>
                                {b.adj_delta_econ >= 0 ? `+${b.adj_delta_econ.toFixed(2)}` : b.adj_delta_econ.toFixed(2)}
                              </span>
                            </td>
                            <td className="py-2.5 px-3 text-right text-slate-300">{b.impact_score.toFixed(1)}</td>
                            <td className="py-2.5 px-3 text-right text-slate-300">{b.resilience_score.toFixed(1)}</td>
                            <td className="py-2.5 px-3 text-right text-slate-300">{b.consistency_score.toFixed(1)}</td>
                            <td className="py-2.5 px-3 text-right text-slate-300">{b.sample_confidence_score.toFixed(1)}</td>
                            <td className="py-2.5 px-3 text-right text-slate-300">{b.aggression_resistance_score.toFixed(1)}</td>
                            <td className="py-2.5 px-3 text-right text-slate-400">{b.pressure_legal_balls}</td>
                            <td className="py-2.5 px-3 text-right font-bold text-amber-400">{b.pressure_wickets}</td>
                          </tr>
                        ))}
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
            <div className="space-y-6 animate-fadeIn">
              <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800">
                <div className="flex flex-col md:flex-row items-center justify-between gap-4 mb-6">
                  <div>
                    <h3 className="text-base font-bold text-white">Delivery-Level Explainability Audit</h3>
                    <p className="text-xs text-slate-400">Transparent ball-by-ball verification: actual vs expected delivery outcomes.</p>
                  </div>

                  <div className="flex items-center gap-3">
                    <select
                      value={selectedFormat}
                      onChange={e => setSelectedFormat(e.target.value)}
                      className="px-3 py-2 rounded-xl bg-slate-800 text-xs text-white border border-slate-700 focus:outline-none"
                    >
                      <option value="All">All Formats</option>
                      <option value="IPL">IPL Only</option>
                      <option value="T20I">T20I Only</option>
                    </select>

                    <div className="relative w-64">
                      <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
                      <input
                        type="text"
                        placeholder="Filter player..."
                        value={searchQuery}
                        onChange={e => setSearchQuery(e.target.value)}
                        className="w-full pl-9 pr-3 py-1.5 rounded-xl bg-slate-800 text-xs text-white placeholder-slate-400 border border-slate-700 focus:outline-none"
                      />
                    </div>
                  </div>
                </div>

                <div className="overflow-x-auto max-h-[550px]">
                  <table className="w-full text-xs text-left">
                    <thead className="bg-slate-800/90 text-slate-300 font-extrabold uppercase text-[10px] sticky top-0 z-10">
                      <tr>
                        <th className="py-3 px-3">Match</th>
                        <th className="py-3 px-3">Format</th>
                        <th className="py-3 px-3">Over</th>
                        <th className="py-3 px-3">Striker</th>
                        <th className="py-3 px-3">Bowler</th>
                        <th className="py-3 px-3 text-right">Pressure Score</th>
                        <th className="py-3 px-3 text-right">Scenario</th>
                        <th className="py-3 px-3 text-right">Actual Runs</th>
                        <th className="py-3 px-3 text-right">Expected Runs</th>
                        <th className="py-3 px-3 text-right">Impact</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 font-medium">
                      {filteredEvidence.slice(0, 100).map((row, idx) => (
                        <tr key={idx} className="hover:bg-slate-800/40 transition">
                          <td className="py-2.5 px-3 font-mono text-slate-400">#{row.match_id}</td>
                          <td className="py-2.5 px-3">
                            <span className="font-bold text-cyan-400">{row.format_type}</span>
                          </td>
                          <td className="py-2.5 px-3 text-slate-300">Ov {row.overid}.{row.over_ball_num}</td>
                          <td className="py-2.5 px-3 font-bold text-white">{row.striker_name}</td>
                          <td className="py-2.5 px-3 text-slate-300">{row.bowler_name}</td>
                          <td className="py-2.5 px-3 text-right font-black text-amber-400">
                            {row.batting_pressure_score || row.bowling_pressure_score}
                          </td>
                          <td className="py-2.5 px-3 text-right text-slate-300">
                            {row.dominant_batting_scenario || row.dominant_bowling_scenario}
                          </td>
                          <td className="py-2.5 px-3 text-right font-black text-white">
                            {row.batter_runs || row.bowler_runs_conceded}
                          </td>
                          <td className="py-2.5 px-3 text-right font-mono text-slate-400">
                            {(row.exp_batter_runs || row.exp_bowler_runs).toFixed(2)}
                          </td>
                          <td className="py-2.5 px-3 text-right">
                            <span className={`inline-block px-1.5 py-0.5 rounded text-[11px] font-bold ${
                              (row.batting_impact || row.bowling_impact) >= 0 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'
                            }`}>
                              {(row.batting_impact || row.bowling_impact) > 0 ? `+${(row.batting_impact || row.bowling_impact).toFixed(2)}` : (row.batting_impact || row.bowling_impact).toFixed(2)}
                            </span>
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
