import type { Agent } from '../api/agents'

interface AgentListProps {
  agents: Agent[]
  selectedAgentId: string
  onSelectAgent: (agentId: string) => void
  onDeleteAgent: (agentId: string) => void
}

export function AgentList({
  agents,
  selectedAgentId,
  onSelectAgent,
  onDeleteAgent,
}: AgentListProps) {
  if (agents.length === 0) {
    return (
      <p className="empty-state">
        Aucun agent pour le moment. Créez votre premier agent.
      </p>
    )
  }

  return (
    <div className="agent-list">
      {agents.map((agent) => (
        <article
          className={`agent-card ${
            selectedAgentId === agent.id ? 'agent-card--selected' : ''
          }`}
          key={agent.id}
        >
          <button
            className="agent-card__select"
            type="button"
            onClick={() => onSelectAgent(agent.id)}
          >
            <div className="agent-card__header">
              <span>{agent.status === 'draft' ? 'Brouillon' : 'Publié'}</span>
              <small>{agent.language.toUpperCase()}</small>
            </div>

            <h3>{agent.name}</h3>
            <p>{agent.description || agent.use_case}</p>
            <strong>{agent.use_case}</strong>
          </button>

          <button
            className="agent-card__delete"
            type="button"
            onClick={() => onDeleteAgent(agent.id)}
          >
            Supprimer
          </button>
        </article>
      ))}
    </div>
  )
}

