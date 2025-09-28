/**
 * SCM Legal - API Gateway with Load Balancing
 * Distributed system patterns from System Design Primer
 */

import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { logger } from 'hono/logger';
import { jwt } from 'hono/jwt';

// Service discovery and registry
class ServiceRegistry {
  private services: Map<string, ServiceInstance[]> = new Map();
  private healthChecks: Map<string, NodeJS.Timeout> = new Map();

  registerService(serviceName: string, instance: ServiceInstance): void {
    if (!this.services.has(serviceName)) {
      this.services.set(serviceName, []);
    }

    const instances = this.services.get(serviceName)!;
    
    // Remove existing instance with same id if it exists
    const existingIndex = instances.findIndex(i => i.id === instance.id);
    if (existingIndex !== -1) {
      instances.splice(existingIndex, 1);
    }

    instances.push(instance);
    this.startHealthCheck(serviceName, instance);
    
    console.log(`Service registered: ${serviceName} at ${instance.url}`);
  }

  deregisterService(serviceName: string, instanceId: string): void {
    const instances = this.services.get(serviceName);
    if (instances) {
      const index = instances.findIndex(i => i.id === instanceId);
      if (index !== -1) {
        instances.splice(index, 1);
        this.stopHealthCheck(instanceId);
        console.log(`Service deregistered: ${serviceName}/${instanceId}`);
      }
    }
  }

  getHealthyInstances(serviceName: string): ServiceInstance[] {
    const instances = this.services.get(serviceName) || [];
    return instances.filter(i => i.healthy);
  }

  getAllServices(): Record<string, ServiceInstance[]> {
    return Object.fromEntries(this.services);
  }

  private startHealthCheck(serviceName: string, instance: ServiceInstance): void {
    const checkInterval = setInterval(async () => {
      try {
        const response = await fetch(`${instance.url}/health`, {
          method: 'GET',
          timeout: 5000
        });
        
        const wasHealthy = instance.healthy;
        instance.healthy = response.ok;
        instance.lastSeen = new Date();

        if (wasHealthy !== instance.healthy) {
          console.log(`Service ${serviceName}/${instance.id} health changed: ${instance.healthy}`);
        }
      } catch (error) {
        const wasHealthy = instance.healthy;
        instance.healthy = false;
        instance.lastSeen = new Date();

        if (wasHealthy) {
          console.error(`Service ${serviceName}/${instance.id} health check failed:`, error);
        }
      }
    }, 30000); // Check every 30 seconds

    this.healthChecks.set(instance.id, checkInterval);
  }

  private stopHealthCheck(instanceId: string): void {
    const interval = this.healthChecks.get(instanceId);
    if (interval) {
      clearInterval(interval);
      this.healthChecks.delete(instanceId);
    }
  }
}

// Load balancer with multiple strategies
class LoadBalancer {
  private roundRobinCounters: Map<string, number> = new Map();

  selectInstance(
    instances: ServiceInstance[], 
    strategy: LoadBalancingStrategy = 'round-robin'
  ): ServiceInstance | null {
    const healthyInstances = instances.filter(i => i.healthy);
    
    if (healthyInstances.length === 0) {
      return null;
    }

    switch (strategy) {
      case 'round-robin':
        return this.roundRobin(healthyInstances);
      case 'least-connections':
        return this.leastConnections(healthyInstances);
      case 'weighted-round-robin':
        return this.weightedRoundRobin(healthyInstances);
      case 'random':
        return this.random(healthyInstances);
      default:
        return this.roundRobin(healthyInstances);
    }
  }

  private roundRobin(instances: ServiceInstance[]): ServiceInstance {
    const serviceKey = instances[0]?.serviceName || 'default';
    const counter = this.roundRobinCounters.get(serviceKey) || 0;
    const selectedInstance = instances[counter % instances.length];
    this.roundRobinCounters.set(serviceKey, counter + 1);
    return selectedInstance;
  }

  private leastConnections(instances: ServiceInstance[]): ServiceInstance {
    return instances.reduce((min, current) => 
      current.connections < min.connections ? current : min
    );
  }

  private weightedRoundRobin(instances: ServiceInstance[]): ServiceInstance {
    // Simple weighted selection based on instance weight
    const totalWeight = instances.reduce((sum, i) => sum + i.weight, 0);
    let random = Math.random() * totalWeight;
    
    for (const instance of instances) {
      random -= instance.weight;
      if (random <= 0) {
        return instance;
      }
    }
    
    return instances[0]; // Fallback
  }

