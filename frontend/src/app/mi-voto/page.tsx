'use client';

import { useState, useSyncExternalStore } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import WhatsAppButton from '@/components/WhatsAppButton';
import { antiVoteMessage } from '@/lib/whatsapp';
import type { SavedVote } from '@/lib/types';

function getStoredVote(): SavedVote | null {
  if (typeof window === 'undefined') return null;
  try {
    const stored = localStorage.getItem('votoclaro_mi_voto');
    return stored ? JSON.parse(stored) : null;
  } catch {
    return null;
  }
}

const subscribe = (callback: () => void) => {
  window.addEventListener('storage', callback);
  return () => window.removeEventListener('storage', callback);
};

export default function MiVotoPage() {
  const savedVote = useSyncExternalStore(subscribe, getStoredVote, () => null);
  const [loading] = useState(false);

  if (loading) {
    return (
      <div className="max-w-lg mx-auto px-4 py-20 text-center">
        <div className="animate-pulse text-[#D4AF37]">Cargando...</div>
      </div>
    );
  }

  if (!savedVote) {
    return (
      <div className="max-w-lg mx-auto px-4 py-20 text-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <span className="text-5xl block mb-4">🗳️</span>
          <h1 className="text-2xl font-extrabold mb-2">Aún no tienes un voto guardado</h1>
          <p className="text-gray-400 mb-6">
            Usa el simulador para calcular tu voto estratégico y se guardará aquí.
          </p>
          <Link
            href="/simulador"
            className="inline-block px-6 py-3 rounded-xl bg-[#D4AF37] text-gray-950 font-bold hover:bg-[#C4A030] transition-colors"
          >
            Ir al simulador
          </Link>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="max-w-lg mx-auto px-4 py-12">
      <h1 className="text-3xl font-extrabold mb-2">
        🗳️ Mi <span className="text-[#D4AF37]">voto</span> estratégico
      </h1>
      <p className="text-gray-400 mb-8">Tu recomendación de voto actual.</p>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-b from-[#D4AF37]/10 to-transparent border border-[#D4AF37]/30 rounded-2xl p-6 mb-6"
      >
        <p className="text-sm text-gray-400 mb-1">Recomendación para {savedVote.region.name}</p>
        <p className="text-3xl font-extrabold text-[#D4AF37] mb-4">
          {savedVote.recommendation.name}
        </p>

        <div className="space-y-2 text-sm text-gray-400">
          <p>
            <span className="text-gray-500">Partidos a evitar:</span>{' '}
            {savedVote.anti_vote_parties.map((p) => p.name).join(', ')}
          </p>
          <p>
            <span className="text-gray-500">Última actualización:</span>{' '}
            {new Date(savedVote.last_updated).toLocaleDateString('es-PE', {
              day: 'numeric',
              month: 'long',
              year: 'numeric',
            })}
          </p>
        </div>
      </motion.div>

      <div className="flex flex-col gap-3">
        <WhatsAppButton
          message={antiVoteMessage(
            savedVote.region.name,
            savedVote.anti_vote_parties.map((p) => p.name).join(', '),
            savedVote.recommendation.name
          )}
          label="Compartir mi voto estratégico"
        />

        <Link
          href="/simulador"
          className="text-center px-6 py-3 rounded-xl border border-gray-700 text-gray-300 hover:border-[#D4AF37] hover:text-[#D4AF37] transition-colors"
        >
          Recalcular
        </Link>
      </div>
    </div>
  );
}
