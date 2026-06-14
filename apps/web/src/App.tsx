import './App.css'

function App() {
  return (
    <main className="landing-page">
      <section className="hero">
        <p className="eyebrow">Domain-Specific Knowledge Agents</p>

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
    </main>
  )
}

export default App