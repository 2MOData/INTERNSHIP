export interface HealthResponse {
  status: string
  service: string
}

export async function getApiHealth(): Promise<HealthResponse> {
  const response = await fetch('http://localhost:8000/health')

  if (!response.ok) {
    throw new Error(`Health request failed with status ${response.status}`)
  }

  return response.json() as Promise<HealthResponse>
}