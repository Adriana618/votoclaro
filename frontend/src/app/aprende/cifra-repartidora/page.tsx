'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import DhondtTable from '@/components/DhondtTable';
import WhatsAppButton from '@/components/WhatsAppButton';
import type { DhondtRow } from '@/lib/types';

const EXAMPLE_ROWS: DhondtRow[] = [
  { party: 'Partido A', votes: 100000, divisors: [1, 2, 3, 4, 5], quotients: [100000, 50000, 33333, 25000, 20000], seats_won: 3 },
  { party: 'Partido B', votes: 80000, divisors: [1, 2, 3, 4, 5], quotients: [80000, 40000, 26667, 20000, 16000], seats_won: 2 },
  { party: 'Partido C', votes: 30000, divisors: [1, 2, 3, 4, 5], quotients: [30000, 15000, 10000, 7500, 6000], seats_won: 0 },
  { party: 'Partido D', votes: 20000, divisors: [1, 2, 3, 4, 5], quotients: [20000, 10000, 6667, 5000, 4000], seats_won: 0 },
];

const steps = [
  {
    title: 'Los votos se cuentan por partido',
    description: 'Primero se suman todos los votos válidos que recibió cada partido en la región.',
  },
  {
    title: 'Se dividen entre 1, 2, 3, ...',
    description: 'Los votos de cada partido se dividen entre 1, 2, 3, y así sucesivamente hasta el número de escaños disponibles.',
  },
  {
    title: 'Se ordenan los cocientes',
    description: 'Todos los resultados (cocientes) se ordenan de mayor a menor.',
  },
  {
    title: 'Se asignan escaños a los más altos',
    description: 'Los escaños se reparten a los partidos cuyos cocientes son los más altos. El último cociente que entra se llama "cifra repartidora".',
  },
  {
    title: '¿Por qué importa?',
    description: 'Si muchas personas votan por partidos pequeños diferentes, sus votos se "desperdician" porque ninguno alcanza cocientes altos. Esto beneficia al partido grande, que concentra votos.',
  },
];

export default function CifraRepartidoraPage() {
  const [currentStep, setCurrentStep] = useState(0);

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <h1 className="text-3xl sm:text-4xl font-extrabold mb-2">
        📊 La Cifra <span className="text-[#D4AF37]">Repartidora</span>
      </h1>
      <p className="text-gray-400 mb-8">
        El método D&apos;Hondt explicado paso a paso. Así se decide quién llega al Congreso.
      </p>

      {/* Steps */}
      <div className="space-y-4 mb-12">
        {steps.map((step, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.15 }}
            className={`p-5 rounded-xl border cursor-pointer transition-all ${
              currentStep === i
                ? 'border-[#D4AF37] bg-[#D4AF37]/5'
                : 'border-gray-800 bg-gray-900 hover:border-gray-700'
            }`}
            onClick={() => setCurrentStep(i)}
          >
            <div className="flex items-start gap-3">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold shrink-0 ${
                  currentStep === i ? 'bg-[#D4AF37] text-gray-950' : 'bg-gray-800 text-gray-500'
                }`}
              >
                {i + 1}
              </div>
              <div>
                <h3 className="font-bold text-white mb-1">{step.title}</h3>
                <p className="text-sm text-gray-400">{step.description}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Example table */}
      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 mb-8">
        <h2 className="text-lg font-bold text-white mb-4">Ejemplo con 5 escaños</h2>
        <DhondtTable rows={EXAMPLE_ROWS} totalSeats={5} animate={true} />
        <div className="mt-4 p-4 rounded-xl bg-amber-500/10 border border-amber-500/20">
          <p className="text-sm text-amber-300">
            <strong>Nota:</strong> En este ejemplo, los Partidos C y D juntos tienen 50,000 votos
            pero no ganan ningún escaño. Si hubieran votado unidos, podrían haber ganado 1 escaño.
            Esto es el efecto de la cifra repartidora.
          </p>
        </div>
      </div>

      <div className="text-center">
        <WhatsAppButton
          message={
            '📊 *¿Sabes cómo funciona la cifra repartidora?*\n\n' +
            'Es el método que decide quién llega al Congreso. Si no lo entiendes, ' +
            'tu voto puede terminar ayudando a quien no quieres.\n\n' +
            'Aprende en 👉 votaclaro.com/aprende/cifra-repartidora\n\n' +
            '_Que la ignorancia no gane las elecciones 🇵🇪_'
          }
          label="Compartir explicación"
        />
      </div>
    </div>
  );
}
