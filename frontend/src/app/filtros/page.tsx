'use client';

import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { getFilters, getCandidatesControversial } from '@/lib/api';
import type { SpicyFilter, Candidate } from '@/lib/types';

const CATEGORIES = [
  { id: 'seguridad', label: 'Seguridad', emoji: '🛡️' },
  { id: 'economia', label: 'Economía', emoji: '💰' },
  { id: 'social', label: 'Temas Sociales', emoji: '🤝' },
  { id: 'politica', label: 'Política', emoji: '🏛️' },
];

export default function FiltrosPage() {
  const [filters, setFilters] = useState<SpicyFilter[]>([]);
  const [activeFilters, setActiveFilters] = useState<Set<string>>(new Set());
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getFilters()
      .then(setFilters)
      .catch(() => {
        setFilters([
          { id: 'antecedentes', label: 'Antecedentes penales', category: 'seguridad' },
          { id: 'narcotrafico', label: 'Vínculos con narcotráfico', category: 'seguridad' },
          { id: 'corrupcion', label: 'Casos de corrupción', category: 'politica' },
          { id: 'evasion', label: 'Evasión tributaria', category: 'economia' },
          { id: 'violencia', label: 'Violencia familiar', category: 'social' },
          { id: 'transfuguismo', label: 'Transfuguismo', category: 'politica' },
          { id: 'deuda-sunat', label: 'Deuda con SUNAT', category: 'economia' },
          { id: 'anti-derechos', label: 'Anti-derechos humanos', category: 'social' },
        ]);
      });
  }, []);

  const prevFiltersRef = useRef(activeFilters);
  useEffect(() => {
    prevFiltersRef.current = activeFilters;
    if (activeFilters.size === 0) {
      setCandidates([]);
      return;
    }
    let cancelled = false;
    const fetchData = async () => {
      try {
        const data = await getCandidatesControversial(undefined, Array.from(activeFilters));
        if (!cancelled) setCandidates(data);
      } catch {
        if (!cancelled) setCandidates([]);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    setLoading(true);
    fetchData();
    return () => { cancelled = true; };
  }, [activeFilters]);

  const toggleFilter = (filterId: string) => {
    setActiveFilters((prev) => {
      const next = new Set(prev);
      if (next.has(filterId)) next.delete(filterId);
      else next.add(filterId);
      return next;
    });
  };

  const filtersByCategory = CATEGORIES.map((cat) => ({
    ...cat,
    filters: filters.filter((f) => f.category === cat.id),
  }));

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <h1 className="text-3xl sm:text-4xl font-extrabold mb-2">
        🔍 Filtros <span className="text-[#D4AF37]">Picantes</span>
      </h1>
      <p className="text-gray-400 mb-8">
        Filtra partidos y candidatos por los temas que te importan.
      </p>

      {/* Filter categories */}
      <div className="space-y-6 mb-10">
        {filtersByCategory.map((cat) => (
          <div key={cat.id}>
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
              {cat.emoji} {cat.label}
            </h2>
            <div className="flex flex-wrap gap-2">
              {cat.filters.map((filter) => (
                <button
                  key={filter.id}
                  onClick={() => toggleFilter(filter.id)}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                    activeFilters.has(filter.id)
                      ? 'bg-[#D4AF37] text-gray-950'
                      : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                  }`}
                >
                  {filter.label}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Active filter count */}
      {activeFilters.size > 0 && (
        <div className="flex items-center justify-between mb-6">
          <p className="text-sm text-gray-400">
            {activeFilters.size} filtro{activeFilters.size > 1 ? 's' : ''} activo{activeFilters.size > 1 ? 's' : ''}
            {candidates.length > 0 && ` — ${candidates.length} resultado${candidates.length > 1 ? 's' : ''}`}
          </p>
          <button
            onClick={() => setActiveFilters(new Set())}
            className="text-sm text-[#D4AF37] hover:underline"
          >
            Limpiar filtros
          </button>
        </div>
      )}

      {/* Results */}
      {loading ? (
        <div className="text-center py-12 text-gray-500">Buscando...</div>
      ) : candidates.length > 0 ? (
        <div className="grid sm:grid-cols-2 gap-4">
          {candidates.map((candidate, i) => (
            <motion.div
              key={candidate.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="bg-gray-900 border border-gray-800 rounded-xl p-4"
            >
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-lg bg-gray-800 flex items-center justify-center text-sm font-bold text-gray-400">
                  {candidate.position}
                </div>
                <div>
                  <h3 className="font-bold text-white">{candidate.name}</h3>
                  <p className="text-sm text-gray-500">
                    {candidate.party?.name || 'Partido'} &bull; {candidate.region?.name || 'Región'}
                  </p>
                  {candidate.controversy_reason && (
                    <p className="text-xs text-red-400 mt-1">{candidate.controversy_reason}</p>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      ) : activeFilters.size > 0 ? (
        <div className="text-center py-12 text-gray-500">
          No se encontraron resultados con estos filtros.
        </div>
      ) : (
        <div className="text-center py-12 text-gray-600">
          Selecciona al menos un filtro para ver resultados.
        </div>
      )}
    </div>
  );
}
