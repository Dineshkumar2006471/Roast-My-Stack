import axios from "axios";

export type RoastResult = {
  roast: string;
  issues: Array<{
    type: string;
    line: number | null;
    description: string;
    severity: "critical" | "high" | "medium" | "low";
  }>;
  fixPlan: Array<{
    issue: string;
    fix: string;
    priority: number;
  }>;
  scores: {
    codeQuality: number;
    security: number;
    efficiency: number;
    testing: number;
    accessibility: number;
  };
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export const submitRoast = async (sourceType: "github" | "snippet", content: string, intensity: string): Promise<RoastResult> => {
  const response = await axios.post(`${API_BASE_URL}/api/roast`, {
    source_type: sourceType,
    content: content,
    intensity: intensity,
  });
  
  return response.data;
};
