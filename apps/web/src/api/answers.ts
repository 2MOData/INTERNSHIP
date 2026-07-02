export interface CorpusAnswerSource {
  chunk_id: string
  source_id: string
  page_number: number
  text: string
  score: number
}

export interface CorpusAnswerResponse {
  answer: string
  sources: CorpusAnswerSource[]
}

export interface AskCorpusQuestionInput {
  corpusId: string
  question: string
  limit: number
}

const API_URL = 'http://localhost:8000'

export async function askCorpusQuestion(
  input: AskCorpusQuestionInput,
): Promise<CorpusAnswerResponse> {
  const response = await fetch(`${API_URL}/api/corpora/${input.corpusId}/answer`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      question: input.question,
      limit: input.limit,
    }),
  })

  if (!response.ok) {
    throw new Error(`Corpus answer request failed with status ${response.status}`)
  }

  return response.json() as Promise<CorpusAnswerResponse>
}