import type { Corpus } from '../api/corpora'

interface CorpusListProps {
  corpora: Corpus[]
  isLoading: boolean
  selectedCorpusId: string
  onSelectCorpus: (corpusId: string) => void
}

export function CorpusList({
  corpora,
  isLoading,
  selectedCorpusId,
  onSelectCorpus,
}: CorpusListProps) {
  if (isLoading) {
    return <p className="empty-state">Chargement des corpus…</p>
  }

  if (corpora.length === 0) {
    return (
      <p className="empty-state">
        Aucun corpus pour cet agent. Créez un corpus via l’API pour le moment.
      </p>
    )
  }

  return (
    <div className="corpus-list">
      {corpora.map((corpus) => (
        <button
          className={`corpus-card ${
            selectedCorpusId === corpus.id ? 'corpus-card--selected' : ''
          }`}
          key={corpus.id}
          type="button"
          onClick={() => onSelectCorpus(corpus.id)}
        >
          <div className="corpus-card__header">
            <strong>{corpus.name}</strong>
            <span>{corpus.status}</span>
          </div>

          <p>{corpus.description || 'Aucune description.'}</p>
        </button>
      ))}
    </div>
  )
}