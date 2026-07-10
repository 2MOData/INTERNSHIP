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

export interface CreateCorpusInput {
  name: string
  description: string
}

const API_URL = 'http://localhost:8000'

export async function listAgentCorpora(agentId: string): Promise<Corpus[]> {
  const response = await fetch(`${API_URL}/api/agents/${agentId}/corpora`)

  if (!response.ok) {
    throw new Error(`Corpora request failed with status ${response.status}`)
  }

  return response.json() as Promise<Corpus[]>
}

export async function createAgentCorpus(
  agentId: string,
  corpusInput: CreateCorpusInput,
): Promise<Corpus> {
  const response = await fetch(`${API_URL}/api/agents/${agentId}/corpora`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(corpusInput),
  })

  if (!response.ok) {
    throw new Error(`Corpus creation failed with status ${response.status}`)
  }

  return response.json() as Promise<Corpus>
}