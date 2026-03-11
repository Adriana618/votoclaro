'use client';

import { motion } from 'framer-motion';
import WhatsAppButton from './WhatsAppButton';
import { spicyFactMessage } from '@/lib/whatsapp';
import type { ShareableFact } from '@/lib/types';

interface ShareCardProps {
  fact: ShareableFact;
}

export default function ShareCard({ fact }: ShareCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      className="bg-gray-900 border border-gray-800 rounded-2xl p-6 flex flex-col"
    >
      <div className="flex items-start gap-3 mb-4">
        <span className="text-3xl">{fact.emoji || '🔥'}</span>
        <div>
          <span className="inline-block text-xs font-medium text-[#D4AF37] uppercase tracking-wide bg-[#D4AF37]/10 px-2 py-0.5 rounded-full mb-2">
            {fact.category}
          </span>
          <p className="text-white text-lg font-medium leading-snug">{fact.text}</p>
        </div>
      </div>

      <p className="text-xs text-gray-500 mb-4 mt-auto">
        Fuente: {fact.source}
      </p>

      <WhatsAppButton
        message={spicyFactMessage(fact.share_text || fact.text)}
        label="Compartir dato"
        size="sm"
      />
    </motion.div>
  );
}
