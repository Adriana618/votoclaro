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
  category: string;
  category_emoji: string;
  text: string;
  options: QuizOption[];
  context?: string;
  source?: string;
}

export interface QuizOption {
  id: string;
  text: string;
  party_weights: Record<string, number>;
}

export interface QuizAnswer {
  question_id: string;
  option_id: string;
}

export interface AntiVoteResult {
  region: Region;
  rejected_parties: Party[];
  recommended_party: Party;
  recommended_party_label: string;
  explanation: string;
  dhondt_table: DhondtRow[];
  wasted_vote_risk: number;
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
  top_match: Party;
  match_percent: number;
}

export interface AffinityRanking {
  party: Party;
  affinity_percent: number;
  matching_topics: string[];
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
