'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import QuizQuestionComponent from '@/components/QuizQuestion';
import WhatsAppButton from '@/components/WhatsAppButton';
import { getQuizQuestions, submitQuiz } from '@/lib/api';
import { quizMessage } from '@/lib/whatsapp';
import type { QuizQuestion, QuizAnswer, AffinityResult } from '@/lib/types';
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Cell } from 'recharts';

export default function QuizPage() {
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<QuizAnswer[]>([]);
  const [result, setResult] = useState<AffinityResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    getQuizQuestions()
      .then((q) => {
        setQuestions(q);
        setLoading(false);
      })
      .catch(() => {
        // Placeholder questions
        const placeholders: QuizQuestion[] = Array.from({ length: 15 }, (_, i) => ({
          id: `q${i + 1}`,
          category: ['Seguridad', 'Economia', 'Educacion', 'Salud', 'Politica'][i % 5],
          emoji: ['\u{1F6E1}\u{FE0F}', '\u{1F4B0}', '\u{1F4DA}', '\u{1F3E5}', '\u{1F3DB}\u{FE0F}'][i % 5],
          question: `Pregunta ${i + 1}: \u00bfCu\u00e1l es tu posici\u00f3n sobre este tema?`,
          options: [
            { text: 'Totalmente en desacuerdo', value: -2 },
            { text: 'En desacuerdo', value: -1 },
            { text: 'De acuerdo', value: 1 },
            { text: 'Totalmente de acuerdo', value: 2 },
          ],
          context: 'Contexto de ejemplo para esta pregunta.',
          source: 'Fuente de ejemplo',
        }));
        setQuestions(placeholders);
        setLoading(false);
      });
  }, []);

  const handleAnswer = (value: number) => {
    const question = questions[currentIndex];
    const newAnswers = [
      ...answers.filter((a) => a.question_id !== question.id),
      { question_id: question.id, value },
    ];
    setAnswers(newAnswers);

    // Auto-advance after short delay
    setTimeout(() => {
      if (currentIndex < questions.length - 1) {
        setCurrentIndex(currentIndex + 1);
      }
    }, 400);
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const res = await submitQuiz(answers);
      setResult(res);
    } catch {
      // Show placeholder result
      setResult({
        rankings: [
          { party: 'PE', name: 'Partido Ejemplo', match_percentage: 78 },
          { party: 'OP', name: 'Otro Partido', match_percentage: 65 },
          { party: 'TP', name: 'Tercer Partido', match_percentage: 52 },
        ],
      });
    } finally {
      setSubmitting(false);
    }
  };

  const currentAnswer = answers.find((a) => a.question_id === questions[currentIndex]?.id);
  const progress = questions.length > 0 ? ((currentIndex + 1) / questions.length) * 100 : 0;
  const allAnswered = answers.length === questions.length;

  if (loading) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-20 text-center">
        <div className="animate-pulse text-[#D4AF37] text-xl">Cargando preguntas...</div>
      </div>
    );
  }

  // Results screen
  if (result) {
    const topMatch = result.rankings[0];
    const chartData = result.rankings.map((r) => ({
      name: r.party,
      afinidad: r.match_percentage,
    }));

    return (
      <div className="max-w-2xl mx-auto px-4 py-12">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center mb-8"
        >
          <span className="text-5xl mb-4 block">{'\u{1F3AF}'}</span>
          <h1 className="text-3xl font-extrabold mb-2">Tus resultados</h1>
          <p className="text-gray-400">{'Seg\u00fan tus respuestas, esta es tu afinidad con cada partido'}</p>
        </motion.div>

        {/* Top match */}
        {topMatch && (
          <div className="bg-gradient-to-b from-[#D4AF37]/10 to-transparent border border-[#D4AF37]/30 rounded-2xl p-6 mb-8 text-center">
            <p className="text-sm text-gray-400 mb-1">Mayor afinidad</p>
            <p className="text-2xl font-extrabold text-[#D4AF37] mb-1">{topMatch.name}</p>
            <p className="text-4xl font-black text-white">{topMatch.match_percentage}%</p>
          </div>
        )}

        {/* Chart */}
        <div className="bg-gray-900 rounded-2xl p-4 mb-8">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData} layout="vertical" margin={{ left: 10 }}>
              <XAxis type="number" domain={[0, 100]} tick={{ fill: '#9CA3AF', fontSize: 12 }} />
              <YAxis type="category" dataKey="name" tick={{ fill: '#E5E7EB', fontSize: 12 }} width={60} />
              <Bar dataKey="afinidad" radius={[0, 6, 6, 0]}>
                {chartData.map((_, i) => (
                  <Cell key={i} fill={i === 0 ? '#D4AF37' : '#374151'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Rankings */}
        <div className="space-y-3 mb-8">
          {result.rankings.map((r, i) => (
            <motion.div
              key={r.party}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
              className="flex items-center gap-4 bg-gray-900 rounded-xl p-4"
            >
              <span className="text-2xl font-black text-gray-600 w-8">#{i + 1}</span>
              <div className="flex-1">
                <p className="font-bold text-white">{r.name}</p>
                <p className="text-xs text-gray-500">{r.party}</p>
              </div>
              <span className={`text-lg font-bold ${i === 0 ? 'text-[#D4AF37]' : 'text-gray-400'}`}>
                {r.match_percentage}%
              </span>
            </motion.div>
          ))}
        </div>

        <div className="text-center">
          {topMatch && (
            <WhatsAppButton
              message={quizMessage(topMatch.name, topMatch.match_percentage)}
              label="Compartir mi resultado"
              size="lg"
            />
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-extrabold mb-2">
        {'\u{1F3AF}'} {'\u00bfCon qui\u00e9n '}<span className="text-[#D4AF37]">coincides</span>?
      </h1>
      <p className="text-gray-400 mb-6">
        Responde {questions.length} preguntas y descubre tu afinidad con cada partido.
      </p>

      {/* Progress bar */}
      <div className="mb-8">
        <div className="flex justify-between text-sm text-gray-500 mb-2">
          <span>Pregunta {currentIndex + 1} de {questions.length}</span>
          <span>{Math.round(progress)}%</span>
        </div>
        <div className="w-full bg-gray-800 rounded-full h-2">
          <motion.div
            className="h-2 rounded-full bg-[#D4AF37]"
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.3 }}
          />
        </div>
      </div>

      {/* Question */}
      <AnimatePresence mode="wait">
        <QuizQuestionComponent
          key={questions[currentIndex].id}
          question={questions[currentIndex]}
          onAnswer={handleAnswer}
          selectedValue={currentAnswer?.value}
        />
      </AnimatePresence>

      {/* Navigation */}
      <div className="flex justify-between mt-8">
        <button
          onClick={() => setCurrentIndex(Math.max(0, currentIndex - 1))}
          disabled={currentIndex === 0}
          className="px-5 py-2.5 rounded-xl border border-gray-700 text-gray-300 hover:border-gray-500 disabled:opacity-30 transition-colors"
        >
          Anterior
        </button>
        {currentIndex === questions.length - 1 ? (
          <button
            onClick={handleSubmit}
            disabled={!allAnswered || submitting}
            className="px-8 py-2.5 rounded-xl bg-[#D4AF37] text-gray-950 font-bold hover:bg-[#C4A030] disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            {submitting ? 'Calculando...' : 'Ver resultados'}
          </button>
        ) : (
          <button
            onClick={() => setCurrentIndex(Math.min(questions.length - 1, currentIndex + 1))}
            className="px-5 py-2.5 rounded-xl border border-gray-700 text-gray-300 hover:border-gray-500 transition-colors"
          >
            Siguiente
          </button>
        )}
      </div>
    </div>
  );
}
