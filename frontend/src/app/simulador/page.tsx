'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import RegionSelector from '@/components/RegionSelector';
import PartyCard from '@/components/PartyCard';
import DhondtTable from '@/components/DhondtTable';
import WhatsAppButton from '@/components/WhatsAppButton';
import { calculateAntiVote, getParties } from '@/lib/api';
import { antiVoteMessage } from '@/lib/whatsapp';
import type { Party, AntiVoteResult } from '@/lib/types';
import { useEffect } from 'react';

type Step = 1 | 2 | 3;

export default function SimuladorPage() {
  const [step, setStep] = useState<Step>(1);
  const [region, setRegion] = useState('');
  const [parties, setParties] = useState<Party[]>([]);
  const [selectedParties, setSelectedParties] = useState<Set<string>>(new Set());
  const [result, setResult] = useState<AntiVoteResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    getParties()
      .then(setParties)
      .catch(() => {
        // Use placeholder data if API is not available
        setParties([
          { id: 'fp', name: 'Fuerza Popular', abbreviation: 'fp', color: '#FF6B00' },
          { id: 'rp', name: 'Renovación Popular', abbreviation: 'rp', color: '#1B3A6B' },
          { id: 'app', name: 'Alianza Para el Progreso', abbreviation: 'app', color: '#00529B' },
          { id: 'ap', name: 'Acción Popular', abbreviation: 'ap', color: '#E31937' },
          { id: 'pl', name: 'Perú Libre', abbreviation: 'pl', color: '#CC0000' },
          { id: 'pm', name: 'Partido Morado', abbreviation: 'pm', color: '#7B2D8E' },
          { id: 'jpp', name: 'Juntos por el Perú', abbreviation: 'jpp', color: '#DC143C' },
          { id: 'pod', name: 'Podemos Perú', abbreviation: 'pod', color: '#6F2DA8' },
          { id: 'avp', name: 'Avanza País', abbreviation: 'avp', color: '#FF0000' },
          { id: 'sc', name: 'Somos Perú', abbreviation: 'sc', color: '#FF6B00' },
          { id: 'an', name: 'Alianza Nacional', abbreviation: 'an', color: '#003366' },
          { id: 'fep', name: 'Frente Esperanza', abbreviation: 'fep', color: '#FFD700' },
        ]);
      });
  }, []);

  const toggleParty = (partyId: string) => {
    setSelectedParties((prev) => {
      const next = new Set(prev);
      if (next.has(partyId)) {
        next.delete(partyId);
      } else {
        next.add(partyId);
      }
      return next;
    });
  };

  const handleCalculate = async () => {
    if (!region || selectedParties.size === 0) return;
    setLoading(true);
    setError('');
    try {
      const res = await calculateAntiVote(region, Array.from(selectedParties));
      setResult(res);
      setStep(3);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al calcular. Intenta de nuevo.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <h1 className="text-3xl sm:text-4xl font-extrabold mb-2">
        🗳️ Simulador de <span className="text-[#D4AF37]">Voto Estratégico</span>
      </h1>
      <p className="text-gray-400 mb-8">
        Descubre cómo votar para que los partidos que rechazas NO ganen escaños en tu región.
      </p>

      {/* Progress */}
      <div className="flex items-center gap-2 mb-8">
        {[1, 2, 3].map((s) => (
          <div key={s} className="flex items-center gap-2">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-colors ${
                step >= s ? 'bg-[#D4AF37] text-gray-950' : 'bg-gray-800 text-gray-500'
              }`}
            >
              {s}
            </div>
            {s < 3 && (
              <div
                className={`w-12 h-0.5 transition-colors ${
                  step > s ? 'bg-[#D4AF37]' : 'bg-gray-800'
                }`}
              />
            )}
          </div>
        ))}
      </div>

      <AnimatePresence mode="wait">
        {/* Step 1: Region */}
        {step === 1 && (
          <motion.div
            key="step1"
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -30 }}
          >
            <h2 className="text-xl font-bold mb-4">¿En qué región votas?</h2>
            <RegionSelector value={region} onChange={setRegion} />
            <button
              onClick={() => region && setStep(2)}
              disabled={!region}
              className="mt-6 w-full sm:w-auto px-8 py-3 rounded-xl bg-[#D4AF37] text-gray-950 font-bold hover:bg-[#C4A030] disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              Siguiente
            </button>
          </motion.div>
        )}

        {/* Step 2: Select parties to reject */}
        {step === 2 && (
          <motion.div
            key="step2"
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -30 }}
          >
            <h2 className="text-xl font-bold mb-2">
              ¿A quiénes NO quieres en el Congreso?
            </h2>
            <p className="text-gray-400 text-sm mb-6">
              Selecciona uno o más partidos que quieres evitar.
            </p>
            <div className="grid sm:grid-cols-2 gap-3 mb-6">
              {parties.map((party) => (
                <PartyCard
                  key={party.id}
                  party={party}
                  selected={selectedParties.has(party.id)}
                  onToggle={toggleParty}
                />
              ))}
            </div>
            {error && (
              <p className="text-red-400 text-sm mb-4">{error}</p>
            )}
            <div className="flex gap-3">
              <button
                onClick={() => setStep(1)}
                className="px-6 py-3 rounded-xl border border-gray-700 text-gray-300 hover:border-gray-500 transition-colors"
              >
                Atrás
              </button>
              <button
                onClick={handleCalculate}
                disabled={selectedParties.size === 0 || loading}
                className="flex-1 sm:flex-none px-8 py-3 rounded-xl bg-[#D4AF37] text-gray-950 font-bold hover:bg-[#C4A030] disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? 'Calculando...' : 'Calcular voto estratégico'}
              </button>
            </div>
          </motion.div>
        )}

        {/* Step 3: Result */}
        {step === 3 && result && (
          <motion.div
            key="step3"
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -30 }}
          >
            <div className="bg-gradient-to-b from-[#D4AF37]/10 to-transparent border border-[#D4AF37]/30 rounded-2xl p-6 mb-8">
              <h2 className="text-xl font-bold mb-2">Tu voto estratégico</h2>
              <p className="text-gray-300 mb-4">{result.explanation}</p>
              <div className="bg-gray-900 rounded-xl p-4 mb-4">
                <p className="text-sm text-gray-400 mb-1">Recomendación para {result.region.name}:</p>
                <p className="text-2xl font-extrabold text-[#D4AF37]">
                  Vota por {result.recommended_party.name}
                </p>
              </div>
              {result.wasted_vote_risk > 0 && (
                <p className="text-sm text-amber-400">
                  ⚠️ Riesgo de voto desperdiciado si no votas estratégicamente: {result.wasted_vote_risk}%
                </p>
              )}
            </div>

            {/* D'Hondt Table */}
            {result.dhondt_table && result.dhondt_table.length > 0 && (
              <div className="mb-8">
                <h3 className="text-lg font-bold mb-3">Así funciona la cifra repartidora</h3>
                <DhondtTable rows={result.dhondt_table} totalSeats={result.region.seats} />
              </div>
            )}

            {/* WhatsApp */}
            <div className="text-center mb-6">
              <WhatsAppButton
                message={antiVoteMessage(
                  result.region.name,
                  result.rejected_parties.map((p) => p.name).join(', '),
                  result.recommended_party.name
                )}
                label="Compartir mi voto estratégico"
                size="lg"
              />
            </div>

            <div className="flex flex-wrap gap-3 justify-center">
              <button
                onClick={() => {
                  setStep(1);
                  setResult(null);
                  setSelectedParties(new Set());
                }}
                className="px-6 py-2.5 rounded-xl border border-gray-700 text-gray-300 hover:border-gray-500 transition-colors text-sm"
              >
                Volver a calcular
              </button>
              <Link
                href="/registrar"
                className="px-6 py-2.5 rounded-xl border border-[#D4AF37]/50 text-[#D4AF37] hover:bg-[#D4AF37]/10 transition-colors text-sm"
              >
                Recibir alertas cuando cambie
              </Link>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
