import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { OutputRenderer } from './OutputRenderer';
import type { QueryResultItem } from '../../types/query';

interface ResultCardProps {
  result: QueryResultItem;
}

export function ResultCard({ result }: ResultCardProps) {
  const isSuccess = result.status === 'success';

  return (
    <Card hoverable className="animate-slide-up">
      <div className="flex flex-wrap items-center gap-3 mb-4">
        <span className={`w-2 h-2 rounded-full ${isSuccess ? 'bg-emerald-500' : 'bg-red-500'}`} />
        <div className="ml-auto flex items-center gap-2 text-sm" style={{ color: 'var(--lg-text-muted)' }}>
          {isSuccess && <span>{result.response_time_ms}ms</span>}
          <Badge variant={isSuccess ? 'success' : 'error'}>
            {isSuccess ? 'Complete' : 'Error'}
          </Badge>
          {result.cached && <Badge variant="warning">Cache</Badge>}
        </div>
      </div>
      {isSuccess && result.output ? (
        <OutputRenderer output={result.output} />
      ) : result.error ? (
        <p className="text-sm text-red-500">{result.error}</p>
      ) : null}
    </Card>
  );
}
