import { useState } from 'react'
import type { SyntheticEvent } from 'react'
import type { CreateAgentInput } from '../api/agents'

interface CorpusDraft {
  name: string
  description: string
  files: File[]
}

export interface CreateAgentWorkspaceInput {
  agent: CreateAgentInput
  corpora: CorpusDraft[]
}

interface CreateAgentWorkspaceFormProps {
  isSubmitting: boolean
  progressMessage: string
  onSubmit: (input: CreateAgentWorkspaceInput) => Promise<void>
}

const initialAgentForm: CreateAgentInput = {
  name: '',
  description: '',
  use_case: '',
  language: 'fr',
}

const initialCorpusDraft: CorpusDraft = {
  name: '',
  description: '',
  files: [],
}

export function CreateAgentWorkspaceForm({
  isSubmitting,
  progressMessage,
  onSubmit,
}: CreateAgentWorkspaceFormProps) {
  const [agentForm, setAgentForm] = useState<CreateAgentInput>(initialAgentForm)
  const [corpora, setCorpora] = useState<CorpusDraft[]>([
    initialCorpusDraft,
  ])

  function updateCorpus(
    index: number,
    updatedCorpus: CorpusDraft,
  ) {
    setCorpora((currentCorpora) =>
      currentCorpora.map((corpus, corpusIndex) =>
        corpusIndex === index ? updatedCorpus : corpus,
      ),
    )
  }

  function addCorpus() {
    setCorpora((currentCorpora) => [
      ...currentCorpora,
      {
        name: '',
        description: '',
        files: [],
      },
    ])
  }

  function removeCorpus(index: number) {
    setCorpora((currentCorpora) =>
      currentCorpora.filter((_, corpusIndex) => corpusIndex !== index),
    )
  }

  async function handleSubmit(event: SyntheticEvent<HTMLFormElement>) {
    event.preventDefault()

    await onSubmit({
      agent: agentForm,
      corpora: corpora.filter((corpus) => corpus.name.trim()),
    })

    setAgentForm(initialAgentForm)
    setCorpora([initialCorpusDraft])
  }

  return (
    <form className="agent-workspace-form" onSubmit={handleSubmit}>
      <div className="agent-workspace-form__section">
        <p className="eyebrow">Agent</p>

        <label>
          Nom
          <input
            required
            minLength={3}
            maxLength={100}
            value={agentForm.name}
            onChange={(event) =>
              setAgentForm({ ...agentForm, name: event.target.value })
            }
            placeholder="Stage"
          />
        </label>

        <label>
          Cas d’usage
          <input
            required
            minLength={3}
            maxLength={200}
            value={agentForm.use_case}
            onChange={(event) =>
              setAgentForm({ ...agentForm, use_case: event.target.value })
            }
            placeholder="Répondre aux questions sur mon stage"
          />
        </label>

        <label>
          Description
          <textarea
            maxLength={500}
            value={agentForm.description}
            onChange={(event) =>
              setAgentForm({ ...agentForm, description: event.target.value })
            }
            placeholder="Décrivez la mission de l’agent."
          />
        </label>

        <label>
          Langue
          <select
            value={agentForm.language}
            onChange={(event) =>
              setAgentForm({ ...agentForm, language: event.target.value })
            }
          >
            <option value="fr">Français</option>
            <option value="en">Anglais</option>
          </select>
        </label>
      </div>

      <div className="agent-workspace-form__section">
        <div className="agent-workspace-form__header">
          <p className="eyebrow">Corpus et documents</p>

          <button type="button" onClick={addCorpus}>
            Ajouter un corpus
          </button>
        </div>

        {corpora.map((corpus, index) => (
          <article className="corpus-draft-card" key={index}>
            <div className="corpus-draft-card__header">
              <strong>Corpus {index + 1}</strong>

              {corpora.length > 1 && (
                <button type="button" onClick={() => removeCorpus(index)}>
                  Retirer
                </button>
              )}
            </div>

            <label>
              Nom du corpus
              <input
                required
                minLength={3}
                maxLength={100}
                value={corpus.name}
                onChange={(event) =>
                  updateCorpus(index, {
                    ...corpus,
                    name: event.target.value,
                  })
                }
                placeholder="Cahier des charges stage"
              />
            </label>

            <label>
              Description
              <textarea
                maxLength={500}
                value={corpus.description}
                onChange={(event) =>
                  updateCorpus(index, {
                    ...corpus,
                    description: event.target.value,
                  })
                }
                placeholder="Documents de référence du stage."
              />
            </label>

            <label>
              Fichiers PDF
              <input
                accept="application/pdf"
                multiple
                type="file"
                onChange={(event) =>
                  updateCorpus(index, {
                    ...corpus,
                    files: Array.from(event.target.files ?? []),
                  })
                }
              />
            </label>

            {corpus.files.length > 0 && (
              <ul className="selected-files-list">
                {corpus.files.map((file) => (
                  <li key={file.name}>{file.name}</li>
                ))}
              </ul>
            )}
          </article>
        ))}
      </div>

      {progressMessage && (
        <p className="progress-message">{progressMessage}</p>
      )}

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Création et indexation…' : 'Créer l’agent complet'}
      </button>
    </form>
  )
}