// ==========================================
// VENTURETWIN SCHEMA DEFINITIONS
// Sourced strictly from FastAPI & SQLAlchemy
// ==========================================

export interface UserRegisterRequest {
  email: string;
  password: string;
  full_name?: string | null;
}

export interface UserLoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface UserResponse {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
}

export interface UserUpdateRequest {
  full_name?: string | null;
  email?: string | null;
}

// ------------------------------------------
// STARTUP PROFILE SCHEMAS
// ------------------------------------------

export interface StartupProfileCreate {
  startup_name: string;
  description?: string | null;
  business_type?: string | null;
  target_market?: string | null;
  website?: string | null;
  founded_year?: number | null;
}

export interface StartupProfileUpdate {
  startup_name?: string | null;
  description?: string | null;
  business_type?: string | null;
  target_market?: string | null;
  website?: string | null;
  founded_year?: number | null;
}

export interface StartupProfileResponse {
  startup_id: number;
  user_id: number;
  startup_name: string;
  description: string | null;
  business_type: string | null;
  target_market: string | null;
  website: string | null;
  founded_year: number | null;
  created_at: string;
  updated_at: string;
}

// ------------------------------------------
// FINANCIAL INFORMATION
// ------------------------------------------

export interface FinancialInformationCreate {
  initial_investment?: number | null;
  monthly_expenses?: number | null;
  monthly_revenue?: number | null;
  annual_revenue?: number | null;
  annual_profit?: number | null;
  funding_raised?: number | null;
  burn_rate?: number | null;
}

export interface FinancialInformationResponse {
  financial_id: number;
  startup_id: number;
  initial_investment: number | null;
  monthly_expenses: number | null;
  monthly_revenue: number | null;
  annual_revenue: number | null;
  annual_profit: number | null;
  funding_raised: number | null;
  burn_rate: number | null;
  created_at: string;
  updated_at: string;
}

// ------------------------------------------
// TEAM INFORMATION
// ------------------------------------------

export interface TeamInformationCreate {
  employee_count?: number | null;
  founder_name?: string | null;
  founder_experience_years?: number | null;
  founder_education?: string | null;
  team_skills?: string | null;
  has_technical_cofounder: boolean;
}

export interface TeamInformationResponse {
  team_id: number;
  startup_id: number;
  employee_count: number | null;
  founder_name: string | null;
  founder_experience_years: number | null;
  founder_education: string | null;
  team_skills: string | null;
  has_technical_cofounder: boolean;
  created_at: string;
  updated_at: string;
}

// ------------------------------------------
// BUSINESS LOCATION
// ------------------------------------------

export interface BusinessLocationCreate {
  country?: string | null;
  state?: string | null;
  city?: string | null;
  address?: string | null;
  pincode?: string | null;
}

export interface BusinessLocationResponse {
  location_id: number;
  startup_id: number;
  country: string | null;
  state: string | null;
  city: string | null;
  address: string | null;
  pincode: string | null;
  created_at: string;
  updated_at: string;
}

// ------------------------------------------
// LAND DETAILS
// ------------------------------------------

export type LandStatus = 'owned' | 'rented' | 'no_land' | 'planning';

export interface LandDetailsCreate {
  has_land: boolean;
  land_status?: string | null;
  land_area_sqft?: number | null;
  land_value?: number | null;
  monthly_rent?: number | null;
  expansion_available: boolean;
}

export interface LandDetailsResponse {
  land_id: number;
  startup_id: number;
  has_land: boolean;
  land_status: string | null;
  land_area_sqft: number | null;
  land_value: number | null;
  monthly_rent: number | null;
  expansion_available: boolean;
  created_at: string;
  updated_at: string;
}

// ------------------------------------------
// PREDICTION
// ------------------------------------------

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH';

export interface PredictionResponse {
  prediction_id: number;
  startup_id: number;
  success_probability: number | null;
  predicted_annual_revenue: number | null;
  predicted_annual_profit: number | null;
  break_even_months: number | null;
  risk_level: RiskLevel | string | null;
  prediction_summary: string | null;
  assumptions: string | null; // serialized JSON array
  created_at: string;
}

// ------------------------------------------
// AI SUGGESTIONS
// ------------------------------------------

export type SuggestionPriority = 'HIGH' | 'MEDIUM' | 'LOW';

export interface AISuggestionResponse {
  suggestion_id: number;
  startup_id: number;
  prediction_id: number;
  title: string;
  description: string;
  priority: SuggestionPriority | string;
  category: string;
  created_at: string;
}

export interface AISuggestionGenerationResponse {
  startup_id: number;
  prediction_id: number;
  generated_count: number;
  suggestions: AISuggestionResponse[];
}

// ------------------------------------------
// REPORTS
// ------------------------------------------

export interface ReportResponse {
  report_id: number;
  startup_id: number;
  prediction_id: number | null;
  report_type: string;
  title: string;
  file_path: string | null;
  created_at: string;
}

// ------------------------------------------
// DASHBOARD
// ------------------------------------------

export interface DashboardResponse {
  total_startups: number;
  total_predictions: number;
  total_reports: number;
  recent_startups: StartupProfileResponse[];
  recent_predictions: PredictionResponse[];
}

// ------------------------------------------
// FULL STARTUP AGGREGATE BUNDLE
// (Client-side view model combining subresources)
// ------------------------------------------

export interface StartupFullData {
  profile: StartupProfileResponse;
  financial: FinancialInformationResponse | null;
  team: TeamInformationResponse | null;
  location: BusinessLocationResponse | null;
  land: LandDetailsResponse | null;
  latestPrediction: PredictionResponse | null;
  suggestions: AISuggestionResponse[];
  reports: ReportResponse[];
}
