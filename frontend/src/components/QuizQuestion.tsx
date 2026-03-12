'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronDown, ChevronUp } from 'lucide-react';
import type { QuizQuestion as QuizQuestionType } from '@/lib/types';

interface QuizQuestionProps {
  question: QuizQuestionType;
  onAnswer: (value: number) => void;
  selectedValue?: number;
}

export default function QuizQuestion({
  question,
  onAnswer,
  selectedValue,
}: QuizQuestionProps) {
  const [showContext, setShowContext] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -50 }}
      transition={{ duration: 0.3 }}
      className="w-full max-w-2xl mx-auto"
    >
      {/* Category */}
      <div className="flex items-center gap-2 mb-4">
        <span className="text-2xl">{question.emoji}</span>
        <span className="text-sm font-medium text-[#D4AF37] uppercase tracking-wide">
          {question.category}
        </span>
      </div>

      {/* Question text */}
      <h2 className="text-xl sm:text-2xl font-bold text-white mb-6 leading-tight">
        {question.question}
      </h2>

      {/* Options */}
      <div className="space-y-3">
        {question.options.map((option, index) => (
          <motion.button
            key={`${question.id}-opt-${index}`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            onClick={() => onAnswer(option.value)}
            className={`w-full text-left p-4 rounded-xl border-2 transition-all ${
              selectedValue === option.value
                ? 'border-[#D4AF37] bg-[#D4AF37]/10 text-white'
                : 'border-gray-700 bg-gray-900 text-gray-300 hover:border-gray-500 hover:text-white'
            }`}
            aria-pressed={selectedValue === option.value}
          >
            <span className="font-medium">{option.text}</span>
          </motion.button>
        ))}
      </div>

      {/* Context / Source */}
      {(question.context || question.source) && (
        <div className="mt-6">
          <button
            onClick={() => setShowContext(!showContext)}
            className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-300 transition-colors"
          >
            {showContext ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            <span>{'\u00bf'}Por qu{'\u00e9'} importa?</span>
          </button>
          {showContext && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="mt-2 p-3 rounded-lg bg-gray-900 border border-gray-800 text-sm text-gray-400"
            >
              {question.context && <p className="mb-2">{question.context}</p>}
              {question.source && (
                <p className="text-xs text-gray-500">Fuente: {question.source}</p>
              )}
            </motion.div>
          )}
        </div>
      )}
    </motion.div>
  );
}
