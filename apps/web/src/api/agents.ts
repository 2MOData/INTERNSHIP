export type AgentStatus = 'draft' | 'published'

export interface Agent {
  id: string
  name: string
  description: string
  use_case: string
  language: string
  status: AgentStatus
  created_at: string
}

export interface CreateAgentInput {
  name: string
  description: string
  use_case: string
  language: string
}

const API_URL = 'http://localhost:8000'

export async function listAgents(): Promise<Agent[]> {
  const response = await fetch(`${API_URL}/api/agents`)

  if (!response.ok) {
    throw new Error(`Agents request failed with status ${response.status}`)
  }

  return response.json() as Promise<Agent[]>
}

export async function createAgent(
  agentInput: CreateAgentInput,
): Promise<Agent> {
  const response = await fetch(`${API_URL}/api/agents`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(agentInput),
  })

  if (!response.ok) {
    throw new Error(`Agent creation failed with status ${response.status}`)
  }

  return response.json() as Promise<Agent>
}