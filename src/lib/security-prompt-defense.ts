// 🛡️ Security Prompt Defense System
// Protection against Prem Natarajan's Prompting Attacks Framework
// Integrated with Context Engineering for Legal AI Security

export interface SecurityThreatAssessment {
  threatLevel: 'low' | 'medium' | 'high' | 'critical';
  detectedAttacks: string[];
  confidenceScore: number;
  blockQuery: boolean;
  reasoning: string;
}

export interface SecurityRiskMetrics {
  injectionRisk: number;        // Prompt injection probability (0-1)
  roleAbuseRisk: number;        // Role consistency violation (0-1)  
  exfiltrationRisk: number;     // Data extraction attempt (0-1)
  chainedQueryRisk: number;     // Multi-query attack pattern (0-1)
  socialEngineeringRisk: number; // Persuasive/deceptive language (0-1)
  overallRisk: number;          // Combined risk score (0-1)
}

export class PromptInjectionDetector {
  
  private injectionPatterns = [
    // Direct instruction override
    /ignore\s+(all\s+)?(previous|above|earlier|prior)\s+(instructions?|prompts?|rules?)/i,
    /forget\s+(everything|all|your)\s+(instructions?|training|rules?)/i,
    /disregard\s+(your|all|previous)\s+(instructions?|guidelines|rules?)/i,
    
    // Role breaking attempts  
    /act\s+as\s+(if\s+you\s+are\s+)?(?:an?|the)?\s*(?:unrestricted|uncensored|jailbroken)/i,
    /pretend\s+(you\s+are|to\s+be)\s+(?:an?|the)?\s*(?:unrestricted|uncensored)/i,
    /roleplay\s+as\s+(?:an?|the)?\s*(?:unrestricted|uncensored|evil)/i,
    
    // System prompt extraction
    /(?:repeat|show|display|tell\s+me)\s+(?:your|the)\s+(?:system|initial|original)\s+(?:prompt|instructions?)/i,
    /what\s+(?:are|were)\s+your\s+(?:original|initial|system)\s+(?:instructions?|prompts?)/i,
    
    // Legal authority impersonation
    /i\s+am\s+(?:your|an?|the)\s+(?:lawyer|attorney|judge|legal\s+expert)/i,
    /as\s+(?:your|an?|the)\s+(?:legal\s+counsel|attorney|advocate)/i,
    
    // Ethical bypass attempts
    /for\s+(?:educational|research|academic)\s+purposes?\s+only/i,
    /this\s+is\s+(?:just\s+)?(?:a\s+)?(?:hypothetical|theoretical|fictional)/i,
    
    // Multi-language injection attempts
    /\u200b|\u200c|\u200d|\ufeff/g, // Zero-width characters
    /[\u0080-\u00FF]{3,}/g, // Extended ASCII injection attempts
  ];
  
  public detectInjection(query: string): {
    isInjection: boolean;
    confidence: number;
    patterns: string[];
  } {
    const detectedPatterns: string[] = [];
    let maxConfidence = 0;
    
    for (const pattern of this.injectionPatterns) {
      const match = query.match(pattern);
      if (match) {
        detectedPatterns.push(match[0]);
        maxConfidence = Math.max(maxConfidence, 0.8);
      }
    }
    
    // Check for instruction delimiter attacks
    const delimiterAttacks = [
      '---', '###', '```', '===', '***',
      'SYSTEM:', 'USER:', 'ASSISTANT:', 'HUMAN:',
      'IGNORE PREVIOUS', 'NEW INSTRUCTIONS:'
    ];
    
    for (const delimiter of delimiterAttacks) {
      if (query.toUpperCase().includes(delimiter)) {
        detectedPatterns.push(`Delimiter attack: ${delimiter}`);
        maxConfidence = Math.max(maxConfidence, 0.7);
      }
    }
    
    return {
      isInjection: detectedPatterns.length > 0,
      confidence: maxConfidence,
      patterns: detectedPatterns
    };
  }
}

export class RoleAbuseDetector {
  
  private legitimateLegalRoles = [
    'consulta legal', 'asesoría jurídica', 'información legal',
    'análisis normativo', 'revisión legal', 'compliance'
  ];
  
  private prohibitedRoles = [
    'abogado personal', 'representante legal', 'defensor',
    'asesor sin restricciones', 'experto ilimitado',
    'chatgpt', 'gpt-4', 'claude', 'otro modelo'
  ];
  
