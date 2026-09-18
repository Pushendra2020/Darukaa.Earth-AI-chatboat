export interface Recommendation {
  action: string;
  why_it_works: string;
  impacted_metrics: string[];
  time_horizon: string;
  evidence_ids: string[];
  confidence: number;
  evidence: any[];
}

export interface ChatResponse {
  conversation_id: string;
  answer: string;
  clarification_required: boolean;
  recommendations: Recommendation[];
}

export async function sendMessage(
  message: string,
  conversationId?: string,
  environment?: any,
  location?: any
): Promise<ChatResponse> {
  const payload = {
    conversation_id: conversationId,
    message,
    environment,
    location
  };

  const response = await fetch("http://localhost:8000/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error("Failed to communicate with backend");
  }

  return response.json();
}
