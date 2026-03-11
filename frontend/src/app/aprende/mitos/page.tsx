'use client';

import { motion } from 'framer-motion';
import WhatsAppButton from '@/components/WhatsAppButton';

const myths = [
  {
    myth: '"Viciar mi voto es una forma de protesta"',
    reality: 'Viciar tu voto solo hace que tu papeleta no cuente. Beneficia directamente al partido con más votos en tu región, porque la cifra repartidora se calcula solo con votos válidos.',
    verdict: 'FALSO',
    emoji: '❌',
  },
  {
    myth: '"Si voto en blanco, el candidato no puede asumir"',
    reality: 'El voto en blanco se cuenta como "emitido" pero no como "válido". No afecta al resultado final. Para que se anulen las elecciones se necesitan condiciones muy específicas que el voto en blanco no cumple.',
    verdict: 'FALSO',
    emoji: '❌',
  },
  {
    myth: '"Mi voto para congresistas tiene que ser del mismo partido que mi voto presidencial"',
    reality: 'No. La cédula tiene columnas separadas y puedes marcar partidos diferentes. Esto es voto cruzado y es completamente legal.',
    verdict: 'FALSO',
    emoji: '❌',
  },
  {
    myth: '"Los partidos pequeños no tienen chance"',
    reality: 'Depende de la región. En regiones con pocos escaños, los partidos pequeños tienen menos probabilidad. Pero en regiones grandes como Lima, sí pueden obtener escaños. El simulador te ayuda a calcular.',
    verdict: 'DEPENDE',
    emoji: '⚠️',
  },
  {
    myth: '"El voto preferencial no sirve para nada"',
    reality: 'El voto preferencial puede cambiar el orden de la lista de un partido. Si un candidato recibe suficientes votos preferenciales, puede subir sobre otros candidatos de su misma lista.',
    verdict: 'FALSO',
    emoji: '❌',
  },
  {
    myth: '"Da igual por quién vote, todos son iguales"',
    reality: 'No todos los candidatos tienen antecedentes penales, denuncias por corrupción o investigaciones fiscales. Hay diferencias reales y verificables. Usa nuestros filtros para compararlos.',
    verdict: 'FALSO',
    emoji: '❌',
  },
];

export default function MitosPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <h1 className="text-3xl sm:text-4xl font-extrabold mb-2">
        🧨 Mitos del <span className="text-[#D4AF37]">voto</span>
      </h1>
      <p className="text-gray-400 mb-8">
        Creencias populares que perjudican tu poder de cambio. Veamos la realidad.
      </p>

      <div className="space-y-6">
        {myths.map((item, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden"
          >
            {/* Myth */}
            <div className="p-5 border-b border-gray-800">
              <div className="flex items-start gap-3">
                <span className="text-2xl">{item.emoji}</span>
                <div>
                  <span
                    className={`inline-block text-xs font-bold px-2 py-0.5 rounded-full mb-2 ${
                      item.verdict === 'FALSO'
                        ? 'bg-red-500/20 text-red-400'
                        : 'bg-amber-500/20 text-amber-400'
                    }`}
                  >
                    {item.verdict}
                  </span>
                  <p className="text-lg font-bold text-white italic">{item.myth}</p>
                </div>
              </div>
            </div>

            {/* Reality */}
            <div className="p-5 bg-gray-900/50">
              <p className="text-sm text-gray-300 leading-relaxed">
                <span className="text-[#D4AF37] font-semibold">Realidad: </span>
                {item.reality}
              </p>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="text-center mt-10">
        <WhatsAppButton
          message={
            '🧨 *Mitos del voto que debes conocer*\n\n' +
            '❌ "Viciar mi voto es protesta" → FALSO. Solo beneficia al partido más grande.\n' +
            '❌ "Voto en blanco anula elecciones" → FALSO.\n' +
            '❌ "Todos son iguales" → FALSO. Compáralos.\n\n' +
            'Más mitos en 👉 votoclaro.pe/aprende/mitos\n\n' +
            '_Que la ignorancia no gane las elecciones 🇵🇪_'
          }
          label="Compartir mitos"
        />
      </div>
    </div>
  );
}
