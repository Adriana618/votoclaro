'use client';

import { motion } from 'framer-motion';
import type { DhondtRow } from '@/lib/types';

interface DhondtTableProps {
  rows: DhondtRow[];
  totalSeats: number;
  animate?: boolean;
}

export default function DhondtTable({ rows, totalSeats, animate = true }: DhondtTableProps) {
  if (!rows.length) return null;

  const maxDivisor = Math.max(...rows.map((r) => r.divisors?.length || 0), totalSeats);
  const divisors = Array.from({ length: maxDivisor }, (_, i) => i + 1);

  // Collect all quotients and find the winning threshold
  const allQuotients: { party: string; value: number; divisor: number }[] = [];
  rows.forEach((row) => {
    divisors.forEach((d, i) => {
      const q = row.quotients?.[i] ?? Math.floor(row.votes / d);
      allQuotients.push({ party: row.party, value: q, divisor: d });
    });
  });
  allQuotients.sort((a, b) => b.value - a.value);
  const threshold = allQuotients[totalSeats - 1]?.value ?? 0;

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr>
            <th className="text-left p-2 text-gray-400 border-b border-gray-800 font-medium">
              Partido
            </th>
            <th className="text-right p-2 text-gray-400 border-b border-gray-800 font-medium">
              Votos
            </th>
            {divisors.map((d) => (
              <th key={d} className="text-right p-2 text-gray-400 border-b border-gray-800 font-medium">
                ÷{d}
              </th>
            ))}
            <th className="text-center p-2 text-gray-400 border-b border-gray-800 font-medium">
              Escaños
            </th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIdx) => (
            <tr key={row.party} className="border-b border-gray-800/50">
              <td className="p-2 font-semibold text-white">{row.party}</td>
              <td className="p-2 text-right text-gray-300">
                {row.votes.toLocaleString('es-PE')}
              </td>
              {divisors.map((d, i) => {
                const q = row.quotients?.[i] ?? Math.floor(row.votes / d);
                const isWinning = q >= threshold && row.seats_won > 0;
                const delay = animate ? (rowIdx * divisors.length + i) * 0.05 : 0;

                return (
                  <td key={d} className="p-2 text-right">
                    <motion.span
                      initial={animate ? { opacity: 0, scale: 0.5 } : false}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay, duration: 0.2 }}
                      className={`inline-block px-1.5 py-0.5 rounded ${
                        isWinning
                          ? 'bg-[#D4AF37]/20 text-[#D4AF37] font-bold'
                          : 'text-gray-500'
                      }`}
                    >
                      {q.toLocaleString('es-PE')}
                    </motion.span>
                  </td>
                );
              })}
              <td className="p-2 text-center">
                <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-[#D4AF37]/20 text-[#D4AF37] font-bold">
                  {row.seats_won}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <p className="mt-3 text-xs text-gray-500">
        La cifra repartidora es {threshold.toLocaleString('es-PE')}. Se asignan {totalSeats} escaños
        a los cocientes más altos.
      </p>
    </div>
  );
}
