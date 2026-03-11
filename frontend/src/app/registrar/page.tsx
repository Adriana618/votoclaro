'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import RegionSelector from '@/components/RegionSelector';
import { registerDni } from '@/lib/api';
import { Shield, Lock, Bell } from 'lucide-react';

export default function RegistrarPage() {
  const [dni, setDni] = useState('');
  const [region, setRegion] = useState('');
  const [whatsapp, setWhatsapp] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const isValidDni = /^\d{8}$/.test(dni);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isValidDni || !region) return;

    setLoading(true);
    setError('');
    try {
      await registerDni({ dni, region_id: region, whatsapp: whatsapp || undefined });
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al registrar. Intenta de nuevo.');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="max-w-lg mx-auto px-4 py-20 text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <span className="text-5xl block mb-4">✅</span>
          <h1 className="text-2xl font-extrabold mb-2">Registro exitoso</h1>
          <p className="text-gray-400 mb-6">
            Te avisaremos cuando la estrategia de voto cambie en tu región.
          </p>
          <a
            href="/simulador"
            className="inline-block px-6 py-3 rounded-xl bg-[#D4AF37] text-gray-950 font-bold hover:bg-[#C4A030] transition-colors"
          >
            Ir al simulador
          </a>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="max-w-lg mx-auto px-4 py-12">
      <h1 className="text-3xl font-extrabold mb-2">
        🔔 Recibe <span className="text-[#D4AF37]">alertas</span>
      </h1>
      <p className="text-gray-400 mb-8">
        Registra tu DNI para recibir alertas cuando la estrategia de voto cambie en tu región.
      </p>

      {/* Benefits */}
      <div className="grid gap-3 mb-8">
        {[
          { icon: Bell, text: 'Alertas cuando la estrategia cambie' },
          { icon: Shield, text: 'Recomendaciones personalizadas para tu región' },
          { icon: Lock, text: 'Tu DNI se guarda encriptado, nunca lo veremos' },
        ].map((benefit, i) => (
          <div key={i} className="flex items-center gap-3 text-sm text-gray-400">
            <benefit.icon size={16} className="text-[#D4AF37] shrink-0" />
            <span>{benefit.text}</span>
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* DNI */}
        <div>
          <label htmlFor="dni" className="block text-sm font-medium text-gray-400 mb-2">
            DNI (8 dígitos)
          </label>
          <input
            id="dni"
            type="text"
            inputMode="numeric"
            maxLength={8}
            value={dni}
            onChange={(e) => setDni(e.target.value.replace(/\D/g, ''))}
            placeholder="12345678"
            className="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder:text-gray-600 focus:outline-none focus:border-[#D4AF37] focus:ring-1 focus:ring-[#D4AF37] transition-colors"
          />
          {dni.length > 0 && !isValidDni && (
            <p className="text-xs text-red-400 mt-1">El DNI debe tener exactamente 8 dígitos</p>
          )}
        </div>

        {/* Region */}
        <RegionSelector value={region} onChange={setRegion} label="Tu región electoral" />

        {/* WhatsApp (optional) */}
        <div>
          <label htmlFor="whatsapp" className="block text-sm font-medium text-gray-400 mb-2">
            WhatsApp (opcional)
          </label>
          <input
            id="whatsapp"
            type="tel"
            value={whatsapp}
            onChange={(e) => setWhatsapp(e.target.value)}
            placeholder="+51 999 999 999"
            className="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder:text-gray-600 focus:outline-none focus:border-[#D4AF37] focus:ring-1 focus:ring-[#D4AF37] transition-colors"
          />
          <p className="text-xs text-gray-600 mt-1">
            Para recibir alertas directamente en tu WhatsApp.
          </p>
        </div>

        {/* Privacy */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
          <div className="flex items-start gap-3">
            <Lock size={16} className="text-[#D4AF37] mt-0.5 shrink-0" />
            <div className="text-xs text-gray-500">
              <p className="font-semibold text-gray-400 mb-1">Tu privacidad es nuestra prioridad</p>
              <p>
                Tu DNI se almacena encriptado con AES-256. Nunca veremos tu DNI en texto plano.
                Tu número de WhatsApp solo se usa para enviarte alertas. No compartimos datos con terceros.
              </p>
              <a href="/privacidad" className="text-[#D4AF37] hover:underline mt-1 inline-block">
                Leer política de privacidad completa
              </a>
            </div>
          </div>
        </div>

        {error && <p className="text-red-400 text-sm">{error}</p>}

        <button
          type="submit"
          disabled={!isValidDni || !region || loading}
          className="w-full px-6 py-3 rounded-xl bg-[#D4AF37] text-gray-950 font-bold hover:bg-[#C4A030] disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? 'Registrando...' : 'Registrarme para alertas'}
        </button>
      </form>
    </div>
  );
}
