import { useState, useCallback } from 'react';
import { rateLimiter } from '../lib/rateLimiter';

export function useRateLimit() {
  const [isLimited, setIsLimited] = useState(false);
  const [retryAfter, setRetryAfter] = useState(0);
  const [message, setMessage] = useState('');

  const checkLimit = useCallback((): boolean => {
    const result = rateLimiter.canMakeRequest();
    if (!result.allowed) {
      setIsLimited(true);
      setRetryAfter(result.retryAfter ?? 0);
      setMessage(result.message ?? '');
      setTimeout(() => {
        setIsLimited(false);
        setRetryAfter(0);
        setMessage('');
      }, (result.retryAfter ?? 5) * 1000);
      return false;
    }
    rateLimiter.recordRequest();
    return true;
  }, []);

  return { isLimited, retryAfter, message, checkLimit };
}
