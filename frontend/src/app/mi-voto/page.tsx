'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import WhatsAppButton from '@/components/WhatsAppButton';
import { antiVoteMessage } from '@/lib/whatsapp';
import { lookupVote } from '@/lib/api';

interface VoteData {
  region: { id: string; name: string; seats: number };
  recommended_party: { id: string; name: string; abbreviation: string; color?: string };
  rejected_parties: { id: string; name: string; abbreviation: string; color?: string }[];
  saved_at: string;
}

export default function MiVotoPage() {
  const [dni, setDni] = useState('');
  const [vote, setVote] = useState<VoteData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searched, setSearched] = useState(false);

  const isValidDni = /^\d{8}$/.test(dni);

  const handleLookup = async () => {
    if (!isValidDni) return;
    setLoading(true);
    setError('');
    try {
      const data = await lookupVote(dni);
      setVote(data);
      setSearched(true);
    } catch (err) {
      setVote(null);
      setSearched(true);
      setError(err instanceof Error ? err.message : 'No se encontró un voto guardado.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-lg mx-auto px-4 py-12">
      <h1 className="text-3xl font-extrabold mb-2">
        🗳️ Mi <span className="text-[#D4AF37]">voto</span> estratégico
      </h1>
      <p className="text-gray-400 mb-8">
        Ingresa tu DNI para consultar tu voto estratégico guardado.
      </p>

      {/* DNI lookup */}
      <div className="mb-8">
        <div className="flex gap-3">
          <input
            type="text"
            inputMode="numeric"
            maxLength={8}
            value={dni}
            onChange={(e) => { setDni(e.target.value.replace(/\D/g, '')); setError(''); setSearched(false); }}
            placeholder="Tu DNI (8 dígitos)"
            onKeyDown={(e) => e.key === 'Enter' && handleLookup()}
            className="flex-1 bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder:text-gray-600 focus:outline-none focus:border-[#D4AF37] focus:ring-1 focus:ring-[#D4AF37] transition-colors"
          />
          <button
            onClick={handleLookup}
            disabled={!isValidDni || loading}
            className="px-6 py-3 rounded-xl bg-[#D4AF37] text-gray-950 font-bold hover:bg-[#C4A030] disabled:opacity-40 transition-colors"
          >
            {loading ? 'Buscando...' : 'Buscar'}
          </button>
        </div>
        <p className="text-xs text-gray-600 mt-2">Tu DNI solo se usa para buscar, no se almacena en texto plano.</p>
      </div>

      {/* Result */}
      {vote && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="bg-gradient-to-b from-[#D4AF37]/10 to-transparent border border-[#D4AF37]/30 rounded-2xl p-6 mb-6">
            <p className="text-sm text-gray-400 mb-1">Recomendación para {vote.region.name}</p>
            <p className="text-3xl font-extrabold text-[#D4AF37] mb-4">
              {vote.recommended_party.name}
            </p>

            <div className="space-y-2 text-sm text-gray-400">
              <p>
                <span className="text-gray-500">Partidos a evitar:</span>{' '}
                {vote.rejected_parties.map((p) => p.name).join(', ')}
              </p>
              {vote.saved_at && (
                <p>
                  <span className="text-gray-500">Guardado:</span>{' '}
                  {new Date(vote.saved_at).toLocaleDateString('es-PE', {
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric',
                  })}
                </p>
              )}
            </div>
          </div>

          <div className="flex flex-col gap-3">
            <WhatsAppButton
              message={antiVoteMessage(
                vote.region.name,
                vote.rejected_parties.map((p) => p.name).join(', '),
                vote.recommended_party.name
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
        </motion.div>
      )}

      {/* Not found */}
      {searched && !vote && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-8"
        >
          <span className="text-4xl block mb-4">🗳️</span>
          <h2 className="text-xl font-bold mb-2">No tienes un voto guardado</h2>
          <p className="text-gray-400 mb-6">
            {error || 'Usa el simulador para calcular tu voto estratégico y guárdalo con tu DNI.'}
          </p>
          <Link
            href="/simulador"
            className="inline-block px-6 py-3 rounded-xl bg-[#D4AF37] text-gray-950 font-bold hover:bg-[#C4A030] transition-colors"
          >
            Ir al simulador
          </Link>
        </motion.div>
      )}

      {/* Initial state */}
      {!searched && !vote && (
        <div className="text-center py-8 text-gray-600">
          <p>Ingresa tu DNI arriba para consultar tu voto guardado.</p>
          <p className="mt-2 text-sm">
            ¿Aún no tienes uno?{' '}
            <Link href="/simulador" className="text-[#D4AF37] hover:underline">
              Calcula tu voto estratégico
            </Link>
          </p>
        </div>
      )}
    </div>
  );
}
