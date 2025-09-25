// WorldClass RAG integration for SLM Legal Anti-alucinación
// Simplified TypeScript version of the Python worldclass-rag system

interface Document {
  id: string
  content: string
  metadata: {
    source: string
    type: 'ley' | 'decreto' | 'codigo' | 'constitucion' | 'jurisprudencia'
    numero?: string
    articulo?: string
    fecha?: string
    jurisdiccion: string
    jerarquia: number
    vigente: boolean
  }
}

interface Chunk {
  id: string
  content: string
  document_id: string
  metadata: Document['metadata']
  start_char?: number
  end_char?: number
  similarity?: number
}

interface EmbeddingModel {
  embed(texts: string[]): Promise<number[][]>
  embedSingle(text: string): Promise<number[]>
}

// Mock embedding model for MVP (replace with real embeddings later)
class MockEmbeddings implements EmbeddingModel {
  async embed(texts: string[]): Promise<number[][]> {
    return texts.map(text => this.generateMockEmbedding(text))
  }

  async embedSingle(text: string): Promise<number[]> {
    return this.generateMockEmbedding(text)
  }

  private generateMockEmbedding(text: string): number[] {
    // Generate consistent mock embedding based on text content
    const words = text.toLowerCase().split(/\\s+/)
    const embedding = new Array(384).fill(0)
    
    // Simple hash-based embedding simulation
    for (let i = 0; i < words.length; i++) {
      const word = words[i]
      const hash = this.simpleHash(word)
      const idx = Math.abs(hash) % 384
      embedding[idx] += 1 / Math.sqrt(words.length)
    }
    
    // Normalize
    const norm = Math.sqrt(embedding.reduce((sum, val) => sum + val * val, 0))
    return embedding.map(val => val / (norm || 1))
  }

  private simpleHash(str: string): number {
    let hash = 0
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i)
      hash = ((hash << 5) - hash) + char
      hash = hash & hash // Convert to 32-bit integer
    }
    return hash
  }
}

// Chunking strategies
class SemanticChunker {
  constructor(private maxChunkSize = 512, private overlap = 50) {}

  chunk(document: Document): Chunk[] {
    const sentences = this.splitIntoSentences(document.content)
    const chunks: Chunk[] = []
    let currentChunk = ''
    let startChar = 0

    for (let i = 0; i < sentences.length; i++) {
      const sentence = sentences[i]
      
      if (currentChunk.length + sentence.length > this.maxChunkSize && currentChunk.length > 0) {
        // Create chunk
        chunks.push({
          id: `${document.id}-chunk-${chunks.length}`,
          content: currentChunk.trim(),
          document_id: document.id,
          metadata: document.metadata,
          start_char: startChar,
          end_char: startChar + currentChunk.length
        })
        
        // Start new chunk with overlap
        const overlapSentences = sentences.slice(Math.max(0, i - 2), i)
        currentChunk = overlapSentences.join(' ') + ' ' + sentence
        startChar += currentChunk.length - sentence.length - overlapSentences.join(' ').length - 2
      } else {
        currentChunk += (currentChunk ? ' ' : '') + sentence
      }
    }

    // Add final chunk if any content remains
    if (currentChunk.trim()) {
      chunks.push({
        id: `${document.id}-chunk-${chunks.length}`,
        content: currentChunk.trim(),
        document_id: document.id,
        metadata: document.metadata,
        start_char: startChar,
        end_char: startChar + currentChunk.length
      })
    }

    return chunks
  }

  private splitIntoSentences(text: string): string[] {
    // Simple Spanish sentence splitting
    return text
      .split(/[.!?]+/)
      .map(s => s.trim())
      .filter(s => s.length > 0)
      .map(s => s + '.')
  }
}

// Vector similarity calculation
class VectorUtils {
  static cosineSimilarity(a: number[], b: number[]): number {
    if (a.length !== b.length) return 0
    
    let dotProduct = 0
    let normA = 0
    let normB = 0
    
    for (let i = 0; i < a.length; i++) {
      dotProduct += a[i] * b[i]
      normA += a[i] * a[i]
      normB += b[i] * b[i]
    }
    
    return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB))
  }

  static topK<T extends { similarity: number }>(items: T[], k: number): T[] {
    return items
      .sort((a, b) => b.similarity - a.similarity)
      .slice(0, k)
  }
}

// BM25 scoring for keyword search
class BM25Scorer {
  private k1 = 1.2
  private b = 0.75
  private termFreqs: Map<string, Map<string, number>> = new Map()
  private docFreqs: Map<string, number> = new Map()
  private docLengths: Map<string, number> = new Map()
  private avgDocLength = 0
  private totalDocs = 0

  buildIndex(chunks: Chunk[]): void {
    this.termFreqs.clear()
    this.docFreqs.clear()
    this.docLengths.clear()
    
    let totalLength = 0
    
    for (const chunk of chunks) {
      const terms = this.tokenize(chunk.content)
      const uniqueTerms = new Set(terms)
      
      this.docLengths.set(chunk.id, terms.length)
      totalLength += terms.length
      
      // Term frequencies for this document
      const tfMap = new Map<string, number>()
      for (const term of terms) {
        tfMap.set(term, (tfMap.get(term) || 0) + 1)
      }
      this.termFreqs.set(chunk.id, tfMap)
      
      // Document frequencies
      for (const term of uniqueTerms) {
        this.docFreqs.set(term, (this.docFreqs.get(term) || 0) + 1)
      }
    }
    
    this.totalDocs = chunks.length
    this.avgDocLength = totalLength / this.totalDocs
  }