  public detectRoleAbuse(query: string): {
    isAbuse: boolean;
    confidence: number;
    attemptedRole: string | null;
  } {
    const lowerQuery = query.toLowerCase();
    
    // Check for prohibited role assumption
    for (const role of this.prohibitedRoles) {
      if (lowerQuery.includes(role)) {
        return {
          isAbuse: true,
          confidence: 0.9,
          attemptedRole: role
        };
      }
    }
    
    // Check for role override patterns
    const rolePatterns = [
      /you\s+are\s+now\s+(?:a|an|the)\s+([^.]+)/i,
      /act\s+as\s+(?:a|an|the)\s+([^.]+)/i,
      /pretend\s+(?:you\s+are|to\s+be)\s+(?:a|an|the)\s+([^.]+)/i,
      /from\s+now\s+on,?\s+you\s+are\s+(?:a|an|the)\s+([^.]+)/i
    ];
    
    for (const pattern of rolePatterns) {
      const match = lowerQuery.match(pattern);
      if (match) {
        const role = match[1]?.trim();
        // Check if it's a legitimate legal consultation role
        const isLegitimate = this.legitimateLegalRoles.some(legit => 
          role?.includes(legit)
        );
        
        if (!isLegitimate) {
          return {
            isAbuse: true,
            confidence: 0.8,
            attemptedRole: role || 'unknown'
          };
        }
      }
    }
    
    return {
      isAbuse: false,
      confidence: 0,
      attemptedRole: null
    };
  }
}

export class DataExfiltrationDetector {
  
  private exfiltrationPatterns = [
    // Direct data requests
    /(?:repeat|show|display|tell\s+me)\s+(?:exactly\s+)?(?:the\s+)?(?:full\s+)?(?:original\s+)?(?:text|content|data)/i,
    /(?:what\s+is|show\s+me)\s+(?:the\s+)?(?:exact\s+)?(?:full\s+)?(?:document|file|data|text)/i,
    
    // Memory probing
    /do\s+you\s+remember\s+(?:the\s+)?(?:previous|earlier|specific)\s+(?:conversation|document|data)/i,
    /what\s+(?:was|were)\s+(?:the\s+)?(?:previous|last|earlier)\s+(?:documents?|texts?|data)/i,
    
    // Training data extraction
    /(?:repeat|recite|quote)\s+(?:from\s+)?(?:your\s+)?(?:training|dataset|knowledge)/i,
    /what\s+(?:training\s+)?data\s+(?:do\s+you\s+have|were\s+you\s+trained\s+on)/i,
    
    // Corpus extraction attempts
    /list\s+all\s+(?:the\s+)?(?:legal\s+)?(?:documents?|cases?|laws?)/i,
    /show\s+me\s+(?:your\s+)?(?:complete\s+)?(?:legal\s+)?(?:database|corpus|collection)/i
  ];
  
  public detectExfiltration(query: string): {
    isExfiltration: boolean;
    confidence: number;
    patterns: string[];
  } {
    const detectedPatterns: string[] = [];
    let maxConfidence = 0;
    
    for (const pattern of this.exfiltrationPatterns) {
      const match = query.match(pattern);
      if (match) {
        detectedPatterns.push(match[0]);
        maxConfidence = Math.max(maxConfidence, 0.85);
      }
    }
    
    // Check for repetitive probing (sign of systematic extraction)
    const repetitiveWords = query.toLowerCase().split(' ');
    const wordCount = new Map<string, number>();
    
    repetitiveWords.forEach(word => {
      if (word.length > 3) {
        wordCount.set(word, (wordCount.get(word) || 0) + 1);
      }
    });
    
    for (const [word, count] of wordCount) {
      if (count >= 3 && ['document', 'data', 'text', 'information'].includes(word)) {
        detectedPatterns.push(`Repetitive probing: ${word} (${count}x)`);
        maxConfidence = Math.max(maxConfidence, 0.6);
      }
    }
    
    return {
      isExfiltration: detectedPatterns.length > 0,
      confidence: maxConfidence,
      patterns: detectedPatterns
    };
  }
}

export class SocialEngineeringDetector {
  
