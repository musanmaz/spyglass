import { useQueryStore } from '../../store/queryStore';
import { StreamingResult } from './StreamingResult';
import { ErrorState } from './ErrorState';

export function ResultsContainer() {
  const { streamingLines, streamingStatus, streamingMeta, error } = useQueryStore();

  if (streamingStatus === 'idle') return null;

  if (streamingStatus === 'error' && error && streamingLines.length === 0) {
    return <ErrorState message={error} />;
  }

  return (
    <StreamingResult
      lines={streamingLines}
      status={streamingStatus}
      meta={streamingMeta}
      error={error}
    />
  );
}
