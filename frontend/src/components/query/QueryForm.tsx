import { useRef } from 'react';
import { Card } from '../ui/Card';
import { QueryTypeSelector } from './QueryTypeSelector';
import { TargetInput } from './TargetInput';
import { QueryButton } from './QueryButton';
import { useQueryStore } from '../../store/queryStore';
import { isValidTarget } from '../../lib/validators';

export function QueryForm() {
  const {
    queryType, target, isLoading, setLoading, setError,
    appendStreamLine, setStreamingStatus, setStreamingMeta, resetStream,
  } = useQueryStore();
  const wsRef = useRef<WebSocket | null>(null);

  const canSubmit = target.trim().length > 0 && !isLoading && isValidTarget(target.trim(), queryType) === null;

  const handleSubmit = () => {
    if (!canSubmit) return;

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    resetStream();
    setLoading(true);
    setError(null);
    setStreamingStatus('connecting');

    const backendUrl = import.meta.env.VITE_WS_URL;
    let wsUrl: string;
    if (backendUrl) {
      wsUrl = backendUrl;
    } else {
      const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
      wsUrl = `${proto}//${location.host}/ws/query`;
    }
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      ws.send(JSON.stringify({
        query_type: queryType,
        target: target.trim(),
      }));
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);

        switch (msg.type) {
          case 'status':
            setStreamingStatus('streaming');
            break;
          case 'output':
            appendStreamLine(msg.data);
            break;
          case 'complete':
            setStreamingMeta({
              response_time_ms: msg.response_time_ms,
              request_id: msg.request_id,
            });
            setStreamingStatus('done');
            setLoading(false);
            break;
          case 'error':
            setError(msg.message || 'Query failed');
            setStreamingStatus('error');
            setLoading(false);
            break;
        }
      } catch {
        /* ignore parse errors */
      }
    };

    ws.onerror = () => {
      setError('Connection error');
      setStreamingStatus('error');
      setLoading(false);
    };

    ws.onclose = (event) => {
      if (event.code === 4029) {
        setError('Too many requests. Please wait.');
        setStreamingStatus('error');
      } else if (event.code === 4003) {
        setError('Connection rejected');
        setStreamingStatus('error');
      }
      setLoading(false);
      wsRef.current = null;
    };
  };

  return (
    <Card className="space-y-5 dark:bg-[rgba(26,14,48,0.6)] dark:backdrop-blur-xl">
      <div>
        <label className="block text-sm font-medium mb-2" style={{ color: 'var(--lg-text-secondary)' }}>Query Type</label>
        <QueryTypeSelector />
      </div>
      <div>
        <label className="block text-sm font-medium mb-2" style={{ color: 'var(--lg-text-secondary)' }}>Target</label>
        <TargetInput />
      </div>
      <QueryButton onSubmit={handleSubmit} isLoading={isLoading} disabled={!canSubmit} />
    </Card>
  );
}
