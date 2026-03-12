import type {
  QuizQuestion,
  QuizAnswer,
  AntiVoteResult,
  AffinityResult,
  Party,
  SpicyFilter,
  Candidate,
  Region,
  ShareableFact,
  RegistrationData,
  TrendData,
} from './types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${BASE_URL}${endpoint}`;
  const res = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Error de conexión' }));
    throw new Error(error.detail || `Error ${res.status}`);
  }

  return res.json();
}

export async function getQuizQuestions(): Promise<QuizQuestion[]> {
  return fetchApi<QuizQuestion[]>('/quiz/questions');
}

export async function submitQuiz(answers: QuizAnswer[]): Promise<AffinityResult> {
  return fetchApi<AffinityResult>('/quiz/submit', {
    method: 'POST',
    body: JSON.stringify({
      answers: answers.map((a) => ({ question_id: a.question_id, value: a.value })),
    }),
  });
}

export async function calculateAntiVote(
  regionId: string,
  rejectedPartyIds: string[]
): Promise<AntiVoteResult> {
  return fetchApi<AntiVoteResult>('/simulador/calculate', {
    method: 'POST',
    body: JSON.stringify({
      region_id: regionId,
      rejected_party_ids: rejectedPartyIds,
    }),
  });
}

export async function getParties(): Promise<Party[]> {
  return fetchApi<Party[]>('/parties');
}

export async function getFilters(): Promise<SpicyFilter[]> {
  return fetchApi<SpicyFilter[]>('/filters');
}

export async function getCandidatesControversial(
  regionId?: string,
  filters?: string[]
): Promise<Candidate[]> {
  const params = new URLSearchParams();
  if (regionId) params.append('region_id', regionId);
  if (filters?.length) params.append('filters', filters.join(','));
  return fetchApi<Candidate[]>(`/candidates/controversial?${params}`);
}

export async function getRegions(): Promise<Region[]> {
  return fetchApi<Region[]>('/regions');
}

export async function getFacts(): Promise<ShareableFact[]> {
  return fetchApi<ShareableFact[]>('/facts');
}

export async function registerDni(data: RegistrationData): Promise<{ success: boolean }> {
  return fetchApi<{ success: boolean }>('/register', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getTrends(regionId: string): Promise<TrendData[]> {
  return fetchApi<TrendData[]>(`/trends?region_id=${regionId}`);
}

export async function saveVote(data: {
  dni: string;
  digito: string;
  region: unknown;
  recommended_party: unknown;
  rejected_parties: unknown[];
  saved_at: string;
}): Promise<{ success: boolean }> {
  return fetchApi<{ success: boolean }>('/mi-voto/save', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function lookupVote(dni: string, digito: string): Promise<{
  region: { id: string; name: string; seats: number };
  recommended_party: { id: string; name: string; abbreviation: string; color?: string };
  rejected_parties: { id: string; name: string; abbreviation: string; color?: string }[];
  saved_at: string;
}> {
  return fetchApi('/mi-voto/lookup', {
    method: 'POST',
    body: JSON.stringify({ dni, digito }),
  });
}
