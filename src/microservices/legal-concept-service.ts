/**
 * SCM Legal - Legal Concept Microservice
 * Distributed architecture inspired by System Design Primer patterns
 */

import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { logger } from 'hono/logger';
import { JurisdictionManager, defaultJurisdictionConfig } from '../core/jurisdiction/manager';
import type { LegalContextRequest, LegalContextResponse, LegalConcept } from '../core/jurisdiction/types';

// Circuit breaker pattern for resilience
class CircuitBreaker {
  private failures: number = 0;
  private nextAttempt: number = Date.now();
  private state: 'closed' | 'open' | 'half-open' = 'closed';
  
  constructor(
    private maxFailures: number = 5,
    private timeout: number = 60000 // 60 seconds
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

// Rate limiter for API protection
class RateLimiter {
  private requests: Map<string, number[]> = new Map();

  constructor(
    private maxRequests: number = 100,
    private windowMs: number = 60000 // 1 minute
  ) {}

  isAllowed(clientId: string): boolean {
    const now = Date.now();
    const windowStart = now - this.windowMs;

    if (!this.requests.has(clientId)) {
      this.requests.set(clientId, []);
    }

    const clientRequests = this.requests.get(clientId)!;
    
    // Remove old requests outside the window
    const validRequests = clientRequests.filter(timestamp => timestamp > windowStart);
    
    if (validRequests.length >= this.maxRequests) {
      return false;
    }

    validRequests.push(now);
    this.requests.set(clientId, validRequests);
    return true;
  }
}

// Cache layer for performance optimization
class ConceptCache {
  private cache: Map<string, { data: any; expiry: number }> = new Map();
  private ttl: number = 300000; // 5 minutes

  get(key: string): any | null {
    const entry = this.cache.get(key);
    if (!entry) return null;
    
    if (Date.now() > entry.expiry) {
      this.cache.delete(key);
      return null;
    }
    
    return entry.data;
  }

  set(key: string, data: any): void {
    this.cache.set(key, {
      data,
      expiry: Date.now() + this.ttl
    });
  }

  clear(): void {
    this.cache.clear();
  }
}

// Health check utilities
class HealthChecker {
  private services: Map<string, () => Promise<boolean>> = new Map();

  registerService(name: string, healthCheck: () => Promise<boolean>): void {
    this.services.set(name, healthCheck);
  }

  async checkAll(): Promise<{ status: string; services: Record<string, boolean> }> {
    const results: Record<string, boolean> = {};
    let allHealthy = true;

    for (const [name, check] of this.services) {
      try {
        results[name] = await check();
        if (!results[name]) allHealthy = false;
      } catch (error) {
        results[name] = false;
        allHealthy = false;
      }
    }

    return {
      status: allHealthy ? 'healthy' : 'degraded',
      services: results
    };
  }
}

// Main Legal Concept Service
export class LegalConceptService {
  private app: Hono;
  private jurisdictionManager: JurisdictionManager;
  private circuitBreaker: CircuitBreaker;
  private rateLimiter: RateLimiter;
  private cache: ConceptCache;
  private healthChecker: HealthChecker;

  constructor() {
    this.app = new Hono();
    this.jurisdictionManager = new JurisdictionManager(defaultJurisdictionConfig);
    this.circuitBreaker = new CircuitBreaker();
    this.rateLimiter = new RateLimiter();
    this.cache = new ConceptCache();
    this.healthChecker = new HealthChecker();

    this.setupMiddleware();
    this.setupRoutes();
    this.setupHealthChecks();
  }

  private setupMiddleware(): void {
    // CORS for cross-origin requests
    this.app.use('/api/*', cors({
      origin: ['https://scm-legal.pages.dev', 'http://localhost:3000'],
      allowMethods: ['GET', 'POST', 'PUT', 'DELETE'],
      allowHeaders: ['Content-Type', 'Authorization', 'X-Jurisdiction']
    }));

    // Request logging
    this.app.use('/api/*', logger());

    // Rate limiting middleware
    this.app.use('/api/*', async (c, next) => {
      const clientId = c.req.header('x-client-id') || c.req.header('x-forwarded-for') || 'anonymous';
      
      if (!this.rateLimiter.isAllowed(clientId)) {
        return c.json({ error: 'Rate limit exceeded' }, 429);
      }
      
      await next();
    });

    // Error handling middleware
    this.app.onError((error, c) => {
      console.error('Service error:', error);
      return c.json({ 
        error: 'Internal service error',
        requestId: c.req.header('x-request-id') || 'unknown'
      }, 500);
    });
  }

  private setupRoutes(): void {
    // Legal concept analysis endpoint
    this.app.post('/api/legal/analyze', async (c) => {
      try {
        const request: LegalContextRequest = await c.req.json();
        
        // Input validation
        if (!request.query || !request.jurisdiction) {
          return c.json({ error: 'Query and jurisdiction are required' }, 400);
        }

        // Cache check
        const cacheKey = `analyze:${JSON.stringify(request)}`;
        const cached = this.cache.get(cacheKey);
        if (cached) {
          return c.json({
            ...cached,
            metadata: { ...cached.metadata, cached: true }
          });
        }

        // Process with circuit breaker protection
        const response = await this.circuitBreaker.call(async () => {
          return await this.jurisdictionManager.processLegalContext(request);
        });

        // Cache the response
        this.cache.set(cacheKey, response);

        return c.json(response);

      } catch (error) {
        console.error('Analysis error:', error);
        return c.json({ 
          error: error.message || 'Analysis failed',
          requestId: c.req.header('x-request-id')
        }, 500);
      }
    });

    // Jurisdiction management endpoints
    this.app.get('/api/jurisdictions', (c) => {
      const jurisdictions = this.jurisdictionManager.getEnabledJurisdictions();
      return c.json({ jurisdictions });
    });

    this.app.get('/api/jurisdictions/:code', (c) => {
      const code = c.req.param('code');
      try {
        const jurisdiction = this.jurisdictionManager.getJurisdiction(code);
        return c.json({ jurisdiction });
      } catch (error) {
        return c.json({ error: 'Jurisdiction not found' }, 404);
      }
    });

    // Service management endpoints
    this.app.post('/api/admin/cache/clear', async (c) => {
      // Authentication would be required in production
      this.cache.clear();
      return c.json({ message: 'Cache cleared successfully' });
    });

    this.app.get('/api/admin/circuit-breaker/status', (c) => {
      return c.json({
        state: (this.circuitBreaker as any).state,
        failures: (this.circuitBreaker as any).failures
      });
    });
  }

  private setupHealthChecks(): void {
    // Register health checks for different components
    this.healthChecker.registerService('jurisdiction-manager', async () => {
      try {
        const jurisdictions = this.jurisdictionManager.getEnabledJurisdictions();
        return jurisdictions.length > 0;
      } catch {
        return false;
      }
    });

    this.healthChecker.registerService('cache', async () => {
      try {
        this.cache.set('health-check', 'ok');
        const result = this.cache.get('health-check');
        return result === 'ok';
      } catch {
        return false;
      }
    });

    // Health check endpoint
    this.app.get('/health', async (c) => {
      const health = await this.healthChecker.checkAll();
      return c.json(health, health.status === 'healthy' ? 200 : 503);
    });

    // Readiness probe for Kubernetes
    this.app.get('/ready', (c) => {
      return c.json({ status: 'ready', timestamp: new Date().toISOString() });
    });

    // Liveness probe for Kubernetes
    this.app.get('/live', (c) => {
      return c.json({ status: 'alive', timestamp: new Date().toISOString() });
    });
  }

  getApp(): Hono {
    return this.app;
  }

  // Graceful shutdown handler
  async shutdown(): Promise<void> {
    console.log('Shutting down Legal Concept Service gracefully...');
    this.cache.clear();
    // Add any other cleanup operations here
  }
}

// Metrics and monitoring
class ServiceMetrics {
  private metrics: Map<string, number> = new Map();

  increment(metric: string, value: number = 1): void {
    const current = this.metrics.get(metric) || 0;
    this.metrics.set(metric, current + value);
  }

  get(metric: string): number {
    return this.metrics.get(metric) || 0;
  }

  getAll(): Record<string, number> {
    return Object.fromEntries(this.metrics);
  }

  reset(): void {
    this.metrics.clear();
  }
}

// Export for use in main application
export const metrics = new ServiceMetrics();