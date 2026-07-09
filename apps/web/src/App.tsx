import { createAgent, listAgents } from './api/agents'
import type { Agent, CreateAgentInput } from './api/agents'

import { AgentList } from './components/AgentList'
import { CreateAgentForm } from './components/CreateAgentForm'

import { useEffect, useState } from 'react'
import './App.css'
import { getApiHealth } from './api/health'
import { askCorpusQuestion } from './api/answers'
import type {
  AskCorpusQuestionInput,
  CorpusAnswerResponse,
} from './api/answers'
import { AskCorpusForm } from './components/AskCorpusForm'
import { listAgentCorpora } from './api/corpora'
import type { Corpus } from './api/corpora'
import { CorpusList } from './components/CorpusList'

type ApiStatus = 'loading' | 'connected' | 'unavailable'

function App() {
  const [apiStatus, setApiStatus] = useState<ApiStatus>('loading')
  const [agents, setAgents] = useState<Agent[]>([])
  const [agentsError, setAgentsError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [answer, setAnswer] = useState<CorpusAnswerResponse | null>(null)
  const [answerError, setAnswerError] = useState('')
  const [isAnswering, setIsAnswering] = useState(false)
  const [selectedAgentId, setSelectedAgentId] = useState('')
  const [corpora, setCorpora] = useState<Corpus[]>([])
  const [corporaError, setCorporaError] = useState('')
  const [isLoadingCorpora, setIsLoadingCorpora] = useState(false)
  const [selectedCorpusId, setSelectedCorpusId] = useState('')

  useEffect(() => {
    getApiHealth()
      .then(() => setApiStatus('connected'))
      .catch(() => setApiStatus('unavailable'))

    listAgents()
      .then(setAgents)
      .catch(() => setAgentsError('Impossible de charger les agents.'))
  }, [])

  async function handleCreateAgent(agentInput: CreateAgentInput) {
    setIsSubmitting(true)
    setAgentsError('')

    try {
      const createdAgent = await createAgent(agentInput)
      setAgents((currentAgents) => [...currentAgents, createdAgent])
    } catch {
      setAgentsError('Impossible de créer l’agent.')
      throw new Error('Agent creation failed')
    } finally {
      setIsSubmitting(false)
    }
  }
  async function handleAskCorpusQuestion(input: AskCorpusQuestionInput) {
    setIsAnswering(true)
    setAnswerError('')
    setAnswer(null)

    try {
      const generatedAnswer = await askCorpusQuestion(input)
      setAnswer(generatedAnswer)
    } catch {
      setAnswerError(
        'Impossible de générer une réponse. Vérifiez le corpus et la configuration IA.',
      )
    } finally {
      setIsAnswering(false)
    }
  }

  async function handleSelectAgent(agentId: string) {
    setSelectedAgentId(agentId)
    setSelectedCorpusId('')
    setCorpora([])
    setCorporaError('')
    setIsLoadingCorpora(true)

    try {
      const agentCorpora = await listAgentCorpora(agentId)
      setCorpora(agentCorpora)

      if (agentCorpora.length > 0) {
        setSelectedCorpusId(agentCorpora[0].id)
      }
    } catch {
      setCorporaError('Impossible de charger les corpus de cet agent.')
    } finally {
      setIsLoadingCorpora(false)
    }
  }
  return (
    <main className="landing-page">
      <section className="hero">
        <p className="eyebrow">Domain-Specific Knowledge Agents</p>
        
        <div className={`api-status api-status--${apiStatus}`}>
          <span aria-hidden="true" />
          {apiStatus === 'loading' && 'Connexion à l’API…'}
          {apiStatus === 'connected' && 'API connectée'}
          {apiStatus === 'unavailable' && 'API indisponible'}
        </div>
        
        <h1>Transformez vos connaissances en actions fiables.</h1>

        <p className="hero-description">
          Créez des agents spécialisés capables de répondre à partir de vos
          documents et d'automatiser des tâches métier sous votre contrôle.
        </p>

        <button type="button">Commencer</button>
      </section>

      <section className="capabilities" aria-label="Capacités principales">
        <article>
          <span aria-hidden="true">01</span>
          <h2>Réponses sourcées</h2>
          <p>
            Chaque réponse s'appuie sur les documents associés à l'agent et
            affiche les sources utilisées.
          </p>
        </article>

        <article>
          <span aria-hidden="true">02</span>
          <h2>Automatisations contrôlées</h2>
          <p>
            Déclenchez des actions métier et ajoutez une validation humaine
            lorsque la situation l'exige.
          </p>
        </article>
      </section>
      <section className="agents-section" aria-labelledby="agents-title">
        <div className="agents-section__header">
          <div>
            <p className="eyebrow">Première ressource métier</p>
            <h2 id="agents-title">Vos agents</h2>
          </div>

          <p>{agents.length} agent(s)</p>
        </div>

        {agentsError && <p className="error-message">{agentsError}</p>}

        <div className="agents-workspace">
          <CreateAgentForm
            isSubmitting={isSubmitting}
            onSubmit={handleCreateAgent}
          />

          <AgentList
            agents={agents}
            selectedAgentId={selectedAgentId}
            onSelectAgent={handleSelectAgent}
          />
        </div>
        <div className="corpus-panel">
          <p className="eyebrow">Corpus de l’agent sélectionné</p>

          {corporaError && <p className="error-message">{corporaError}</p>}

          {!selectedAgentId && (
            <p className="empty-state">
              Sélectionnez un agent pour afficher ses corpus.
            </p>
          )}

          {selectedAgentId && (
            <CorpusList
              corpora={corpora}
              isLoading={isLoadingCorpora}
              selectedCorpusId={selectedCorpusId}
              onSelectCorpus={setSelectedCorpusId}
            />
          )}
        </div>
      </section>
      <section className="answer-section" aria-labelledby="answer-title">
        <div className="agents-section__header">
          <div>
            <p className="eyebrow">Réponse sourcée</p>
            <h2 id="answer-title">Interroger un corpus</h2>
          </div>

          <p>RAG MVP</p>
        </div>

        <AskCorpusForm
          answer={answer}
          errorMessage={answerError}
          isSubmitting={isAnswering}
          selectedCorpusId={selectedCorpusId}
          onSubmit={handleAskCorpusQuestion}
        />
      </section>
    </main>
  )
}

export default App