  private random(instances: ServiceInstance[]): ServiceInstance {
    return instances[Math.floor(Math.random() * instances.length)];
  }
}

// Request routing and proxying
class RequestRouter {
  constructor(
    private serviceRegistry: ServiceRegistry,
    private loadBalancer: LoadBalancer
  ) {}

  async routeRequest(
    serviceName: string,
    path: string,
    request: Request,
    strategy?: LoadBalancingStrategy
  ): Promise<Response> {
    const instances = this.serviceRegistry.getHealthyInstances(serviceName);
    
    if (instances.length === 0) {
      return new Response(
        JSON.stringify({ error: `Service ${serviceName} unavailable` }),
        { status: 503, headers: { 'content-type': 'application/json' } }
      );
    }

    const selectedInstance = this.loadBalancer.selectInstance(instances, strategy);
    
    if (!selectedInstance) {
      return new Response(
        JSON.stringify({ error: 'No healthy instances available' }),
        { status: 503, headers: { 'content-type': 'application/json' } }
      );
    }

    // Increment connection count
    selectedInstance.connections++;

    try {
      const targetUrl = `${selectedInstance.url}${path}`;
      const proxyRequest = new Request(targetUrl, {
        method: request.method,
        headers: request.headers,
        body: request.method !== 'GET' ? request.body : undefined
      });

      const response = await fetch(proxyRequest);
      
      // Copy response with additional headers
      const proxyResponse = new Response(response.body, {
        status: response.status,
        statusText: response.statusText,
        headers: {
          ...Object.fromEntries(response.headers),
          'x-served-by': selectedInstance.id,
          'x-service-name': serviceName
        }
      });

      return proxyResponse;

    } catch (error) {
      console.error(`Request routing failed for ${serviceName}:`, error);
      
      // Mark instance as unhealthy on error
      selectedInstance.healthy = false;
      
      return new Response(
        JSON.stringify({ error: 'Service request failed' }),
        { status: 502, headers: { 'content-type': 'application/json' } }
      );
    } finally {
      // Decrement connection count
      selectedInstance.connections--;
    }
  }
}

// Main API Gateway
export class APIGateway {
  private app: Hono;
  private serviceRegistry: ServiceRegistry;
  private loadBalancer: LoadBalancer;
  private requestRouter: RequestRouter;
  private rateLimiters: Map<string, RateLimiter> = new Map();

  constructor() {
    this.app = new Hono();
    this.serviceRegistry = new ServiceRegistry();
    this.loadBalancer = new LoadBalancer();
    this.requestRouter = new RequestRouter(this.serviceRegistry, this.loadBalancer);

    this.setupMiddleware();
    this.setupRoutes();
    this.registerDefaultServices();
  }

  private setupMiddleware(): void {
    // CORS configuration
    this.app.use('*', cors({
      origin: ['https://scm-legal.pages.dev', 'http://localhost:3000'],
      allowMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
      allowHeaders: ['Content-Type', 'Authorization', 'X-Jurisdiction', 'X-Client-ID'],
      exposeHeaders: ['X-Served-By', 'X-Service-Name']
    }));

    // Request logging with enhanced information
    this.app.use('*', logger((message, ...rest) => {
      console.log(`[API Gateway] ${message}`, ...rest);
    }));

    // Global rate limiting
    this.app.use('/api/*', async (c, next) => {
      const clientId = c.req.header('x-client-id') || 
                      c.req.header('cf-connecting-ip') || 
                      'anonymous';
      
      if (!this.rateLimiters.has(clientId)) {
        this.rateLimiters.set(clientId, new RateLimiter(200, 60000)); // 200 req/min per client
      }

      const limiter = this.rateLimiters.get(clientId)!;
      if (!limiter.isAllowed(clientId)) {
        return c.json({ error: 'Rate limit exceeded' }, 429);
      }

      await next();
    });

    // Authentication middleware (JWT)
    this.app.use('/api/admin/*', jwt({
      secret: process.env.JWT_SECRET || 'dev-secret-key',
      cookie: 'auth-token'
    }));

    // Request ID generation for tracing
    this.app.use('*', async (c, next) => {
      const requestId = c.req.header('x-request-id') || 
                       `req_${Date.now()}_${Math.random().toString(36).substring(2)}`;
      c.set('requestId', requestId);
      c.header('x-request-id', requestId);
      await next();
    });
  }

