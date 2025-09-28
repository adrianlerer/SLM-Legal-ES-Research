/**
 * SCM Legal - Legal Data Sources Integration Framework
 * Inspired by Public APIs repository patterns for comprehensive data integration
 */

// Base API client interface following REST patterns
interface APIClient {
  name: string;
  baseUrl: string;
  version: string;
  authentication: AuthenticationMethod;
  rateLimit: RateLimit;
  healthCheck(): Promise<boolean>;
  request<T>(endpoint: string, options?: RequestOptions): Promise<APIResponse<T>>;
}

interface AuthenticationMethod {
  type: 'api-key' | 'oauth2' | 'bearer' | 'basic' | 'none';
  headers?: Record<string, string>;
  queryParams?: Record<string, string>;
  refreshToken?: () => Promise<string>;
}

interface RateLimit {
  requests: number;
  period: number; // milliseconds
  retryAfter?: number;
}

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  headers?: Record<string, string>;
  body?: any;
  timeout?: number;
  retries?: number;
}

interface APIResponse<T> {
  data: T;
  status: number;
  headers: Record<string, string>;
  pagination?: PaginationInfo;
  metadata?: {
    requestId: string;
    timestamp: Date;
    source: string;
  };
}

interface PaginationInfo {
  page: number;
  limit: number;
  total: number;
  hasNext: boolean;
  hasPrev: boolean;
}

// Legal data source configurations following Public APIs categorization
export const LEGAL_DATA_SOURCES = {
  // Government and Official Legal Sources
  ARGENTINA: {
    INFOLEG: {
      name: 'InfoLEG - Sistema Argentino de Información Jurídica',
      baseUrl: 'http://servicios.infoleg.gob.ar/infolegInternet/anexos',
      category: 'government',
      jurisdiction: 'AR',
      dataTypes: ['laws', 'decrees', 'resolutions'],
      authentication: { type: 'none' as const },
      rateLimit: { requests: 100, period: 60000 },
      endpoints: {
        searchLaws: '/normativas/search',
        getLaw: '/normativas/{id}',
        getDecrees: '/decretos/search'
      }
    },
    CSJN: {
      name: 'Corte Suprema de Justicia de la Nación',
      baseUrl: 'https://sjconsulta.csjn.gov.ar/sjconsulta/documentos',
      category: 'jurisprudence',
      jurisdiction: 'AR',
      dataTypes: ['court-decisions', 'jurisprudence'],
      authentication: { type: 'none' as const },
      rateLimit: { requests: 50, period: 60000 }
    }
  },
  SPAIN: {
    BOE: {
      name: 'Boletín Oficial del Estado',
      baseUrl: 'https://www.boe.es/datosabiertos/api',
      category: 'government',
      jurisdiction: 'ES',
      dataTypes: ['laws', 'royal-decrees', 'orders'],
      authentication: { type: 'api-key' as const },
      rateLimit: { requests: 200, period: 60000 },
      endpoints: {
        searchDocuments: '/buscar/doc',
        getDocument: '/documento/{id}',
        getDailyBulletin: '/diario_boe/fecha/{date}'
      }
    },
    CENDOJ: {
      name: 'Centro de Documentación Judicial',
      baseUrl: 'https://www.poderjudicial.es/search/openDocument',
      category: 'jurisprudence',
      jurisdiction: 'ES',
      dataTypes: ['court-decisions', 'jurisprudence'],
      authentication: { type: 'none' as const },
      rateLimit: { requests: 100, period: 60000 }
    }
  },
  CHILE: {
    LEYCHILE: {
      name: 'Ley Chile - Biblioteca del Congreso Nacional',
      baseUrl: 'https://www.leychile.cl/Consulta/api',
      category: 'government',
      jurisdiction: 'CL',
      dataTypes: ['laws', 'constitution', 'codes'],
      authentication: { type: 'api-key' as const },
      rateLimit: { requests: 150, period: 60000 },
      endpoints: {
        searchLaws: '/listado_normas',
        getLaw: '/norma/{id}',
        getConstitution: '/constitucion'
      }
    },
    PJUD: {
      name: 'Poder Judicial de Chile',
      baseUrl: 'https://oficinajudicial.pjud.cl/api',
      category: 'jurisprudence',
      jurisdiction: 'CL',
      dataTypes: ['court-decisions'],
      authentication: { type: 'bearer' as const },
      rateLimit: { requests: 75, period: 60000 }
    }
  },
  URUGUAY: {
    IMPO: {
      name: 'IMPO - Registro Nacional de Leyes y Decretos',
      baseUrl: 'https://www.impo.com.uy/api',
      category: 'government',
      jurisdiction: 'UY',
      dataTypes: ['laws', 'decrees', 'constitution'],
      authentication: { type: 'none' as const },
      rateLimit: { requests: 100, period: 60000 },
      endpoints: {
        searchNorms: '/normativa/buscar',
        getNorm: '/normativa/{id}',
        getConstitution: '/constitucion'
      }
    }
  },
  // International and Comparative Sources
  INTERNATIONAL: {
    UN_TREATY_COLLECTION: {
      name: 'UN Treaty Collection',
      baseUrl: 'https://treaties.un.org/api',
      category: 'international',
      jurisdiction: 'INTL',
      dataTypes: ['treaties', 'conventions'],
      authentication: { type: 'api-key' as const },
      rateLimit: { requests: 50, period: 60000 }
    },
    WORLD_BANK_LAW: {
      name: 'World Bank Law Library',
      baseUrl: 'https://openknowledge.worldbank.org/server/api',
      category: 'international',
      jurisdiction: 'INTL',
      dataTypes: ['legal-analysis', 'comparative-law'],
      authentication: { type: 'none' as const },
      rateLimit: { requests: 100, period: 60000 }
    }
  },
  // Commercial Legal Databases (with API access)
  COMMERCIAL: {
    WESTLAW: {
      name: 'Westlaw API',
      baseUrl: 'https://api.westlaw.com/v1',
      category: 'commercial',
      jurisdiction: 'MULTI',
      dataTypes: ['case-law', 'statutes', 'legal-analysis'],
      authentication: { type: 'oauth2' as const },
      rateLimit: { requests: 1000, period: 60000 },
      pricing: 'subscription'
    },
    LEXIS_NEXIS: {
      name: 'LexisNexis API',
      baseUrl: 'https://services-api.lexisnexis.com/v1',
      category: 'commercial',
      jurisdiction: 'MULTI',
      dataTypes: ['case-law', 'news', 'legal-analysis'],
      authentication: { type: 'oauth2' as const },
      rateLimit: { requests: 500, period: 60000 },
      pricing: 'usage-based'
    }
  }
};

