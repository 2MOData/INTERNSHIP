export type CorpusStatus = 'empty' | 'indexing' | 'ready' | 'error'

export interface Corpus {
  id: string
  agent_id: string
  name: string
  description: string
  status: CorpusStatus
  created_at: string
  updated_at: string
}

const API_URL = 'http://localhost:8000'

export async function listAgentCorpora(agentId: string): Promise<Corpus[]> {
  const response = await fetch(`${API_URL}/api/agents/${agentId}/corpora`)

  if (!response.ok) {
    throw new Error(`Corpora request failed with status ${response.status}`)
  }

  return response.json() as Promise<Corpus[]>
}