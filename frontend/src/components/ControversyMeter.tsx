'use client';

import { motion } from 'framer-motion';

interface ControversyMeterProps {
  score: number; // 0-100
  size?: 'sm' | 'md' | 'lg';
}

function getColor(score: number): string {
  if (score <= 20) return '#22C55E'; // green
  if (score <= 40) return '#EAB308'; // yellow
  if (score <= 60) return '#F97316'; // orange
  if (score <= 80) return '#EF4444'; // red
  return '#DC2626'; // dark red / skull
}

function getLabel(score: number): string {
  if (score <= 20) return 'Bajo';
  if (score <= 40) return 'Moderado';
  if (score <= 60) return 'Alto';
  if (score <= 80) return 'Muy alto';
  return 'Extremo';
}

function getEmoji(score: number): string {
  if (score <= 20) return '🟢';
  if (score <= 40) return '🟡';
  if (score <= 60) return '🟠';
  if (score <= 80) return '🔴';
  return '💀';
}

export default function ControversyMeter({ score, size = 'md' }: ControversyMeterProps) {
  const color = getColor(score);
  const label = getLabel(score);
  const emoji = getEmoji(score);

  const heights = { sm: 'h-2', md: 'h-3', lg: 'h-4' };
  const textSizes = { sm: 'text-xs', md: 'text-sm', lg: 'text-base' };

  return (
    <div className="w-full">
      <div className="flex justify-between items-center mb-1">
        <span className={`${textSizes[size]} text-gray-400`}>
          {emoji} {label}
        </span>
        <span className={`${textSizes[size]} font-bold`} style={{ color }}>
          {score}/100
        </span>
      </div>
      <div className={`w-full bg-gray-800 rounded-full ${heights[size]}`}>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${score}%` }}
          transition={{ duration: 1, ease: 'easeOut' }}
          className={`${heights[size]} rounded-full`}
          style={{ backgroundColor: color }}
        />
      </div>
    </div>
  );
}
