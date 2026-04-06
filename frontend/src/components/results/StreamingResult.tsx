import { useEffect, useRef, useState } from 'react';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Spinner } from '../ui/Spinner';

interface StreamingResultProps {
  lines: string[];
  status: 'idle' | 'connecting' | 'streaming' | 'done' | 'error';
  meta: { response_time_ms?: number; request_id?: string } | null;
  error: string | null;
}

export function StreamingResult({ lines, status, meta, error }: StreamingResultProps) {
  const preRef = useRef<HTMLPreElement>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (preRef.current) {
      preRef.current.scrollTop = preRef.current.scrollHeight;
    }
  }, [lines]);

  const fullOutput = lines.join('\n');

  const handleCopy = async () => {
    await navigator.clipboard.writeText(fullOutput);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isActive = status === 'connecting' || status === 'streaming';

  return (
    <Card className="animate-slide-up">
      <div className="flex flex-wrap items-center gap-3 mb-4">
        {isActive && <Spinner size="sm" />}
        {!isActive && (
          <span className={`w-2 h-2 rounded-full ${status === 'done' ? 'bg-emerald-500' : 'bg-red-500'}`} />
        )}

        <span className="text-sm" style={{ color: 'var(--lg-text-muted)' }}>
          {status === 'connecting' && 'Connecting to device...'}
          {status === 'streaming' && 'Query in progress...'}
          {status === 'done' && meta?.response_time_ms != null && `${meta.response_time_ms}ms`}
          {status === 'error' && 'Error'}
        </span>

        <div className="ml-auto flex items-center gap-2">
          {status === 'done' && (
            <Badge variant="success">Complete</Badge>
          )}
          {status === 'error' && (
            <Badge variant="error">Error</Badge>
          )}
          {(status === 'done' || lines.length > 0) && (
            <button
              onClick={handleCopy}
              className="px-3 py-1.5 rounded-lg text-xs font-medium bg-brand-primary-800 text-white hover:bg-brand-primary-700 transition-colors"
            >
              {copied ? 'Copied' : 'Copy'}
            </button>
          )}
        </div>
      </div>

      <div className="relative">
        <pre
          ref={preRef}
          className="font-mono text-[13px] leading-relaxed p-4 rounded-xl overflow-x-auto overflow-y-auto whitespace-pre-wrap break-words border"
          style={{
            backgroundColor: 'var(--lg-bg-tertiary)',
            borderColor: 'var(--lg-border)',
            color: 'var(--lg-text-primary)',
            maxHeight: '70vh',
            minHeight: lines.length > 0 ? '120px' : '60px',
          }}
        >
          {lines.length > 0 ? (
            lines.map((line, i) => (
              <span key={i}>
                {line}
                {i < lines.length - 1 && '\n'}
              </span>
            ))
          ) : isActive ? (
            <span style={{ color: 'var(--lg-text-muted)' }}>Waiting...</span>
          ) : null}
          {isActive && <span className="inline-block w-2 h-4 ml-0.5 bg-brand-primary-500 animate-pulse" />}
        </pre>
      </div>

      {error && status === 'error' && lines.length > 0 && (
        <p className="mt-3 text-sm text-red-500">{error}</p>
      )}
    </Card>
  );
}
