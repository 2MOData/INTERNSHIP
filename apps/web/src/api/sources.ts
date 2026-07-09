export type SourceStatus = 'uploaded' | 'processing' | 'ready' | 'error'

export interface Source {
  id: string
  corpus_id: string
  source_type: string
  original_filename: string
  content_type: string
  size_bytes: number
  status: SourceStatus
  created_at: string
  updated_at: string
}

export interface SourceChunk {
  id: string
  source_id: string
  page_number: number
  chunk_index: number
  text: string
  created_at: string
}

export interface EmbeddingGenerationResult {
  created: number
}

const API_URL = 'http://localhost:8000'

export async function uploadPdfSource(
  corpusId: string,
  file: File,
): Promise<Source> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_URL}/api/corpora/${corpusId}/sources/pdf`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    throw new Error(`PDF upload failed with status ${response.status}`)
  }

  return response.json() as Promise<Source>
}

export async function generateSourceChunks(
  sourceId: string,
): Promise<SourceChunk[]> {
  const response = await fetch(`${API_URL}/api/sources/${sourceId}/chunks`, {
    method: 'POST',
  })

  if (!response.ok) {
    throw new Error(`Chunk generation failed with status ${response.status}`)
  }

  return response.json() as Promise<SourceChunk[]>
}

export async function generateSourceEmbeddings(
  sourceId: string,
): Promise<EmbeddingGenerationResult> {
  const response = await fetch(`${API_URL}/api/sources/${sourceId}/embeddings`, {
    method: 'POST',
  })

  if (!response.ok) {
    throw new Error(`Embedding generation failed with status ${response.status}`)
  }

  return response.json() as Promise<EmbeddingGenerationResult>
}