  private manipulativePatterns = [
    // Urgency tactics
    /(?:urgent|emergency|immediate|asap|quickly|right\s+away|time\s+sensitive)/i,
    
    // Authority claims
    /i\s+am\s+(?:a|an|the)\s+(?:lawyer|attorney|judge|legal\s+expert|professor)/i,
    /on\s+behalf\s+of\s+(?:my\s+client|the\s+court|legal\s+authority)/i,
    
    // Emotional manipulation
    /(?:please\s+)?(?:help\s+me|i\s+need|desperate|life\s+depends|critical\s+situation)/i,
    
    // False context
    /for\s+(?:my\s+)?(?:thesis|research|academic\s+work|university\s+project)/i,
    /(?:hypothetical|theoretical|fictional)\s+(?:scenario|case|situation)/i,
    
    // Compliance bypass
    /just\s+(?:this\s+once|between\s+us|don't\s+tell)/i,
    /no\s+one\s+will\s+(?:know|find\s+out|see\s+this)/i
  ];
  
  public detectSocialEngineering(query: string): {
    isSocialEngineering: boolean;
    confidence: number;
    tactics: string[];
  } {
    const detectedTactics: string[] = [];
    let maxConfidence = 0;
    
    for (const pattern of this.manipulativePatterns) {
      const match = query.match(pattern);
      if (match) {
        detectedTactics.push(match[0]);
        maxConfidence = Math.max(maxConfidence, 0.7);
      }
    }
    
    // Check for excessive persuasive language
    const persuasiveWords = [
      'please', 'help', 'need', 'important', 'critical', 'essential',
      'trust', 'secret', 'confidential', 'special', 'exception'
    ];
    
    const queryWords = query.toLowerCase().split(/\s+/);
    const persuasiveCount = queryWords.filter(word => 
      persuasiveWords.some(persuasive => word.includes(persuasive))
    ).length;
    
    if (persuasiveCount >= 3) {
      detectedTactics.push(`High persuasive language density: ${persuasiveCount} words`);
      maxConfidence = Math.max(maxConfidence, 0.6);
    }
    
    return {
      isSocialEngineering: detectedTactics.length > 0,
      confidence: maxConfidence,
      tactics: detectedTactics
    };
  }
}

export class ChainedQueryDetector {
  
  private sessionQueries: Map<string, Array<{query: string, timestamp: number}>> = new Map();
  
  public analyzeChainedQuery(
    query: string, 
    sessionId: string
  ): {
    isChainedAttack: boolean;
    confidence: number;
    pattern: string;
  } {
    
    // Get or create session history
    if (!this.sessionQueries.has(sessionId)) {
      this.sessionQueries.set(sessionId, []);
    }
    
    const sessionHistory = this.sessionQueries.get(sessionId)!;
    
    // Add current query
    sessionHistory.push({
      query: query.toLowerCase(),
      timestamp: Date.now()
    });
    
    // Keep only last 10 queries and recent ones (last hour)
    const oneHourAgo = Date.now() - (60 * 60 * 1000);
    const recentQueries = sessionHistory
      .filter(q => q.timestamp > oneHourAgo)
      .slice(-10);
    
    this.sessionQueries.set(sessionId, recentQueries);
    
    if (recentQueries.length < 3) {
      return {
        isChainedAttack: false,
        confidence: 0,
        pattern: 'insufficient data'
      };
    }
    
    // Analyze for suspicious patterns
    const suspiciousKeywords = [
      ['blanqueo', 'capitales', 'offshore'],
      ['evasion', 'impuestos', 'ocultar'],
      ['fraude', 'engaño', 'falsificacion'],
      ['corrupcion', 'soborno', 'coima'],
      ['lavado', 'dinero', 'activos']
    ];
    
    let keywordMatches = 0;
    let totalSuspiciousWords = 0;
    
    for (const keywordGroup of suspiciousKeywords) {
      const groupMatches = recentQueries.filter(q => 
        keywordGroup.some(keyword => q.query.includes(keyword))
      ).length;
      
      if (groupMatches >= 2) {
        keywordMatches++;
        totalSuspiciousWords += groupMatches;
      }
    }
    
    // Check for escalating specificity pattern
    const queryLengths = recentQueries.map(q => q.query.length);
    const isEscalating = queryLengths.every((length, i) => 
      i === 0 || length >= queryLengths[i - 1]
    );
    
    let confidence = 0;
    let pattern = '';
    
    if (keywordMatches >= 2) {
      confidence = Math.min(0.9, keywordMatches * 0.3);
      pattern = `Suspicious keyword progression: ${keywordMatches} groups, ${totalSuspiciousWords} matches`;
    } else if (isEscalating && queryLengths.length >= 4) {
      confidence = 0.6;
      pattern = `Escalating query complexity pattern detected`;
    }
    
    return {
      isChainedAttack: confidence > 0.5,
      confidence,
      pattern
    };
  }
  
  public clearSession(sessionId: string): void {
    this.sessionQueries.delete(sessionId);
  }
}

// =============================================================================
// 🛡️ MASTER SECURITY SYSTEM
// =============================================================================

export class ContextEngineeringSecurity {
  
  private injectionDetector = new PromptInjectionDetector();
  private roleAbuseDetector = new RoleAbuseDetector();
  private exfiltrationDetector = new DataExfiltrationDetector();
  private socialEngineeringDetector = new SocialEngineeringDetector();
  private chainedQueryDetector = new ChainedQueryDetector();
  
