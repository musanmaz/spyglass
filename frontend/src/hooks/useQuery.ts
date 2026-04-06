import { useMutation } from '@tanstack/react-query';
import api from '../lib/api';
import type { QueryRequest, QueryResponse } from '../types/query';
import { useQueryStore } from '../store/queryStore';

export function useLookingGlassQuery() {
  const { setLoading, setResults, setError } = useQueryStore();

  return useMutation<QueryResponse, Error, QueryRequest>({
    mutationFn: async (params) => {
      const res = await api.post<QueryResponse>('/v1/query', params);
      return res.data;
    },
    onMutate: () => {
      setLoading(true);
      setError(null);
    },
    onSuccess: (data) => {
      setResults(data);
    },
    onError: (error: any) => {
      const msg = error.response?.data?.detail?.message || 'Query failed.';
      setError(msg);
    },
    onSettled: () => {
      setLoading(false);
    },
  });
}
