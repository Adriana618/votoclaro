'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import RegionSelector from '@/components/RegionSelector';
import ControversyMeter from '@/components/ControversyMeter';
import WhatsAppButton from '@/components/WhatsAppButton';
import { getCandidatesControversial } from '@/lib/api';
import type { Candidate } from '@/lib/types';

export default function ControversialPage() {
  const [region, setRegion] = useState('');
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!region) return;
    let cancelled = false;
    const fetchData = async () => {
      try {
        const data = await getCandidatesControversial(region);
        if (!cancelled) setCandidates(data.slice(0, 10));
      } catch {
        if (!cancelled) setCandidates([]);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    setLoading(true);
    fetchData();
    return () => { cancelled = true; };
  }, [region]);

  const getMedalEmoji = (index: number): string => {
    if (index === 0) return '🥇';
    if (index === 1) return '🥈';
    if (index === 2) return '🥉';
    return `${index + 1}.`;
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <h1 className="text-3xl sm:text-4xl font-extrabold mb-2">
        🌡️ Ranking <span className="text-[#D4AF37]">Controversial</span>
      </h1>
      <p className="text-gray-400 mb-8">
        Los 10 candidatos más polémicos en tu región, basado en antecedentes verificados.
      </p>

      <RegionSelector value={region} onChange={setRegion} className="mb-8" />

      {loading ? (
        <div className="text-center py-12 text-gray-500 animate-pulse">Cargando ranking...</div>
      ) : candidates.length > 0 ? (
        <div className="space-y-4">
          {candidates.map((candidate, i) => (
            <motion.div
              key={candidate.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.08 }}
              className="bg-gray-900 border border-gray-800 rounded-2xl p-5"
            >
              <div className="flex items-start gap-4">
                <span className="text-2xl mt-1">{getMedalEmoji(i)}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-bold text-white text-lg">{candidate.name}</h3>
                    {candidate.has_criminal_record && (
                      <span className="text-xs bg-red-500/20 text-red-400 px-2 py-0.5 rounded-full">
                        Antecedentes
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-500 mb-3">
                    {candidate.party?.name || 'Partido'} &bull; Posición #{candidate.position}
                  </p>
                  <ControversyMeter score={candidate.controversy_score} />
                  {candidate.controversy_reason && (
                    <p className="text-sm text-gray-400 mt-2">
                      {candidate.controversy_reason}
                    </p>
                  )}
                </div>
              </div>
            </motion.div>
          ))}

          {/* Share */}
          <div className="text-center pt-4">
            <WhatsAppButton
              message={
                `🌡️ *Ranking Controversial - ${region}*\n\n` +
                candidates.slice(0, 5).map((c, i) =>
                  `${i + 1}. ${c.name} (${c.party?.name || '?'}) - ${c.controversy_score}/100`
                ).join('\n') +
                `\n\nVe el ranking completo en 👉 votoclaro.pe/controversial\n\n` +
                `_Que la ignorancia no gane las elecciones 🇵🇪_`
              }
              label="Compartir ranking"
            />
          </div>
        </div>
      ) : region ? (
        <div className="text-center py-12 text-gray-500">
          No se encontraron datos para esta región.
        </div>
      ) : (
        <div className="text-center py-12 text-gray-600">
          Selecciona una región para ver el ranking.
        </div>
      )}
    </div>
  );
}
