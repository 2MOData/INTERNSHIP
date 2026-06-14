import { useState } from 'react'
import type { SyntheticEvent } from 'react'
import type { CreateAgentInput } from '../api/agents'
interface CreateAgentFormProps {
  isSubmitting: boolean
  onSubmit: (agentInput: CreateAgentInput) => Promise<void>
}

const initialForm: CreateAgentInput = {
  name: '',
  description: '',
  use_case: '',
  language: 'fr',
}

export function CreateAgentForm({
  isSubmitting,
  onSubmit,
}: CreateAgentFormProps) {
  const [form, setForm] = useState<CreateAgentInput>(initialForm)

  async function handleSubmit(event: SyntheticEvent<HTMLFormElement>) {
    event.preventDefault()
    await onSubmit(form)
    setForm(initialForm)
  }

  return (
    <form className="agent-form" onSubmit={handleSubmit}>
      <label>
        Nom
        <input
          required
          minLength={3}
          maxLength={100}
          value={form.name}
          onChange={(event) =>
            setForm({ ...form, name: event.target.value })
          }
          placeholder="Baggage Policy Agent"
        />
      </label>

      <label>
        Cas d’usage
        <input
          required
          minLength={3}
          maxLength={200}
          value={form.use_case}
          onChange={(event) =>
            setForm({ ...form, use_case: event.target.value })
          }
          placeholder="Répondre aux questions bagages"
        />
      </label>

      <label>
        Description
        <textarea
          maxLength={500}
          value={form.description}
          onChange={(event) =>
            setForm({ ...form, description: event.target.value })
          }
          placeholder="Décrivez la mission de l’agent."
        />
      </label>

      <label>
        Langue
        <select
          value={form.language}
          onChange={(event) =>
            setForm({ ...form, language: event.target.value })
          }
        >
          <option value="fr">Français</option>
          <option value="en">Anglais</option>
        </select>
      </label>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Création…' : 'Créer l’agent'}
      </button>
    </form>
  )
}