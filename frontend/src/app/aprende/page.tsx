'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';

const topics = [
  {
    href: '/aprende/cifra-repartidora',
    emoji: '📊',
    title: 'La Cifra Repartidora (D\'Hondt)',
    description: 'Cómo se reparten los escaños y por qué tu voto puede terminar ayudando a quien no quieres.',
  },
  {
    href: '/aprende/la-cedula',
    emoji: '🗳️',
    title: 'Las 5 columnas de la cédula',
    description: 'Qué es cada columna de la cédula de votación 2026 y cómo llenarla correctamente.',
  },
  {
    href: '/aprende/mitos',
    emoji: '🧨',
    title: 'Mitos del voto',
    description: '"Viciar tu voto es protesta" y otros mitos que perjudican tu capacidad de cambio.',
  },
];

export default function AprendePage() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl sm:text-4xl font-extrabold mb-2">
          📚 <span className="text-[#D4AF37]">Aprende</span> a votar mejor
        </h1>
        <p className="text-gray-400 mb-8">
          Guías claras y visuales para entender cómo funciona el sistema electoral peruano.
        </p>
      </motion.div>

      <div className="space-y-4">
        {topics.map((topic, i) => (
          <motion.div
            key={topic.href}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
          >
            <Link
              href={topic.href}
              className="block bg-gray-900 border border-gray-800 rounded-2xl p-6 hover:border-[#D4AF37]/50 transition-all hover:scale-[1.01]"
            >
              <div className="flex items-start gap-4">
                <span className="text-3xl">{topic.emoji}</span>
                <div>
                  <h2 className="text-lg font-bold text-white mb-1">{topic.title}</h2>
                  <p className="text-sm text-gray-400">{topic.description}</p>
                </div>
              </div>
            </Link>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
