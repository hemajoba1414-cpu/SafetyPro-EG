export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

export interface Step {
  title: string;
  description: string;
}

export interface Plan {
  id: number;
  title: string;
  description: string;
  status: 'draft' | 'active' | 'completed' | 'archived';
  steps: Step[];
  created_at: string;
  updated_at: string;
}

export interface Subscription {
  id: number;
  plan_type: 'free' | 'starter' | 'professional' | 'enterprise';
  is_active: boolean;
  current_period_end: string | null;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginResponse extends TokenResponse {
  remaining_days: number;
  status: string;
  user: string;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  remainingDays: number | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

export interface PricingPlan {
  name: string;
  price: number;
  max_plans: number | string;
  features: string[];
}