  score(query: string, chunkId: string): number {
    const queryTerms = this.tokenize(query)
    const docTf = this.termFreqs.get(chunkId)
    const docLength = this.docLengths.get(chunkId)
    
    if (!docTf || !docLength) return 0
    
    let score = 0
    
    for (const term of queryTerms) {
      const tf = docTf.get(term) || 0
      const df = this.docFreqs.get(term) || 0
      
      if (tf > 0) {
        const idf = Math.log((this.totalDocs - df + 0.5) / (df + 0.5))
        const tfScore = (tf * (this.k1 + 1)) / (tf + this.k1 * (1 - this.b + this.b * (docLength / this.avgDocLength)))
        score += idf * tfScore
      }
    }
    
    return score
  }

  private tokenize(text: string): string[] {
    return text
      .toLowerCase()
      .replace(/[^a-záéíóúñü\\s]/g, '')
      .split(/\\s+/)
      .filter(token => token.length > 2)
  }
}

// Hybrid retriever combining semantic and keyword search
class HybridRetriever {
  private chunks: Chunk[] = []
  private chunkEmbeddings: Map<string, number[]> = new Map()
  private bm25Scorer = new BM25Scorer()
  
  constructor(
    private embeddings: EmbeddingModel,
    private semanticWeight = 0.7,
    private keywordWeight = 0.3
  ) {}

  async addChunks(chunks: Chunk[]): Promise<void> {
    this.chunks = chunks
    
    // Generate embeddings for all chunks
    const contents = chunks.map(c => c.content)
    const embeddings = await this.embeddings.embed(contents)
    
    for (let i = 0; i < chunks.length; i++) {
      this.chunkEmbeddings.set(chunks[i].id, embeddings[i])
    }
    
    // Build BM25 index
    this.bm25Scorer.buildIndex(chunks)
  }

  async search(query: string, topK = 5, filters?: Partial<Document['metadata']>): Promise<Chunk[]> {
    if (this.chunks.length === 0) return []
    
    // Filter chunks first if filters provided
    let candidates = this.chunks
    if (filters) {
      candidates = this.chunks.filter(chunk => {
        return Object.entries(filters).every(([key, value]) => {
          const chunkValue = (chunk.metadata as any)[key]
          return chunkValue === value
        })
      })
    }
    
    if (candidates.length === 0) return []
    
    // Get query embedding
    const queryEmbedding = await this.embeddings.embedSingle(query)
    
    // Calculate combined scores
    const scoredChunks = candidates.map(chunk => {
      const embedding = this.chunkEmbeddings.get(chunk.id)
      if (!embedding) return { ...chunk, similarity: 0 }
      
      // Semantic similarity
      const semanticScore = VectorUtils.cosineSimilarity(queryEmbedding, embedding)
      
      // Keyword similarity (BM25)
      const keywordScore = this.bm25Scorer.score(query, chunk.id)
      
      // Normalize BM25 score (simple approach)
      const normalizedKeywordScore = Math.min(keywordScore / 10, 1)
      
      // Combined score
      const similarity = this.semanticWeight * semanticScore + this.keywordWeight * normalizedKeywordScore
      
      return {
        ...chunk,
        similarity
      }
    })
    
    return VectorUtils.topK(scoredChunks, topK)
  }

  getStats() {
    return {
      totalChunks: this.chunks.length,
      embeddingsGenerated: this.chunkEmbeddings.size,
      semanticWeight: this.semanticWeight,
      keywordWeight: this.keywordWeight
    }
  }
}

// Main WorldClass RAG Engine
export class WorldClassRAGEngine {
  private documents: Document[] = []
  private chunks: Chunk[] = []
  private retriever: HybridRetriever
  private chunker: SemanticChunker
  
  constructor() {
    const embeddings = new MockEmbeddings()
    this.retriever = new HybridRetriever(embeddings)
    this.chunker = new SemanticChunker(512, 50)
  }

  async addDocument(document: Document): Promise<void> {
    this.documents.push(document)
    
    // Create chunks
    const newChunks = this.chunker.chunk(document)
    this.chunks.push(...newChunks)
    
    // Update retriever
    await this.retriever.addChunks(this.chunks)
  }

  async addDocuments(documents: Document[]): Promise<void> {
    for (const doc of documents) {
      await this.addDocument(doc)
    }
  }

  async query(
    query: string, 
    options: {
      topK?: number
      filters?: Partial<Document['metadata']>
      includeMetadata?: boolean
    } = {}
  ): Promise<{
    chunks: Chunk[]
    totalChunks: number
    processingTime: number
    query: string
  }> {
    const startTime = performance.now()
    
    const chunks = await this.retriever.search(
      query, 
      options.topK || 5, 
      options.filters
    )
    
    const processingTime = performance.now() - startTime
    
    return {
      chunks,
      totalChunks: this.chunks.length,
      processingTime,
      query
    }
  }

  getStats() {
    return {
      documents: this.documents.length,
      chunks: this.chunks.length,
      retriever: this.retriever.getStats()
    }
  }

  // Get document by ID
  getDocument(id: string): Document | undefined {
    return this.documents.find(doc => doc.id === id)
  }

  // Get chunks for a specific document
  getDocumentChunks(documentId: string): Chunk[] {
    return this.chunks.filter(chunk => chunk.document_id === documentId)
  }
}

// Export types and classes
export type { Document, Chunk, EmbeddingModel }
export { MockEmbeddings, SemanticChunker, HybridRetriever, VectorUtils }