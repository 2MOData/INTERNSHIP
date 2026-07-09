import { useState } from 'react'
import type { SyntheticEvent } from 'react'
import type {
  AskCorpusQuestionInput,
  CorpusAnswerResponse,
} from '../api/answers'

interface AskCorpusFormProps {
  answer: CorpusAnswerResponse | null
  errorMessage: string
  isSubmitting: boolean
  selectedCorpusId: string
  onSubmit: (input: AskCorpusQuestionInput) => Promise<void>
}

export function AskCorpusForm({
  answer,
  errorMessage,
  isSubmitting,
  selectedCorpusId,
  onSubmit,
}: AskCorpusFormProps) {
  const [question, setQuestion] = useState('')
  const [limit, setLimit] = useState(5)

  async function handleSubmit(event: SyntheticEvent<HTMLFormElement>) {
    event.preventDefault()

    await onSubmit({
      corpusId: selectedCorpusId,
      question,
      limit,
    })
  }

  return (
    <div className="answer-workspace">
      <form className="answer-form" onSubmit={handleSubmit}>
        <label>
          Corpus sélectionné
          <input
            readOnly
            value={selectedCorpusId || 'Aucun corpus sélectionné'}
          />
        </label>

        <label>
          Question
          <textarea
            required
            minLength={3}
            maxLength={1000}
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Posez une question à partir des documents du corpus."
          />
        </label>

        <label>
          Nombre de sources à utiliser
          <input
            required
            min={1}
            max={20}
            type="number"
            value={limit}
            onChange={(event) => setLimit(Number(event.target.value))}
          />
        </label>

        <button type="submit" disabled={isSubmitting || !selectedCorpusId}>
          {isSubmitting ? 'Recherche…' : 'Poser la question'}
        </button>
      </form>

      <div className="answer-result" aria-live="polite">
        {errorMessage && <p className="error-message">{errorMessage}</p>}

        {!answer && !errorMessage && (
          <p className="empty-state">
            Sélectionnez un corpus puis posez une question.
          </p>
        )}

        {answer && (
          <>
            <article className="answer-card">
              <p className="eyebrow">Réponse</p>
              <p>{answer.answer}</p>
            </article>

            <div className="sources-list">
              <p className="eyebrow">Sources utilisées</p>

              {answer.sources.map((source) => (
                <article className="source-card" key={source.chunk_id}>
                  <div className="source-card__header">
                    <strong>Page {source.page_number}</strong>
                    <span>Score {source.score.toFixed(3)}</span>
                  </div>

                  <p>{source.text}</p>

                  <small>Source ID : {source.source_id}</small>
                </article>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  )
}