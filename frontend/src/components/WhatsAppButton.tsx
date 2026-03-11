'use client';

import { MessageCircle } from 'lucide-react';
import { shareOnWhatsApp } from '@/lib/whatsapp';

interface WhatsAppButtonProps {
  message: string;
  label?: string;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export default function WhatsAppButton({
  message,
  label = 'Compartir por WhatsApp',
  className = '',
  size = 'md',
}: WhatsAppButtonProps) {
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm gap-1.5',
    md: 'px-5 py-2.5 text-base gap-2',
    lg: 'px-6 py-3 text-lg gap-2.5',
  };

  return (
    <button
      onClick={() => shareOnWhatsApp(message)}
      className={`inline-flex items-center justify-center rounded-full bg-[#25D366] hover:bg-[#20BD5A] text-white font-semibold transition-all hover:scale-105 active:scale-95 ${sizeClasses[size]} ${className}`}
      aria-label={label}
    >
      <MessageCircle size={size === 'sm' ? 16 : size === 'lg' ? 22 : 18} />
      <span>{label}</span>
    </button>
  );
}
