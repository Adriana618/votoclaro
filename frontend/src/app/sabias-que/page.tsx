'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import ShareCard from '@/components/ShareCard';
import { getFacts } from '@/lib/api';
import type { ShareableFact } from '@/lib/types';

const PLACEHOLDER_FACTS: ShareableFact[] = [
  {
    id: '1',
    text: '292 candidatos al Congreso 2026 tienen antecedentes penales registrados.',
    source: 'JNE - Plataforma Voto Informado',
    category: 'Seguridad',
    emoji: '🚨',
    share_text: '292 candidatos al Congreso 2026 tienen antecedentes penales registrados.',
  },
  {
    id: '2',
    text: '17 congresistas que votaron contra leyes anticorrupción buscan reelegirse en 2026.',
    source: 'Congreso de la República - Votaciones en Pleno',
    category: 'Política',
    emoji: '🏛️',
    share_text: '17 congresistas que votaron contra leyes anticorrupción buscan reelegirse en 2026.',
  },
  {
    id: '3',
    text: 'El 40% del Congreso actual tiene investigaciones o denuncias fiscales abiertas.',
    source: 'Ministerio Público - Fiscalía de la Nación',
    category: 'Justicia',
    emoji: '⚖️',
    share_text: 'El 40% del Congreso actual tiene investigaciones o denuncias fiscales abiertas.',
  },
  {
    id: '4',
    text: 'Viciar tu voto no es protesta: solo beneficia al partido con más votos en tu región.',
    source: 'Ley Orgánica de Elecciones - Art. 287',
    category: 'Educación cívica',
    emoji: '📋',
    share_text: 'Viciar tu voto no es protesta: solo beneficia al partido con más votos en tu región.',
  },
  {
    id: '5',
    text: 'En 2021, en 8 regiones un solo partido ganó más del 50% de escaños por la cifra repartidora.',
    source: 'ONPE - Resultados oficiales 2021',
    category: 'Datos electorales',
    emoji: '📊',
    share_text: 'En 2021, en 8 regiones un solo partido ganó más del 50% de escaños por la cifra repartidora.',
  },
  {
    id: '6',
    text: 'La cédula tiene 5 columnas: Presidente, Vicepresidentes, Congresistas, Parlamento Andino y Preferencial.',
    source: 'ONPE - Formato de cédula 2026',
    category: 'Educación cívica',
    emoji: '🗳️',
    share_text: 'La cédula de 2026 tiene 5 columnas que debes conocer antes de votar.',
  },
];

export default function SabiasQuePage() {
  const [facts, setFacts] = useState<ShareableFact[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getFacts()
      .then(setFacts)
      .catch(() => setFacts(PLACEHOLDER_FACTS))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center">
        <div className="animate-pulse text-[#D4AF37] text-xl">Cargando datos...</div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl sm:text-4xl font-extrabold mb-2">
          🔥 <span className="text-[#D4AF37]">¿Sabías que...?</span>
        </h1>
        <p className="text-gray-400 mb-8">
          Datos verificados que deberías conocer antes de votar. Comparte los que más te importen.
        </p>
      </motion.div>

      <div className="grid sm:grid-cols-2 gap-4">
        {facts.map((fact) => (
          <ShareCard key={fact.id} fact={fact} />
        ))}
      </div>
    </div>
  );
}
