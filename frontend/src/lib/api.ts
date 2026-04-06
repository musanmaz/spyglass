import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 45_000,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 429) {
      const retryAfter =
        error.response.headers['retry-after'] ||
        error.response.data?.detail?.retry_after ||
        60;
      window.dispatchEvent(
        new CustomEvent('rate-limit-exceeded', {
          detail: {
            retryAfter: Number(retryAfter),
            message: error.response.data?.detail?.message || 'Too many requests.',
          },
        }),
      );
    }
    return Promise.reject(error);
  },
);

export default api;
