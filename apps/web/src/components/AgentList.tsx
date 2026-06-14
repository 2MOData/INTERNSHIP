import type { Agent } from '../api/agents'

interface AgentListProps {
  agents: Agent[]
}

export function AgentList({ agents }: AgentListProps) {
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
        <article className="agent-card" key={agent.id}>
          <div className="agent-card__header">
            <span>{agent.status === 'draft' ? 'Brouillon' : 'Publié'}</span>
            <small>{agent.language.toUpperCase()}</small>
          </div>

          <h3>{agent.name}</h3>
          <p>{agent.description || agent.use_case}</p>
          <strong>{agent.use_case}</strong>
        </article>
      ))}
    </div>
  )
}