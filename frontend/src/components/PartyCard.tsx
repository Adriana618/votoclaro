'use client';

import { motion } from 'framer-motion';
import type { Party } from '@/lib/types';
import PartyLogo from './PartyLogo';

interface PartyCardProps {
  party: Party;
  selected?: boolean;
  onToggle?: (partyId: string) => void;
  affinityPercent?: number;
  showAffinity?: boolean;
}

export default function PartyCard({
  party,
  selected = false,
  onToggle,
  affinityPercent,
  showAffinity = false,
}: PartyCardProps) {
  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={() => onToggle?.(party.id)}
      className={`relative rounded-xl p-4 border-2 transition-colors cursor-pointer ${
        selected
          ? 'border-[#D4AF37] bg-[#D4AF37]/10'
          : 'border-gray-700 bg-gray-900 hover:border-gray-600'
      }`}
      role={onToggle ? 'checkbox' : undefined}
      aria-checked={onToggle ? selected : undefined}
      tabIndex={onToggle ? 0 : undefined}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onToggle?.(party.id);
        }
      }}
    >
      <div className="flex items-center gap-3">
        <PartyLogo
          abbreviation={party.abbreviation || party.id}
          name={party.name}
          color={party.color}
          size={48}
        />

        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-white truncate">{party.name}</h3>
        </div>

        {selected && (
          <div className="w-6 h-6 rounded-full bg-[#D4AF37] flex items-center justify-center shrink-0">
            <svg className="w-4 h-4 text-gray-950" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        )}
      </div>

      {showAffinity && affinityPercent !== undefined && (
        <div className="mt-3">
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-400">Afinidad</span>
            <span className="text-[#D4AF37] font-semibold">{affinityPercent}%</span>
          </div>
          <div className="w-full bg-gray-800 rounded-full h-2">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${affinityPercent}%` }}
              transition={{ duration: 0.8, ease: 'easeOut' }}
              className="h-2 rounded-full bg-gradient-to-r from-[#D4AF37] to-[#F0D060]"
            />
          </div>
        </div>
      )}
    </motion.div>
  );
}
