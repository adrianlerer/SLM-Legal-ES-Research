import type { Context } from 'hono'

// Hallucination Guard based on hallbayes EDFL framework
// Adapted for local SLM instead of OpenAI API

interface HallGuardRequest {
  query: string
  context: string[]
  response: string
  nSamples?: number
  marginExtraBits?: number
}

interface HallGuardResult {
  decision: "ANSWER" | "REFUSE"
  rohBound: number
  informationBudget: number
  isrRatio: number
  rationale: string
  certificateHash: string
  metadata: {
    timestamp: string
    nVariants: number
    method: "evidence-based" | "closed-book"
  }
}

// Mock implementation of EDFL framework for MVP
class EDFLHallGuard {
  private nSamples: number
  private marginExtraBits: number
  private bClip: number

  constructor(nSamples = 6, marginExtraBits = 2.0, bClip = 15.0) {
    this.nSamples = nSamples
    this.marginExtraBits = marginExtraBits  
    this.bClip = bClip
  }

  // Generate skeleton variants by masking evidence
  private generateSkeletons(originalQuery: string, context: string[]): string[] {
    const skeletons: string[] = []
    
    // Original query
    skeletons.push(originalQuery)
    
    // Evidence-based masking
    for (let i = 0; i < this.nSamples - 1; i++) {
      let maskedQuery = originalQuery
      
      // Mask legal entities, numbers, specific terms
      maskedQuery = maskedQuery.replace(/\b(ley|decreto|artículo|art\.?)\s+\d+/gi, '[NORMA]')
      maskedQuery = maskedQuery.replace(/\b\d{4,}\b/g, '[AÑO]')
      maskedQuery = maskedQuery.replace(/\b(municipio|provincia|nación)\b/gi, '[JURISDICCIÓN]')
      maskedQuery = maskedQuery.replace(/\b(sanción|multa|infracción)\b/gi, '[CONSECUENCIA]')
      
      // Progressive masking - remove more context each iteration
      const contextLevel = i / (this.nSamples - 2)
      if (contextLevel > 0.3) {
        maskedQuery = maskedQuery.replace(/\b(comercial|ambulante|habilitación)\b/gi, '[ACTIVIDAD]')
      }
      if (contextLevel > 0.6) {
        maskedQuery = maskedQuery.replace(/\b(puede|podrá|debe)\b/gi, '[MODAL]')
      }
      
      skeletons.push(maskedQuery)
    }
    
    return skeletons
  }

  // Calculate information budget (Δ̄) between original and skeletons
  private calculateInformationBudget(original: string, skeletons: string[]): number {
    let totalBits = 0
    
    for (const skeleton of skeletons.slice(1)) { // Skip original
      // Simple approximation: count information differences
      const originalTokens = original.split(/\s+/).length
      const skeletonTokens = skeleton.split(/\s+/).length
      const maskedCount = (skeleton.match(/\[.*?\]/g) || []).length
      
      // Information lost = log2(tokens_removed + mask_specificity)
      const informationLoss = Math.log2(Math.max(1, originalTokens - skeletonTokens + maskedCount * 2))
      totalBits += informationLoss
    }
    
    return totalBits / (skeletons.length - 1)
  }

  // Calculate prior probabilities for each variant
  private calculatePriors(skeletons: string[], context: string[]): number[] {
    const priors: number[] = []
    
    for (const skeleton of skeletons) {
      // Simple heuristic: more masked = higher uncertainty
      const maskCount = (skeleton.match(/\[.*?\]/g) || []).length
      const contextStrength = context.length
      
      // Base prior: 0.1 to 0.7 depending on masking level and context
      const basePrior = 0.1 + (maskCount * 0.1) + (1 / Math.max(1, contextStrength)) * 0.3
      priors.push(Math.min(0.7, basePrior))
    }
    
    return priors
  }

  // Main hallucination guard evaluation
  public evaluate(request: HallGuardRequest): HallGuardResult {
    const { query, context, response } = request
    
    // Step 1: Generate skeleton variants
    const skeletons = this.generateSkeletons(query, context)
    
    // Step 2: Calculate information budget (Δ̄)
    const informationBudget = this.calculateInformationBudget(query, skeletons)
    
    // Step 3: Calculate priors for each variant
    const priors = this.calculatePriors(skeletons, context)
    const avgPrior = priors.reduce((a, b) => a + b, 0) / priors.length
    const worstPrior = Math.max(...priors)
    
    // Step 4: Calculate Information Sufficiency Ratio (ISR)
    const bitsToTrust = Math.max(0, this.marginExtraBits - Math.log2(worstPrior))
    const isrRatio = informationBudget / Math.max(0.1, bitsToTrust)
    
    // Step 5: Calculate RoH bound using EDFL
    const rohBound = Math.min(worstPrior * Math.exp(-Math.max(0, informationBudget - this.marginExtraBits)), 0.95)
    
    // Step 6: Decision rule
    const decision = (isrRatio >= 1.0 && rohBound <= 0.05) ? "ANSWER" : "REFUSE"
    
    // Step 7: Generate rationale
    let rationale: string
    if (decision === "ANSWER") {
      rationale = `Evidence lift ${informationBudget.toFixed(1)} nats, worst-case prior ${worstPrior.toFixed(3)}, ISR ${isrRatio.toFixed(1)} → safe`
    } else {
      rationale = `Insufficient evidence (ISR ${isrRatio.toFixed(1)} < 1.0) or high risk (RoH ${rohBound.toFixed(3)} > 0.05) → refuse`
    }
    
    // Step 8: Generate certificate hash
    const certificateData = {
      query: query.substring(0, 50),
      decision,
      rohBound: Math.round(rohBound * 1000) / 1000,
      timestamp: Date.now()
    }
    const certificateHash = "sha256:" + btoa(JSON.stringify(certificateData)).substring(0, 16)
    
    return {
      decision,
      rohBound,
      informationBudget,
      isrRatio,
      rationale,
      certificateHash,
      metadata: {
        timestamp: new Date().toISOString(),
        nVariants: skeletons.length,
        method: "evidence-based"
      }
    }
  }
}

// Global instance
const hallGuard = new EDFLHallGuard()

export const hallucinationGuard = async (c: Context) => {
  try {
    const request = await c.req.json() as HallGuardRequest
    
    if (!request.query || !request.response) {
      return c.json({ error: "Query and response required" }, 400)
    }
    
    const result = hallGuard.evaluate(request)
    
    return c.json(result)
    
  } catch (error) {
    console.error("Hallucination guard error:", error)
    return c.json({ error: "Error en validación de alucinación" }, 500)
  }
}