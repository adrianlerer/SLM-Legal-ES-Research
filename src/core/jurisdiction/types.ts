/**
 * SCM Legal - Multi-Jurisdictional Type Definitions
 * Inspired by Tolgee's localization architecture for legal domain
 */

export interface LegalJurisdiction {
  code: 'AR' | 'ES' | 'CL' | 'UY';
  name: string;
  language: string;
  legalSystem: 'civil' | 'common';
  timezone: string;
  currency: string;
  enabled: boolean;
}

export interface JurisdictionConfig {
  jurisdictions: LegalJurisdiction[];
  fallbackJurisdiction: 'AR';
  contextualLegalAnalysis: boolean;
  aiLegalProviders: ['scm-legal', 'openai', 'anthropic'];
  complianceRequirements: {
    dataProtection: string[];
    legalDocumentRetention: number;
    auditTrailRequired: boolean;
  };
}

export interface LegalConcept {
  id: string;
  conceptKey: string;
  jurisdiction: LegalJurisdiction['code'];
  category: 'corporativo' | 'civil' | 'penal' | 'laboral' | 'tributario' | 'administrativo';
  content: {
    definition: string;
    scope: string;
    applications: string[];
    precedents: LegalPrecedent[];
    relatedConcepts: string[];
  };
  metadata: {
    confidence: number;
    lastUpdated: Date;
    reviewStatus: 'draft' | 'reviewed' | 'approved';
    expertValidation: boolean;
  };
}

export interface LegalPrecedent {
  caseId: string;
  court: string;
  date: Date;
  summary: string;
  jurisdiction: LegalJurisdiction['code'];
  relevanceScore: number;
}

export interface CrossJurisdictionalMapping {
  conceptKey: string;
  mappings: {
    [jurisdiction: string]: {
      localConceptKey: string;
      equivalenceLevel: 'exact' | 'similar' | 'partial' | 'none';
      differences: string[];
      notes: string;
    };
  };
}

export interface LegalContextRequest {
  query: string;
  jurisdiction: LegalJurisdiction['code'];
  category?: LegalConcept['category'];
  includeComparative?: boolean;
  confidenceThreshold?: number;
}

export interface LegalContextResponse {
  concepts: LegalConcept[];
  crossJurisdictionalComparison?: CrossJurisdictionalMapping[];
  recommendations: {
    applicableLaw: string;
    complianceChecks: string[];
    riskFactors: string[];
  };
  metadata: {
    processingTime: number;
    modelsUsed: string[];
    confidence: number;
  };
}

export interface AuditEntry {
  id: string;
  timestamp: Date;
  userId: string;
  action: 'query' | 'concept_edit' | 'validation' | 'export';
  jurisdiction: LegalJurisdiction['code'];
  details: {
    query?: string;
    conceptsAccessed: string[];
    modificationsApplied?: any;
  };
  ipAddress: string;
  userAgent: string;
}

export interface ComplianceReport {
  jurisdiction: LegalJurisdiction['code'];
  period: { start: Date; end: Date };
  metrics: {
    totalQueries: number;
    conceptsValidated: number;
    expertReviews: number;
    accuracyScore: number;
  };
  dataProtectionCompliance: {
    gdprCompliant: boolean;
    dataRetentionPolicy: string;
    userConsentManagement: boolean;
  };
  auditTrail: AuditEntry[];
}