# Example: Cache Strategy Debate

This example shows how the decision-debate skill works in practice.

## User Request

> "我們需要為 API response 加快取，但不確定要用 Redis 還是 in-memory cache。請幫我分析。"

## Step 1: Frame the Decision

```markdown
**Context:** API responses need caching to improve performance. Current architecture uses Supabase Edge Functions (Deno runtime).

**Approaches:**
- Approach A: Use Redis (external cache service)
- Approach B: Use in-memory cache (edge function local)

**Criteria:**
1. Performance (latency)
2. Scalability (multi-instance)
3. Complexity (implementation effort)
4. Cost (infrastructure)
5. Reliability (failure modes)
```

## Step 2: Dispatch Advocates (Parallel)

### Claude dispatches two Task agents simultaneously:

**Task 1: Advocate for Redis**
```
You are advocating for Redis as the caching solution.

Context: API responses need caching for Supabase Edge Functions (Deno runtime).

Your position: Use Redis (Upstash or similar) as external cache service.

Tasks:
1. Search codebase for existing cache patterns or Redis usage
2. Find evidence supporting Redis (distributed systems, session handling)
3. Identify 3-5 advantages with codebase references
4. Acknowledge 1-2 weaknesses honestly
5. Propose mitigation strategies

Return structured argument with file:line references.
```

**Task 2: Advocate for In-Memory Cache**
```
You are advocating for in-memory caching solution.

Context: API responses need caching for Supabase Edge Functions (Deno runtime).

Your position: Use in-memory cache (Map, LRU cache) within edge function.

Tasks:
1. Search codebase for existing in-memory patterns
2. Find evidence supporting in-memory approach
3. Identify 3-5 advantages with codebase references
4. Acknowledge 1-2 weaknesses honestly
5. Propose mitigation strategies

Return structured argument with file:line references.
```

## Step 3: Advocate Results (Simulated)

### Advocate A (Redis) Returns:

**Position Summary:** Redis provides distributed caching that works across all edge function instances, ensuring cache consistency and enabling advanced features like TTL, pub/sub for invalidation.

**Key Advantages:**
1. **Shared state** - All edge instances share same cache (apps/deno-api/src/middlewares/ shows stateless design)
2. **Persistence** - Survives function cold starts
3. **Advanced features** - TTL, pattern matching, pub/sub invalidation
4. **Scalability** - Handles high throughput with cluster mode

**Evidence from Codebase:**
- `apps/deno-api/src/hono.ts:45` - Middleware designed for stateless operation
- `packages/drizzle-support/` - Already uses external state (PostgreSQL)

**Acknowledged Weaknesses:**
1. Network latency (additional hop)
2. Additional infrastructure cost
3. New dependency to manage

**Mitigation:** Use Upstash Redis (serverless, pay-per-use), implement connection pooling.

**Recommendation Confidence:** High

---

### Advocate B (In-Memory) Returns:

**Position Summary:** In-memory caching eliminates network latency and external dependencies. For edge functions with short-lived instances, simple LRU cache provides significant improvement with minimal complexity.

**Key Advantages:**
1. **Zero latency** - No network hop, nanosecond access
2. **No infrastructure** - No external service to manage
3. **Simplicity** - Standard Map or LRU library
4. **Cost** - No additional service fees

**Evidence from Codebase:**
- `apps/deno-api/` - Deno runtime supports standard cache patterns
- Edge functions are stateless by design, but can cache within request lifecycle

**Acknowledged Weaknesses:**
1. No sharing between instances (cache miss on cold start)
2. Memory limits in edge functions
3. No persistence across deployments

**Mitigation:** Implement short TTL (5-15 seconds), focus on hot-path caching, use LRU eviction.

**Recommendation Confidence:** Medium

## Step 4: Staff Engineer Evaluation

**Task 3: Staff Engineer Final Recommendation**

```
You are a staff engineer making a final recommendation.

Context: API response caching for Supabase Edge Functions

Advocate A (Redis) argument:
[paste full Redis argument]

Advocate B (In-Memory) argument:
[paste full In-Memory argument]

Evaluate and recommend.
```

### Staff Engineer Returns:

**Argument Analysis:**
- Redis advocate made stronger case for **production scenarios** with multi-instance edge functions
- In-memory advocate made stronger case for **simplicity** and **latency-critical** paths
- Both correctly identified their weaknesses

**Blind Spots Identified:**
1. Neither considered **hybrid approach** (in-memory L1 + Redis L2)
2. Neither analyzed **cache hit rate** expectations
3. Missing consideration of **edge function cold start frequency**

**Additional Considerations:**
- Supabase Edge Functions can have **~50ms cold starts** - in-memory cache lost each time
- API patterns in `apps/deno-api/src/routers/` show **per-request** operations, not long-running
- Production traffic likely hits **multiple instances** simultaneously

**Final Recommendation:** **Hybrid Approach with Redis as primary**

**Reasoning:**
1. Start with Redis for shared state (critical for correctness)
2. Add thin in-memory cache for repeated within-request lookups
3. Use Upstash Redis (serverless pricing, ~$0.20/100K requests)

**Implementation Guidance:**
```typescript
// L1: In-memory for hot path
const localCache = new Map<string, { data: unknown; exp: number }>();

// L2: Redis for shared state
import { Redis } from '@upstash/redis';
const redis = Redis.fromEnv();

async function getCached<T>(key: string): Promise<T | null> {
  // L1 check (microseconds)
  const local = localCache.get(key);
  if (local && local.exp > Date.now()) return local.data as T;

  // L2 check (milliseconds)
  const remote = await redis.get<T>(key);
  if (remote) {
    localCache.set(key, { data: remote, exp: Date.now() + 5000 });
  }
  return remote;
}
```

**Risk Mitigation:**
- Set up Redis connection error handling (fallback to no-cache)
- Monitor cache hit rates in first week
- Set memory limits on local cache (max 100 entries)

## Final Summary Presented to User

```markdown
## Decision Debate Summary

### The Question
Should we use Redis or in-memory cache for API response caching?

### Advocate for Redis
- ✅ Shared state across all edge instances
- ✅ Survives cold starts and deployments
- ✅ Advanced features (TTL, invalidation)
- ⚠️ Additional network latency
- ⚠️ Infrastructure cost

### Advocate for In-Memory
- ✅ Zero latency (nanoseconds)
- ✅ No infrastructure to manage
- ✅ Simple implementation
- ⚠️ Lost on cold start
- ⚠️ No cross-instance sharing

### Staff Engineer Verdict
**Recommendation:** Hybrid (Redis primary + in-memory L1)

**Reasoning:** Edge functions are multi-instance and have cold starts, so shared state is critical. But add thin in-memory cache for within-request performance.

**Key factors:**
1. Production correctness requires shared cache
2. Upstash Redis has serverless pricing (~$0.20/100K)
3. L1 cache handles repeated lookups in same request

### Implementation Next Steps
1. Set up Upstash Redis account
2. Add `@upstash/redis` to deno.json imports
3. Create `cache-middleware.ts` with hybrid approach
4. Add cache keys to API responses
```
