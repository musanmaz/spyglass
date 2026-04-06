import { create } from 'zustand';
import type { QueryResponse } from '../types/query';

interface QueryState {
  queryType: string;
  target: string;
  selectedDevices: string[];
  isLoading: boolean;
  results: QueryResponse | null;
  error: string | null;
  streamingLines: string[];
  streamingStatus: 'idle' | 'connecting' | 'streaming' | 'done' | 'error';
  streamingMeta: { response_time_ms?: number; request_id?: string } | null;

  setQueryType: (type: string) => void;
  setTarget: (target: string) => void;
  setSelectedDevices: (devices: string[]) => void;
  setLoading: (loading: boolean) => void;
  setResults: (results: QueryResponse | null) => void;
  setError: (error: string | null) => void;
  appendStreamLine: (line: string) => void;
  setStreamingStatus: (status: 'idle' | 'connecting' | 'streaming' | 'done' | 'error') => void;
  setStreamingMeta: (meta: { response_time_ms?: number; request_id?: string } | null) => void;
  resetStream: () => void;
  reset: () => void;
}

export const useQueryStore = create<QueryState>((set) => ({
  queryType: 'bgp_route',
  target: '',
  selectedDevices: [],
  isLoading: false,
  results: null,
  error: null,
  streamingLines: [],
  streamingStatus: 'idle',
  streamingMeta: null,

  setQueryType: (queryType) => set({ queryType }),
  setTarget: (target) => set({ target }),
  setSelectedDevices: (selectedDevices) => set({ selectedDevices }),
  setLoading: (isLoading) => set({ isLoading }),
  setResults: (results) => set({ results, error: null }),
  setError: (error) => set({ error, results: null }),
  appendStreamLine: (line) => set((s) => ({ streamingLines: [...s.streamingLines, line] })),
  setStreamingStatus: (streamingStatus) => set({ streamingStatus }),
  setStreamingMeta: (streamingMeta) => set({ streamingMeta }),
  resetStream: () => set({ streamingLines: [], streamingStatus: 'idle', streamingMeta: null, error: null }),
  reset: () => set({
    queryType: 'bgp_route', target: '', selectedDevices: [], isLoading: false,
    results: null, error: null, streamingLines: [],
    streamingStatus: 'idle', streamingMeta: null,
  }),
}));
