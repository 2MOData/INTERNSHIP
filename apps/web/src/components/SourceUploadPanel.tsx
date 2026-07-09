import { useState } from 'react'
import type { SyntheticEvent } from 'react'
import {
  generateSourceChunks,
  generateSourceEmbeddings,
  uploadPdfSource,
} from '../api/sources'
import type { Source } from '../api/sources'

interface SourceUploadPanelProps {
  selectedCorpusId: string
}

export function SourceUploadPanel({
  selectedCorpusId,
}: SourceUploadPanelProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [source, setSource] = useState<Source | null>(null)
  const [message, setMessage] = useState('')
  const [errorMessage, setErrorMessage] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const [isGeneratingChunks, setIsGeneratingChunks] = useState(false)
  const [isGeneratingEmbeddings, setIsGeneratingEmbeddings] = useState(false)

  async function handleUpload(event: SyntheticEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!selectedCorpusId || !selectedFile) {
      return
    }

    setIsUploading(true)
    setMessage('')
    setErrorMessage('')

    try {
      const uploadedSource = await uploadPdfSource(
        selectedCorpusId,
        selectedFile,
      )

      setSource(uploadedSource)
      setMessage('PDF uploadé et texte extrait avec succès.')
    } catch {
      setErrorMessage('Impossible d’uploader le PDF.')
    } finally {
      setIsUploading(false)
    }
  }

  async function handleGenerateChunks() {
    if (!source) {
      return
    }

    setIsGeneratingChunks(true)
    setMessage('')
    setErrorMessage('')

    try {
      const chunks = await generateSourceChunks(source.id)
      setMessage(`${chunks.length} chunk(s) généré(s).`)
    } catch {
      setErrorMessage('Impossible de générer les chunks.')
    } finally {
      setIsGeneratingChunks(false)
    }
  }

  async function handleGenerateEmbeddings() {
    if (!source) {
      return
    }

    setIsGeneratingEmbeddings(true)
    setMessage('')
    setErrorMessage('')

    try {
      const result = await generateSourceEmbeddings(source.id)
      setMessage(`${result.created} embedding(s) généré(s).`)
    } catch {
      setErrorMessage(
        'Impossible de générer les embeddings. Vérifiez la clé API et le quota.',
      )
    } finally {
      setIsGeneratingEmbeddings(false)
    }
  }

  return (
    <section className="source-upload-panel" aria-labelledby="source-upload-title">
      <div className="agents-section__header">
        <div>
          <p className="eyebrow">Documents</p>
          <h2 id="source-upload-title">Indexer un PDF</h2>
        </div>
      </div>

      {!selectedCorpusId && (
        <p className="empty-state">
          Sélectionnez un corpus avant d’uploader un document.
        </p>
      )}

      {selectedCorpusId && (
        <div className="source-upload-workspace">
          <form className="source-upload-form" onSubmit={handleUpload}>
            <label>
              Fichier PDF
              <input
                accept="application/pdf"
                required
                type="file"
                onChange={(event) =>
                  setSelectedFile(event.target.files?.[0] ?? null)
                }
              />
            </label>

            <button type="submit" disabled={isUploading || !selectedFile}>
              {isUploading ? 'Upload…' : 'Uploader le PDF'}
            </button>
          </form>

          <div className="source-indexing-panel">
            {message && <p className="success-message">{message}</p>}
            {errorMessage && <p className="error-message">{errorMessage}</p>}

            {!source && (
              <p className="empty-state">
                La source apparaîtra ici après l’upload.
              </p>
            )}

            {source && (
              <article className="source-card">
                <p className="eyebrow">Source uploadée</p>
                <h3>{source.original_filename}</h3>
                <p>Statut : {source.status}</p>
                <small>Source ID : {source.id}</small>

                <div className="source-actions">
                  <button
                    type="button"
                    disabled={isGeneratingChunks}
                    onClick={handleGenerateChunks}
                  >
                    {isGeneratingChunks
                      ? 'Génération…'
                      : 'Générer les chunks'}
                  </button>

                  <button
                    type="button"
                    disabled={isGeneratingEmbeddings}
                    onClick={handleGenerateEmbeddings}
                  >
                    {isGeneratingEmbeddings
                      ? 'Génération…'
                      : 'Générer les embeddings'}
                  </button>
                </div>
              </article>
            )}
          </div>
        </div>
      )}
    </section>
  )
}