  private setupRoutes(): void {
    // Legal concept service routing
    this.app.all('/api/legal/*', async (c) => {
      const path = new URL(c.req.url).pathname;
      return this.requestRouter.routeRequest('legal-concept-service', path, c.req);
    });

    // Jurisdiction service routing
    this.app.all('/api/jurisdictions/*', async (c) => {
      const path = new URL(c.req.url).pathname;
      return this.requestRouter.routeRequest('jurisdiction-service', path, c.req);
    });

    // Training service routing (for model updates)
    this.app.all('/api/training/*', async (c) => {
      const path = new URL(c.req.url).pathname;
      return this.requestRouter.routeRequest('training-service', path, c.req, 'least-connections');
    });

    // Service registry management
    this.app.post('/api/admin/services/register', async (c) => {
      const instance: ServiceInstance = await c.req.json();
      this.serviceRegistry.registerService(instance.serviceName, instance);
      return c.json({ message: 'Service registered successfully' });
    });

    this.app.delete('/api/admin/services/:serviceName/:instanceId', async (c) => {
      const serviceName = c.req.param('serviceName');
      const instanceId = c.req.param('instanceId');
      this.serviceRegistry.deregisterService(serviceName, instanceId);
      return c.json({ message: 'Service deregistered successfully' });
    });

    this.app.get('/api/admin/services', (c) => {
      const services = this.serviceRegistry.getAllServices();
      return c.json({ services });
    });

    // Gateway health and metrics
    this.app.get('/health', (c) => {
      return c.json({ 
        status: 'healthy',
        timestamp: new Date().toISOString(),
        services: Object.keys(this.serviceRegistry.getAllServices()).length
      });
    });

    this.app.get('/metrics', (c) => {
      const services = this.serviceRegistry.getAllServices();
      const metrics = {
        totalServices: Object.keys(services).length,
        healthyInstances: Object.values(services)
          .flat()
          .filter(i => i.healthy).length,
        totalInstances: Object.values(services).flat().length,
        serviceDetails: services
      };
      
      return c.json(metrics);
    });

    // Catch-all for unknown routes
    this.app.all('*', (c) => {
      return c.json({ 
        error: 'Route not found',
        path: c.req.url,
        method: c.req.method 
      }, 404);
    });
  }

  private registerDefaultServices(): void {
    // Register default local services for development
    this.serviceRegistry.registerService('legal-concept-service', {
      id: 'legal-concept-1',
      serviceName: 'legal-concept-service',
      url: 'http://localhost:3001',
      healthy: true,
      weight: 1.0,
      connections: 0,
      lastSeen: new Date(),
      metadata: {
        version: '1.0.0',
        region: 'local'
      }
    });

    this.serviceRegistry.registerService('jurisdiction-service', {
      id: 'jurisdiction-1',
      serviceName: 'jurisdiction-service',
      url: 'http://localhost:3002',
      healthy: true,
      weight: 1.0,
      connections: 0,
      lastSeen: new Date(),
      metadata: {
        version: '1.0.0',
        region: 'local'
      }
    });
  }

  getApp(): Hono {
    return this.app;
  }

  getServiceRegistry(): ServiceRegistry {
    return this.serviceRegistry;
  }
}

// Type definitions
interface ServiceInstance {
  id: string;
  serviceName: string;
  url: string;
  healthy: boolean;
  weight: number;
  connections: number;
  lastSeen: Date;
  metadata: {
    version: string;
    region: string;
    [key: string]: any;
  };
}

type LoadBalancingStrategy = 'round-robin' | 'least-connections' | 'weighted-round-robin' | 'random';

// Rate limiter class
class RateLimiter {
  private requests: Map<string, number[]> = new Map();

  constructor(
    private maxRequests: number = 100,
    private windowMs: number = 60000
  ) {}

  isAllowed(clientId: string): boolean {
    const now = Date.now();
    const windowStart = now - this.windowMs;

    if (!this.requests.has(clientId)) {
      this.requests.set(clientId, []);
    }

    const clientRequests = this.requests.get(clientId)!;
    const validRequests = clientRequests.filter(timestamp => timestamp > windowStart);
    
    if (validRequests.length >= this.maxRequests) {
      return false;
    }

    validRequests.push(now);
    this.requests.set(clientId, validRequests);
    return true;
  }
}