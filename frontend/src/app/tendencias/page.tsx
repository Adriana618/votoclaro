'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import RegionSelector from '@/components/RegionSelector';
import { getTrends } from '@/lib/api';
import type { TrendData } from '@/lib/types';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts';

const COLORS = ['#D4AF37', '#D91023', '#3B82F6', '#10B981', '#8B5CF6', '#F59E0B', '#EC4899', '#6366F1'];

export default function TendenciasPage() {
  const [region, setRegion] = useState('');
  const [trends, setTrends] = useState<TrendData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!region) return;
    let cancelled = false;
    const fetchData = async () => {
      try {
        const data = await getTrends(region);
        if (!cancelled) {
          setTrends(data);
          setError('');
        }
      } catch {
        if (!cancelled) setError('No se pudieron cargar las tendencias. Intenta más tarde.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    setLoading(true);
    fetchData();
    return () => { cancelled = true; };
  }, [region]);

  const latestTrend = trends[trends.length - 1];

  const pieData = latestTrend
    ? Object.entries(latestTrend.anti_vote_distribution).map(([name, value]) => ({
        name,
        value,
      }))
    : [];

  const lineData = trends.map((t) => ({
    date: new Date(t.date).toLocaleDateString('es-PE', { month: 'short', day: 'numeric' }),
    ...t.anti_vote_distribution,
  }));

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <h1 className="text-3xl sm:text-4xl font-extrabold mb-2">
        📈 <span className="text-[#D4AF37]">Tendencias</span> colectivas
      </h1>
      <p className="text-gray-400 mb-8">
        Cómo están votando estratégicamente los usuarios de VotoClaro en cada región.
      </p>

      <RegionSelector value={region} onChange={setRegion} className="mb-8" />

      {loading ? (
        <div className="text-center py-12 text-gray-500 animate-pulse">Cargando tendencias...</div>
      ) : error ? (
        <div className="text-center py-12 text-red-400">{error}</div>
      ) : latestTrend ? (
        <div className="space-y-8">
          {/* Pie chart */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-gray-900 border border-gray-800 rounded-2xl p-6"
          >
            <h2 className="text-lg font-bold mb-4">Distribución de anti-voto</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  dataKey="value"
                  label={({ name, percent }: { name?: string; percent?: number }) => `${name ?? ''} ${((percent ?? 0) * 100).toFixed(0)}%`}
                >
                  {pieData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Top rejected */}
          {latestTrend.top_rejected && latestTrend.top_rejected.length > 0 && (
            <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
              <h2 className="text-lg font-bold mb-4">Partidos más rechazados</h2>
              <div className="space-y-3">
                {latestTrend.top_rejected.map((party, i) => (
                  <div key={party.id} className="flex items-center gap-3">
                    <span className="text-lg font-bold text-gray-600 w-6">#{i + 1}</span>
                    <div
                      className="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold"
                      style={{ backgroundColor: party.color || COLORS[i] }}
                    >
                      {party.abbreviation?.slice(0, 2)}
                    </div>
                    <span className="text-white font-medium">{party.name}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Trend over time */}
          {lineData.length > 1 && (
            <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
              <h2 className="text-lg font-bold mb-4">Tendencia en el tiempo</h2>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={lineData}>
                  <XAxis dataKey="date" tick={{ fill: '#9CA3AF', fontSize: 12 }} />
                  <YAxis tick={{ fill: '#9CA3AF', fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: 8 }}
                    labelStyle={{ color: '#E5E7EB' }}
                  />
                  {pieData.map((entry, i) => (
                    <Line
                      key={entry.name}
                      type="monotone"
                      dataKey={entry.name}
                      stroke={COLORS[i % COLORS.length]}
                      strokeWidth={2}
                      dot={false}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      ) : region ? (
        <div className="text-center py-12 text-gray-500">
          No hay datos disponibles para esta región aún.
        </div>
      ) : (
        <div className="text-center py-12 text-gray-600">
          Selecciona una región para ver las tendencias.
        </div>
      )}
    </div>
  );
}