// Generic API client implementation
export class LegalAPIClient implements APIClient {
  name: string;
  baseUrl: string;
  version: string;
  authentication: AuthenticationMethod;
  rateLimit: RateLimit;
  
  private requestCount: number = 0;
  private lastResetTime: number = Date.now();

  constructor(config: any) {
    this.name = config.name;
    this.baseUrl = config.baseUrl;
    this.version = config.version || 'v1';
    this.authentication = config.authentication;
    this.rateLimit = config.rateLimit;
  }

  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        timeout: 5000
      });
      return response.ok;
    } catch {
      // If no health endpoint, try a basic request
      try {
        const response = await fetch(this.baseUrl, { 
          method: 'HEAD',
          timeout: 5000 
        });
        return response.ok || response.status === 405; // 405 Method Not Allowed is acceptable
      } catch {
        return false;
      }
    }
  }

  async request<T>(endpoint: string, options: RequestOptions = {}): Promise<APIResponse<T>> {
    // Rate limiting check
    await this.enforceRateLimit();

    const url = `${this.baseUrl}${endpoint}`;
    const headers = await this.buildHeaders(options.headers);
    
    const requestConfig: RequestInit = {
      method: options.method || 'GET',
      headers,
      body: options.body ? JSON.stringify(options.body) : undefined,
      signal: AbortSignal.timeout(options.timeout || 30000)
    };

    const requestId = `req_${Date.now()}_${Math.random().toString(36).substring(2)}`;

    try {
      const response = await fetch(url, requestConfig);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      return {
        data,
        status: response.status,
        headers: Object.fromEntries(response.headers.entries()),
        metadata: {
          requestId,
          timestamp: new Date(),
          source: this.name
        }
      };

    } catch (error) {
      console.error(`API request failed for ${this.name}:`, error);
      throw new Error(`Request to ${this.name} failed: ${error.message}`);
    }
  }

  private async enforceRateLimit(): Promise<void> {
    const now = Date.now();
    
    // Reset counter if window has passed
    if (now - this.lastResetTime >= this.rateLimit.period) {
      this.requestCount = 0;
      this.lastResetTime = now;
    }

    // Check if rate limit exceeded
    if (this.requestCount >= this.rateLimit.requests) {
      const waitTime = this.rateLimit.period - (now - this.lastResetTime);
      console.log(`Rate limit exceeded for ${this.name}, waiting ${waitTime}ms`);
      await new Promise(resolve => setTimeout(resolve, waitTime));
      
      // Reset after waiting
      this.requestCount = 0;
      this.lastResetTime = Date.now();
    }

    this.requestCount++;
  }

  private async buildHeaders(customHeaders: Record<string, string> = {}): Promise<Record<string, string>> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'User-Agent': 'SCM-Legal-v1.0',
      ...customHeaders
    };

    // Add authentication headers
    switch (this.authentication.type) {
      case 'api-key':
        Object.assign(headers, this.authentication.headers || {});
        break;
      case 'bearer':
        if (this.authentication.refreshToken) {
          const token = await this.authentication.refreshToken();
          headers['Authorization'] = `Bearer ${token}`;
        }
        break;
      case 'oauth2':
        if (this.authentication.refreshToken) {
          const token = await this.authentication.refreshToken();
          headers['Authorization'] = `Bearer ${token}`;
        }
        break;
      case 'basic':
        if (this.authentication.headers?.Authorization) {
          headers['Authorization'] = this.authentication.headers.Authorization;
        }
        break;
    }

    return headers;
  }
}

