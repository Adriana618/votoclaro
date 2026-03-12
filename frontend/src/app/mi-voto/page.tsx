'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import WhatsAppButton from '@/components/WhatsAppButton';
import RegionSelector from '@/components/RegionSelector';
import PartyCard from '@/components/PartyCard';
import { antiVoteMessage } from '@/lib/whatsapp';
import { lookupVote, saveVote, getParties } from '@/lib/api';
import type { Party } from '@/lib/types';

interface VoteData {
  region: { id: string; name: string; seats: number };
  recommended_party: { id: string; name: string; abbreviation: string; color?: string };
  rejected_parties: { id: string; name: string; abbreviation: string; color?: string }[];
  saved_at: string;
}

type Mode = 'lookup' | 'save-manual' | 'result';

export default function MiVotoPage() {
  const [mode, setMode] = useState<Mode>('lookup');

  // Lookup state
  const [dni, setDni] = useState('');
  const [digito, setDigito] = useState('');
  const [vote, setVote] = useState<VoteData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Manual save state
  const [parties, setParties] = useState<Party[]>([]);
  const [manualRegion, setManualRegion] = useState('');
  const [selectedRecommended, setSelectedRecommended] = useState('');
  const [selectedRejected, setSelectedRejected] = useState<Set<string>>(new Set());
  const [saveDni, setSaveDni] = useState('');
  const [saveDigito, setSaveDigito] = useState('');
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');

  const isValidDni = /^\d{8}$/.test(dni);
  const isValidDigito = /^[a-zA-Z0-9]$/.test(digito);

  useEffect(() => {
    if (mode === 'save-manual' && parties.length === 0) {
      getParties().then(setParties).catch(() => {});
    }
  }, [mode, parties.length]);

  const handleLookup = async () => {
    if (!isValidDni || !isValidDigito) return;
    setLoading(true);
    setError('');
    try {
      const data = await lookupVote(dni, digito);
      setVote(data);
      setMode('result');
    } catch (err) {
      setVote(null);
      setError(err instanceof Error ? err.message : 'No se encontró un voto guardado.');
    } finally {
      setLoading(false);
    }
  };

  const handleManualSave = async () => {
    if (saveDni.length !== 8 || !saveDigito || !manualRegion || !selectedRecommended) return;
    setSaveStatus('saving');
    const recParty = parties.find((p) => p.id === selectedRecommended);
    const rejParties = parties.filter((p) => selectedRejected.has(p.id));
    try {
      await saveVote({
        dni: saveDni,
        digito: saveDigito,
        region: { id: manualRegion, name: manualRegion, seats: 0 },
        recommended_party: recParty || { id: selectedRecommended, name: selectedRecommended, abbreviation: selectedRecommended },
        rejected_parties: rejParties,
        saved_at: new Date().toISOString(),
      });
      setSaveStatus('saved');
    } catch {
      setSaveStatus('error');
    }
  };

  const toggleRejected = (partyId: string) => {
    setSelectedRejected((prev) => {
      const next = new Set(prev);
      if (next.has(partyId)) next.delete(partyId);
      else next.add(partyId);
      return next;
    });
  };

  return (
    <div className="max-w-lg mx-auto px-4 py-12">
      <h1 className="text-3xl font-extrabold mb-2">
        🗳️ Mi <span className="text-[#D4AF37]">voto</span> estratégico
      </h1>
      <p className="text-gray-400 mb-8">
        Consulta o guarda tu voto estratégico para el día de las elecciones.
      </p>

      {/* Mode tabs */}
      {mode !== 'result' && (
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setMode('lookup')}
            className={`flex-1 py-2.5 rounded-xl text-sm font-semibold transition-colors ${
              mode === 'lookup' ? 'bg-[#D4AF37] text-gray-950' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            Consultar mi voto
          </button>
          <button
            onClick={() => setMode('save-manual')}
            className={`flex-1 py-2.5 rounded-xl text-sm font-semibold transition-colors ${
              mode === 'save-manual' ? 'bg-[#D4AF37] text-gray-950' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            Guardar mi voto
          </button>
        </div>
      )}

      {/* LOOKUP MODE */}
      {mode === 'lookup' && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <div className="space-y-4 mb-6">
            <div>
              <label htmlFor="lookup-dni" className="block text-sm font-medium text-gray-400 mb-2">
                DNI (8 dígitos)
              </label>
              <input
                id="lookup-dni"
                type="text"
                inputMode="numeric"
                maxLength={8}
                value={dni}
                onChange={(e) => { setDni(e.target.value.replace(/\D/g, '')); setError(''); }}
                placeholder="12345678"
                className="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder:text-gray-600 focus:outline-none focus:border-[#D4AF37] transition-colors"
              />
            </div>
            <div>
              <label htmlFor="lookup-digito" className="block text-sm font-medium text-gray-400 mb-2">
                Dígito verificador
              </label>
              <input
                id="lookup-digito"
                type="text"
                maxLength={1}
                value={digito}
                onChange={(e) => { setDigito(e.target.value.replace(/[^a-zA-Z0-9]/g, '')); setError(''); }}
                placeholder="A"
                className="w-20 bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-white text-center uppercase placeholder:text-gray-600 focus:outline-none focus:border-[#D4AF37] transition-colors"
              />
              <p className="text-xs text-gray-600 mt-1">Es la letra o número al costado de tu DNI.</p>
            </div>
          </div>
          <button
            onClick={handleLookup}
            disabled={!isValidDni || !isValidDigito || loading}
            className="w-full px-6 py-3 rounded-xl bg-[#D4AF37] text-gray-950 font-bold hover:bg-[#C4A030] disabled:opacity-40 transition-colors mb-4"
          >
            {loading ? 'Buscando...' : 'Consultar mi voto'}
          </button>

          {error && (
            <div className="text-center py-4">
              <p className="text-gray-400 mb-3">{error}</p>
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <Link
                  href="/simulador"
                  className="px-5 py-2.5 rounded-xl bg-[#D4AF37] text-gray-950 font-bold hover:bg-[#C4A030] transition-colors text-sm"
                >
                  Usar el simulador (recomendado)
                </Link>
                <button
                  onClick={() => setMode('save-manual')}
                  className="px-5 py-2.5 rounded-xl border border-gray-700 text-gray-300 hover:border-[#D4AF37] transition-colors text-sm"
                >
                  Guardar manualmente
                </button>
              </div>
            </div>
          )}

          <p className="text-xs text-gray-600 text-center mt-2">
            Tu DNI y dígito verificador solo se usan para buscar, nunca se almacenan en texto plano.
          </p>
        </motion.div>
      )}

      {/* MANUAL SAVE MODE */}
      {mode === 'save-manual' && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4 mb-6">
            <p className="text-sm text-amber-400">
              Te recomendamos usar el{' '}
              <Link href="/simulador" className="underline font-semibold">simulador</Link>
              {' '}para obtener una recomendación basada en datos reales de la cifra repartidora.
            </p>
          </div>

          <div className="space-y-5">
            {/* Region */}
            <RegionSelector value={manualRegion} onChange={setManualRegion} label="¿En qué región votas?" />

            {/* Recommended party */}
            {parties.length > 0 && (
              <div>
                <p className="text-sm font-medium text-gray-400 mb-2">¿Por quién vas a votar?</p>
                <div className="grid grid-cols-2 gap-2">
                  {parties.map((party) => (
                    <button
                      key={party.id}
                      onClick={() => setSelectedRecommended(party.id)}
                      className={`p-3 rounded-xl text-left text-sm transition-all border ${
                        selectedRecommended === party.id
                          ? 'border-[#D4AF37] bg-[#D4AF37]/10 text-white'
                          : 'border-gray-800 bg-gray-900 text-gray-400 hover:border-gray-600'
                      }`}
                    >
                      <span
                        className="inline-block w-3 h-3 rounded-full mr-2"
                        style={{ backgroundColor: party.color || '#666' }}
                      />
                      {party.name}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Rejected parties */}
            {parties.length > 0 && (
              <div>
                <p className="text-sm font-medium text-gray-400 mb-2">¿A quiénes rechazas? (opcional)</p>
                <div className="grid grid-cols-2 gap-2">
                  {parties.filter((p) => p.id !== selectedRecommended).map((party) => (
                    <button
                      key={party.id}
                      onClick={() => toggleRejected(party.id)}
                      className={`p-3 rounded-xl text-left text-sm transition-all border ${
                        selectedRejected.has(party.id)
                          ? 'border-red-500 bg-red-500/10 text-white'
                          : 'border-gray-800 bg-gray-900 text-gray-400 hover:border-gray-600'
                      }`}
                    >
                      <span
                        className="inline-block w-3 h-3 rounded-full mr-2"
                        style={{ backgroundColor: party.color || '#666' }}
                      />
                      {party.name}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* DNI + digito */}
            <div className="flex gap-3">
              <div className="flex-1">
                <label htmlFor="save-dni" className="block text-sm font-medium text-gray-400 mb-2">DNI</label>
                <input
                  id="save-dni"
                  type="text"
                  inputMode="numeric"
                  maxLength={8}
                  value={saveDni}
                  onChange={(e) => { setSaveDni(e.target.value.replace(/\D/g, '')); setSaveStatus('idle'); }}
                  placeholder="12345678"
                  className="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder:text-gray-600 focus:outline-none focus:border-[#D4AF37] transition-colors"
                />
              </div>
              <div className="w-24">
                <label htmlFor="save-digito" className="block text-sm font-medium text-gray-400 mb-2">Dígito</label>
                <input
                  id="save-digito"
                  type="text"
                  maxLength={1}
                  value={saveDigito}
                  onChange={(e) => { setSaveDigito(e.target.value.replace(/[^a-zA-Z0-9]/g, '')); setSaveStatus('idle'); }}
                  placeholder="A"
                  className="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-white text-center uppercase placeholder:text-gray-600 focus:outline-none focus:border-[#D4AF37] transition-colors"
                />
              </div>
            </div>

            <button
              onClick={handleManualSave}
              disabled={saveDni.length !== 8 || !saveDigito || !manualRegion || !selectedRecommended || saveStatus === 'saving'}
              className="w-full px-6 py-3 rounded-xl bg-[#D4AF37] text-gray-950 font-bold hover:bg-[#C4A030] disabled:opacity-40 transition-colors"
            >
              {saveStatus === 'saving' ? 'Guardando...' : saveStatus === 'saved' ? 'Guardado' : 'Guardar mi voto'}
            </button>

            {saveStatus === 'saved' && (
              <p className="text-sm text-green-400 text-center">Tu voto se guardó exitosamente. Podrás consultarlo con tu DNI y dígito verificador.</p>
            )}
            {saveStatus === 'error' && (
              <p className="text-sm text-red-400 text-center">Error al guardar. Intenta de nuevo.</p>
            )}

            <p className="text-xs text-gray-600 text-center">
              Tu DNI y dígito verificador se almacenan encriptados. Nunca los veremos en texto plano.
            </p>
          </div>
        </motion.div>
      )}

      {/* RESULT MODE */}
      {mode === 'result' && vote && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <div className="bg-gradient-to-b from-[#D4AF37]/10 to-transparent border border-[#D4AF37]/30 rounded-2xl p-6 mb-6">
            <p className="text-sm text-gray-400 mb-1">Recomendación para {vote.region.name}</p>
            <p className="text-3xl font-extrabold text-[#D4AF37] mb-4">
              {vote.recommended_party.name}
            </p>

            <div className="space-y-2 text-sm text-gray-400">
              <p>
                <span className="text-gray-500">Partidos a evitar:</span>{' '}
                {vote.rejected_parties.map((p) => p.name).join(', ') || 'Ninguno seleccionado'}
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
            <button
              onClick={() => { setMode('lookup'); setVote(null); setDni(''); setDigito(''); }}
              className="text-center px-6 py-3 rounded-xl border border-gray-700 text-gray-300 hover:border-[#D4AF37] hover:text-[#D4AF37] transition-colors"
            >
              Nueva consulta
            </button>
            <Link
              href="/simulador"
              className="text-center px-6 py-3 rounded-xl border border-gray-700 text-gray-300 hover:border-[#D4AF37] hover:text-[#D4AF37] transition-colors"
            >
              Recalcular con el simulador
            </Link>
          </div>
        </motion.div>
      )}
    </div>
  );
}
