'use client';

import { motion } from 'framer-motion';
import WhatsAppButton from '@/components/WhatsAppButton';

const columns = [
  {
    number: 1,
    title: 'Presidente y Vicepresidentes',
    description: 'Marcas al partido de tu candidato presidencial. Tu voto también va para sus dos vicepresidentes.',
    tip: 'Solo puedes marcar un partido.',
    color: '#D4AF37',
  },
  {
    number: 2,
    title: 'Congresistas',
    description: 'Eliges al partido cuya lista de candidatos al Congreso quieres apoyar. Este es el voto más importante para la cifra repartidora.',
    tip: 'Puedes votar por un partido diferente al presidencial.',
    color: '#3B82F6',
  },
  {
    number: 3,
    title: 'Voto Preferencial',
    description: 'Dentro de la lista de congresistas del partido elegido, puedes marcar hasta 2 candidatos específicos para que suban en la lista.',
    tip: 'Si no marcas, se respeta el orden de la lista del partido.',
    color: '#10B981',
  },
  {
    number: 4,
    title: 'Parlamento Andino',
    description: 'Eliges representantes al Parlamento Andino, órgano deliberante de la Comunidad Andina de Naciones.',
    tip: 'Muchos lo dejan en blanco, pero es un voto válido.',
    color: '#8B5CF6',
  },
  {
    number: 5,
    title: 'Referéndum (si aplica)',
    description: 'Si hay consulta popular, esta columna aparecerá para que votes SÍ o NO sobre la propuesta.',
    tip: 'No siempre hay referéndum. Confirma antes de ir a votar.',
    color: '#F59E0B',
  },
];

export default function LaCedulaPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <h1 className="text-3xl sm:text-4xl font-extrabold mb-2">
        🗳️ Las 5 columnas de la <span className="text-[#D4AF37]">cédula</span>
      </h1>
      <p className="text-gray-400 mb-8">
        Tu cédula de votación en 2026 tendrá hasta 5 columnas. Aprende qué es cada una.
      </p>

      {/* Visual representation */}
      <div className="flex gap-1 mb-10 overflow-x-auto pb-2">
        {columns.map((col) => (
          <motion.div
            key={col.number}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: col.number * 0.1 }}
            className="flex-1 min-w-[100px] bg-gray-900 border border-gray-800 rounded-xl p-3 text-center"
          >
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold mx-auto mb-1 text-gray-950"
              style={{ backgroundColor: col.color }}
            >
              {col.number}
            </div>
            <p className="text-[10px] sm:text-xs text-gray-400 leading-tight">{col.title}</p>
          </motion.div>
        ))}
      </div>

      {/* Detailed cards */}
      <div className="space-y-4 mb-10">
        {columns.map((col, i) => (
          <motion.div
            key={col.number}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.1 }}
            className="bg-gray-900 border border-gray-800 rounded-2xl p-5"
          >
            <div className="flex items-start gap-4">
              <div
                className="w-10 h-10 rounded-full flex items-center justify-center text-lg font-bold shrink-0 text-gray-950"
                style={{ backgroundColor: col.color }}
              >
                {col.number}
              </div>
              <div>
                <h2 className="font-bold text-white text-lg mb-1">{col.title}</h2>
                <p className="text-sm text-gray-400 mb-2">{col.description}</p>
                <div className="inline-flex items-center gap-1.5 bg-gray-800 px-3 py-1.5 rounded-lg">
                  <span className="text-xs">💡</span>
                  <span className="text-xs text-gray-300">{col.tip}</span>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Key insight */}
      <div className="bg-amber-500/10 border border-amber-500/20 rounded-2xl p-5 mb-8">
        <h3 className="font-bold text-amber-300 mb-2">⚡ Dato clave</h3>
        <p className="text-sm text-gray-300">
          Puedes votar por partidos diferentes en cada columna. Tu voto a presidente NO tiene
          que ser del mismo partido que tu voto a congresistas. Usa esto a tu favor.
        </p>
      </div>

      <div className="text-center">
        <WhatsAppButton
          message={
            '🗳️ *¿Sabes qué son las 5 columnas de la cédula?*\n\n' +
            'Puedes votar por partidos DIFERENTES en cada columna. ' +
            'Aprende a usar tu voto estratégicamente.\n\n' +
            '👉 votoclaro.pe/aprende/la-cedula\n\n' +
            '_Que la ignorancia no gane las elecciones 🇵🇪_'
          }
          label="Compartir guía"
        />
      </div>
    </div>
  );
}
