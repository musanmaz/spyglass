const CONFIG = {
  maxRequests: 10,
  windowMs: 60_000,
  cooldownMs: 5_000,
  lockoutMs: 60_000,
  lockoutThreshold: 12,
} as const;

class ClientRateLimiter {
  private requests: number[] = [];
  private lockoutUntil: number | null = null;

  canMakeRequest(): { allowed: boolean; retryAfter?: number; message?: string } {
    const now = Date.now();

    if (this.lockoutUntil && now < this.lockoutUntil) {
      const retryAfter = Math.ceil((this.lockoutUntil - now) / 1000);
      return { allowed: false, retryAfter, message: `Too many requests. Wait ${retryAfter}s.` };
    }

    this.requests = this.requests.filter((t) => now - t < CONFIG.windowMs);

    const lastReq = this.requests[this.requests.length - 1];
    if (lastReq && now - lastReq < CONFIG.cooldownMs) {
      const retryAfter = Math.ceil((CONFIG.cooldownMs - (now - lastReq)) / 1000);
      return { allowed: false, retryAfter, message: `Please wait ${retryAfter}s.` };
    }

    if (this.requests.length >= CONFIG.maxRequests) {
      if (this.requests.length >= CONFIG.lockoutThreshold) {
        this.lockoutUntil = now + CONFIG.lockoutMs;
      }
      const oldest = this.requests[0];
      const retryAfter = Math.ceil((CONFIG.windowMs - (now - oldest)) / 1000);
      return { allowed: false, retryAfter, message: `Maximum ${CONFIG.maxRequests} queries per minute. Wait ${retryAfter}s.` };
    }

    return { allowed: true };
  }

  recordRequest(): void {
    this.requests.push(Date.now());
  }
}

export const rateLimiter = new ClientRateLimiter();