  public assessSecurityThreat(
    query: string,
    sessionId: string = 'default'
  ): SecurityThreatAssessment {
    
    const detectedAttacks: string[] = [];
    let maxThreatLevel: 'low' | 'medium' | 'high' | 'critical' = 'low';
    let totalConfidence = 0;
    let confidenceCount = 0;
    
    // 1. Prompt Injection Detection
    const injection = this.injectionDetector.detectInjection(query);
    if (injection.isInjection) {
      detectedAttacks.push(`Prompt Injection (${injection.confidence.toFixed(2)})`);
      maxThreatLevel = this.escalateThreatLevel(maxThreatLevel, 'critical');
      totalConfidence += injection.confidence;
      confidenceCount++;
    }
    
    // 2. Role Abuse Detection
    const roleAbuse = this.roleAbuseDetector.detectRoleAbuse(query);
    if (roleAbuse.isAbuse) {
      detectedAttacks.push(`Role Abuse: ${roleAbuse.attemptedRole} (${roleAbuse.confidence.toFixed(2)})`);
      maxThreatLevel = this.escalateThreatLevel(maxThreatLevel, 'high');
      totalConfidence += roleAbuse.confidence;
      confidenceCount++;
    }
    
    // 3. Data Exfiltration Detection
    const exfiltration = this.exfiltrationDetector.detectExfiltration(query);
    if (exfiltration.isExfiltration) {
      detectedAttacks.push(`Data Exfiltration (${exfiltration.confidence.toFixed(2)})`);
      maxThreatLevel = this.escalateThreatLevel(maxThreatLevel, 'critical');
      totalConfidence += exfiltration.confidence;
      confidenceCount++;
    }
    
    // 4. Social Engineering Detection
    const socialEng = this.socialEngineeringDetector.detectSocialEngineering(query);
    if (socialEng.isSocialEngineering) {
      detectedAttacks.push(`Social Engineering (${socialEng.confidence.toFixed(2)})`);
      maxThreatLevel = this.escalateThreatLevel(maxThreatLevel, 'medium');
      totalConfidence += socialEng.confidence;
      confidenceCount++;
    }
    
    // 5. Chained Query Detection
    const chained = this.chainedQueryDetector.analyzeChainedQuery(query, sessionId);
    if (chained.isChainedAttack) {
      detectedAttacks.push(`Chained Attack: ${chained.pattern} (${chained.confidence.toFixed(2)})`);
      maxThreatLevel = this.escalateThreatLevel(maxThreatLevel, 'high');
      totalConfidence += chained.confidence;
      confidenceCount++;
    }
    
    // Calculate overall confidence
    const overallConfidence = confidenceCount > 0 ? totalConfidence / confidenceCount : 0;
    
    // Determine if query should be blocked
    const blockQuery = maxThreatLevel === 'critical' || 
                      (maxThreatLevel === 'high' && overallConfidence > 0.7) ||
                      detectedAttacks.length >= 3;
    
    // Generate reasoning
    const reasoning = detectedAttacks.length > 0
      ? `Security threats detected: ${detectedAttacks.join(', ')}`
      : 'No security threats detected - query appears safe for legal AI processing';
    
    return {
      threatLevel: maxThreatLevel,
      detectedAttacks,
      confidenceScore: overallConfidence,
      blockQuery,
      reasoning
    };
  }
  
  public calculateSecurityRiskMetrics(
    query: string,
    sessionId: string = 'default'
  ): SecurityRiskMetrics {
    
    const injection = this.injectionDetector.detectInjection(query);
    const roleAbuse = this.roleAbuseDetector.detectRoleAbuse(query);
    const exfiltration = this.exfiltrationDetector.detectExfiltration(query);
    const socialEng = this.socialEngineeringDetector.detectSocialEngineering(query);
    const chained = this.chainedQueryDetector.analyzeChainedQuery(query, sessionId);
    
    const injectionRisk = injection.isInjection ? injection.confidence : 0;
    const roleAbuseRisk = roleAbuse.isAbuse ? roleAbuse.confidence : 0;
    const exfiltrationRisk = exfiltration.isExfiltration ? exfiltration.confidence : 0;
    const socialEngineeringRisk = socialEng.isSocialEngineering ? socialEng.confidence : 0;
    const chainedQueryRisk = chained.isChainedAttack ? chained.confidence : 0;
    
    const overallRisk = Math.max(
      injectionRisk,
      roleAbuseRisk, 
      exfiltrationRisk,
      Math.min(0.8, (socialEngineeringRisk + chainedQueryRisk) / 2)
    );
    
    return {
      injectionRisk,
      roleAbuseRisk,
      exfiltrationRisk,
      chainedQueryRisk,
      socialEngineeringRisk,
      overallRisk
    };
  }
  
  private escalateThreatLevel(
    current: 'low' | 'medium' | 'high' | 'critical',
    new_level: 'low' | 'medium' | 'high' | 'critical'
  ): 'low' | 'medium' | 'high' | 'critical' {
    const levels = { low: 1, medium: 2, high: 3, critical: 4 };
    return levels[new_level] > levels[current] ? new_level : current;
  }
}

// Export singleton instance
export const contextEngineeringSecurity = new ContextEngineeringSecurity();