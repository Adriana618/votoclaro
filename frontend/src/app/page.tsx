'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import WhatsAppButton from '@/components/WhatsAppButton';

const ctaCards = [
  {
    emoji: '🗳️',
    title: 'Simulador de Voto Estratégico',
    description: 'Descubre cómo tu voto puede evitar que los peores lleguen al Congreso',
    href: '/simulador',
    color: 'from-amber-500/20 to-amber-700/5',
  },
  {
    emoji: '🎯',
    title: '¿Con quién coincides?',
    description: 'Responde 15 preguntas y descubre tu afinidad con cada partido',
    href: '/quiz',
    color: 'from-blue-500/20 to-blue-700/5',
  },
  {
    emoji: '🔥',
    title: 'Datos que deberías saber',
    description: 'Hechos verificados que los candidatos no quieren que compartas',
    href: '/sabias-que',
    color: 'from-red-500/20 to-red-700/5',
  },
];

const stats = [
  { number: '292', label: 'candidatos con antecedentes penales' },
  { number: '17', label: 'congresistas pro-crimen buscan reelección' },
  { number: '40%', label: 'del Congreso actual tiene denuncias fiscales' },
  { number: '5', label: 'columnas en la cédula que debes entender' },
];

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="relative px-4 py-20 sm:py-32 max-w-5xl mx-auto text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-5xl sm:text-7xl font-extrabold mb-4 tracking-tight">
            <span className="text-[#D4AF37]">Voto</span>
            <span className="text-white">Claro</span>
          </h1>
          <p className="text-xl sm:text-2xl text-gray-300 mb-2 font-medium">
            Que la ignorancia no gane las elecciones 🇵🇪
          </p>
          <p className="text-base sm:text-lg text-gray-500 max-w-2xl mx-auto mb-10">
            En las elecciones 2026, tu voto importa más de lo que crees.
            <br className="hidden sm:block" />
            La cifra repartidora puede hacer que un voto mal informado beneficie a quienes
            quieres evitar.
          </p>
        </motion.div>

        {/* CTA Cards */}
        <div className="grid sm:grid-cols-3 gap-4 sm:gap-6 mb-12">
          {ctaCards.map((card, i) => (
            <motion.div
              key={card.href}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + i * 0.15, duration: 0.5 }}
            >
              <Link
                href={card.href}
                className={`block p-6 rounded-2xl border border-gray-800 bg-gradient-to-b ${card.color} hover:border-[#D4AF37]/50 transition-all hover:scale-[1.02] active:scale-[0.98]`}
              >
                <span className="text-4xl mb-3 block">{card.emoji}</span>
                <h2 className="text-lg font-bold text-white mb-2">{card.title}</h2>
                <p className="text-sm text-gray-400">{card.description}</p>
              </Link>
            </motion.div>
          ))}
        </div>

        {/* WhatsApp Share */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
        >
          <WhatsAppButton
            message={
              '🗳️ *VotoClaro* - Herramienta de voto estratégico para las elecciones Perú 2026.\n\n' +
              'Simula tu voto, descubre con quién coincides y comparte los datos que importan.\n\n' +
              '👉 votoclaro.pe\n\n' +
              '_Que la ignorancia no gane las elecciones 🇵🇪_'
            }
            label="Comparte VotoClaro"
            size="lg"
          />
        </motion.div>
      </section>

      {/* Stats */}
      <section className="bg-gray-900/50 border-y border-gray-800 py-16 px-4">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-center text-sm font-semibold text-[#D4AF37] uppercase tracking-widest mb-10">
            ¿Por qué votar informado?
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-6">
            {stats.map((stat, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="text-center"
              >
                <p className="text-3xl sm:text-4xl font-extrabold text-[#D91023] mb-1">
                  {stat.number}
                </p>
                <p className="text-sm text-gray-400">{stat.label}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Quick links */}
      <section className="py-16 px-4 max-w-5xl mx-auto text-center">
        <div className="flex flex-wrap justify-center gap-3">
          <Link
            href="/controversial"
            className="px-5 py-2.5 rounded-full border border-gray-700 text-gray-300 hover:border-[#D4AF37] hover:text-[#D4AF37] transition-colors text-sm"
          >
            Ranking Controversial
          </Link>
          <Link
            href="/filtros"
            className="px-5 py-2.5 rounded-full border border-gray-700 text-gray-300 hover:border-[#D4AF37] hover:text-[#D4AF37] transition-colors text-sm"
          >
            Filtrar por temas
          </Link>
          <Link
            href="/aprende"
            className="px-5 py-2.5 rounded-full border border-gray-700 text-gray-300 hover:border-[#D4AF37] hover:text-[#D4AF37] transition-colors text-sm"
          >
            Aprende a votar
          </Link>
          <Link
            href="/tendencias"
            className="px-5 py-2.5 rounded-full border border-gray-700 text-gray-300 hover:border-[#D4AF37] hover:text-[#D4AF37] transition-colors text-sm"
          >
            Tendencias colectivas
          </Link>
          <Link
            href="/mi-voto"
            className="px-5 py-2.5 rounded-full border border-gray-700 text-gray-300 hover:border-[#D4AF37] hover:text-[#D4AF37] transition-colors text-sm"
          >
            Consultar mi voto
          </Link>
          <Link
            href="/registrar"
            className="px-5 py-2.5 rounded-full border border-gray-700 text-gray-300 hover:border-[#D4AF37] hover:text-[#D4AF37] transition-colors text-sm"
          >
            Alertas personalizadas
          </Link>
        </div>
      </section>
    </div>
  );
}
