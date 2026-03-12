export interface Party {
  id: string;
  name: string;
  abbreviation: string;
  logo_url?: string;
  color?: string;
  description?: string;
}

export interface Region {
  id: string;
  name: string;
  seats: number;
}

export interface Candidate {
  id: string;
  name: string;
  party_id: string;
  party?: Party;
  region_id: string;
  region?: Region;
  position: number;
  has_criminal_record: boolean;
  controversy_score: number;
  controversy_reason?: string;
  photo_url?: string;
}

export interface QuizQuestion {
  id: string;
  question: string;
  category: string;
  emoji: string;
  options: QuizOption[];
  context?: string;
  source?: string;
}

export interface QuizOption {
  text: string;
  value: number; // -2 to +2
}

export interface QuizAnswer {
  question_id: string;
  value: number; // -2 to +2
}

export interface AntiVoteResult {
  region: Region;
  rejected_parties: Party[];
  recommended_party: Party;
  recommended_party_label: string;
  explanation: string;
  dhondt_table: DhondtRow[];
  wasted_vote_risk: number;
  seats_saved: number;
  rejected_seats_before: number;
  rejected_seats_after: number;
}

export interface DhondtRow {
  party: string;
  votes: number;
  divisors: number[];
  quotients: number[];
  seats_won: number;
}

export interface AffinityResult {
  rankings: AffinityRanking[];
}

export interface AffinityRanking {
  party: string;
  name: string;
  match_percentage: number;
}

export interface SpicyFilter {
  id: string;
  label: string;
  category: 'seguridad' | 'economia' | 'social' | 'politica';
  description?: string;
}

export interface ShareableFact {
  id: string;
  text: string;
  source: string;
  category: string;
  emoji?: string;
  share_text: string;
}

export interface TrendData {
  region_id: string;
  date: string;
  anti_vote_distribution: Record<string, number>;
  top_rejected: Party[];
}

export interface RegistrationData {
  dni: string;
  region_id: string;
  whatsapp?: string;
}

export interface SavedVote {
  region: Region;
  recommendation: Party;
  last_updated: string;
  anti_vote_parties: Party[];
}
