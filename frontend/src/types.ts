export type Health = { status: string; version: string };

export type BeamSteeringRequest = {
  element_count: number;
  frequency_hz: number;
  spacing_m: number;
  target_angle_deg: number;
  reflection_magnitude: number;
  angle_start_deg: number;
  angle_stop_deg: number;
  sample_count: number;
  incident_angle_deg?: number;
  element_pattern?: "isotropic" | "cosine" | "cosine_squared";
  phase_quantization_bits?: number | null;
  coupled_loss_model?: boolean;
};

export type BeamSteeringResult = {
  model_id: string;
  wavelength_m: number;
  wavenumber_rad_m: number;
  element_positions_m: number[];
  angles_deg: number[];
  baseline_phases_deg: number[];
  controlled_phases_deg: number[];
  baseline_normalized_power: number[];
  controlled_normalized_power: number[];
  baseline_normalized_power_db: number[];
  controlled_normalized_power_db: number[];
  target_metrics: {
    baseline_normalized_power: number;
    controlled_normalized_power: number;
    improvement_db: number | null;
  };
  sampled_main_lobe_angles_deg: { baseline: number | null; controlled: number | null };
  research_metrics?: {
    hpbw_deg: number | null;
    psll_db: number | null;
    directivity_dbi: number | null;
    pointing_error_deg: number | null;
    target_lobe_angle_deg?: number | null;
    target_lobe_pointing_error_deg?: number | null;
    competing_lobe_detected?: boolean;
  };
  warnings: string[];
  limitations: string[];
  db_floor_power: number;
};

export type TradeoffRequest = Omit<BeamSteeringRequest, "target_angle_deg"> & {
  receiver_angle_deg: number;
  observation_angle_deg: number;
  penalty: number;
  max_evaluations: number;
  observation_power_threshold?: number;
};

type PatternResult = {
  angles_deg: number[];
  normalized_power: number[];
  normalized_power_db: number[];
  phases_deg: number[];
};

export type TradeoffResult = {
  initial: PatternResult;
  optimized: PatternResult;
  initial_objective: number;
  final_objective: number;
  initial_receiver_power: number;
  final_receiver_power: number;
  initial_observation_power: number;
  final_observation_power: number;
  evaluation_count: number;
  stop_reason: string;
  constraint_status: string;
  scientific_note: string;
};