// Data source manager for coordinating multiple APIs
export class LegalDataSourceManager {
  private clients: Map<string, LegalAPIClient> = new Map();
  private circuitBreakers: Map<string, CircuitBreaker> = new Map();

  constructor() {
    this.initializeClients();
  }

  private initializeClients(): void {
    // Initialize clients for all configured data sources
    Object.values(LEGAL_DATA_SOURCES).forEach(jurisdiction => {
      Object.values(jurisdiction).forEach(source => {
        const client = new LegalAPIClient(source);
        const key = `${source.jurisdiction}-${source.name}`;
        this.clients.set(key, client);
        this.circuitBreakers.set(key, new CircuitBreaker());
      });
    });
  }

  async searchLegalContent(
    query: string, 
    jurisdiction: string, 
    dataTypes: string[] = [],
    options: SearchOptions = {}
  ): Promise<LegalSearchResults> {
    const results: LegalSearchResults = {
      query,
      jurisdiction,
      results: [],
      sources: [],
      metadata: {
        totalSources: 0,
        successfulSources: 0,
        failedSources: 0,
        searchTime: 0
      }
    };

    const startTime = Date.now();
    const relevantClients = this.getRelevantClients(jurisdiction, dataTypes);
    
    // Search all relevant sources in parallel
    const searchPromises = relevantClients.map(async ({ key, client }) => {
      const circuitBreaker = this.circuitBreakers.get(key)!;
      
      try {
        return await circuitBreaker.call(async () => {
          const searchResult = await this.searchInSource(client, query, options);
          results.sources.push({
            name: client.name,
            status: 'success',
            resultCount: searchResult.length
          });
          return searchResult;
        });
      } catch (error) {
        console.error(`Search failed in ${client.name}:`, error);
        results.sources.push({
          name: client.name,
          status: 'failed',
          error: error.message,
          resultCount: 0
        });
        return [];
      }
    });

    const searchResults = await Promise.allSettled(searchPromises);
    
    // Aggregate results
    searchResults.forEach((result) => {
      if (result.status === 'fulfilled') {
        results.results.push(...result.value);
        results.metadata.successfulSources++;
      } else {
        results.metadata.failedSources++;
      }
    });

    results.metadata.totalSources = relevantClients.length;
    results.metadata.searchTime = Date.now() - startTime;

    // Sort results by relevance score
    results.results.sort((a, b) => (b.relevanceScore || 0) - (a.relevanceScore || 0));

    return results;
  }

  private getRelevantClients(jurisdiction: string, dataTypes: string[]): Array<{ key: string; client: LegalAPIClient }> {
    const relevant: Array<{ key: string; client: LegalAPIClient }> = [];
    
    this.clients.forEach((client, key) => {
      const [clientJurisdiction] = key.split('-');
      
      // Include if jurisdiction matches or is international
      const jurisdictionMatch = clientJurisdiction === jurisdiction || 
                              clientJurisdiction === 'INTL' ||
                              jurisdiction === 'ALL';
      
      if (jurisdictionMatch) {
        relevant.push({ key, client });
      }
    });

    return relevant;
  }

  private async searchInSource(client: LegalAPIClient, query: string, options: SearchOptions): Promise<LegalDocument[]> {
    // This would be implemented based on each source's specific API
    // For now, return placeholder structure
    const response = await client.request<any[]>('/search', {
      method: 'POST',
      body: { query, ...options }
    });

    return response.data.map(item => ({
      id: item.id || `doc_${Math.random().toString(36)}`,
      title: item.title || item.name || 'Untitled',
      content: item.content || item.description || '',
      source: client.name,
      jurisdiction: options.jurisdiction || 'unknown',
      documentType: item.type || 'unknown',
      date: new Date(item.date || Date.now()),
      url: item.url || '',
      relevanceScore: item.score || Math.random(),
      metadata: {
        classification: item.classification || 'unclassified',
        authority: item.authority || 'unknown',
        tags: item.tags || []
      }
    }));
  }

  async getSourceHealth(): Promise<SourceHealthReport> {
    const healthChecks = await Promise.allSettled(
      Array.from(this.clients.entries()).map(async ([key, client]) => {
        const isHealthy = await client.healthCheck();
        const circuitBreaker = this.circuitBreakers.get(key)!;
        
        return {
          name: client.name,
          key,
          healthy: isHealthy,
          circuitBreakerState: (circuitBreaker as any).state || 'closed',
          lastCheck: new Date()
        };
      })
    );

    const sources = healthChecks.map(result => 
      result.status === 'fulfilled' ? result.value : {
        name: 'unknown',
        key: 'unknown',
        healthy: false,
        circuitBreakerState: 'open',
        lastCheck: new Date(),
        error: result.reason?.message
      }
    );

    return {
      totalSources: sources.length,
      healthySources: sources.filter(s => s.healthy).length,
      unhealthySources: sources.filter(s => !s.healthy).length,
      sources,
      timestamp: new Date()
    };
  }
}

// Type definitions for search functionality
interface SearchOptions {
  jurisdiction?: string;
  dateFrom?: Date;
  dateTo?: Date;
  documentTypes?: string[];
  limit?: number;
  offset?: number;
  sortBy?: 'relevance' | 'date' | 'title';
  sortOrder?: 'asc' | 'desc';
}

interface LegalDocument {
  id: string;
  title: string;
  content: string;
  source: string;
  jurisdiction: string;
  documentType: string;
  date: Date;
  url: string;
  relevanceScore?: number;
  metadata: {
    classification: string;
    authority: string;
    tags: string[];
  };
}

interface LegalSearchResults {
  query: string;
  jurisdiction: string;
  results: LegalDocument[];
  sources: Array<{
    name: string;
    status: 'success' | 'failed';
    resultCount: number;
    error?: string;
  }>;
  metadata: {
    totalSources: number;
    successfulSources: number;
    failedSources: number;
    searchTime: number;
  };
}

interface SourceHealthReport {
  totalSources: number;
  healthySources: number;
  unhealthySources: number;
  sources: Array<{
    name: string;
    key: string;
    healthy: boolean;
    circuitBreakerState: string;
    lastCheck: Date;
    error?: string;
  }>;
  timestamp: Date;
}

// Simple circuit breaker implementation
class CircuitBreaker {
  private failures: number = 0;
  private nextAttempt: number = Date.now();
  private state: 'closed' | 'open' | 'half-open' = 'closed';
  
  constructor(
    private maxFailures: number = 3,
    private timeout: number = 30000
  ) {}

  async call<T>(operation: () => Promise<T>): Promise<T> {
    if (this.state === 'open') {
      if (Date.now() < this.nextAttempt) {
        throw new Error('Circuit breaker is OPEN');
      }
      this.state = 'half-open';
    }

    try {
      const result = await operation();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  private onSuccess(): void {
    this.failures = 0;
    this.state = 'closed';
  }

  private onFailure(): void {
    this.failures++;
    if (this.failures >= this.maxFailures) {
      this.state = 'open';
      this.nextAttempt = Date.now() + this.timeout;
    }
  }
}