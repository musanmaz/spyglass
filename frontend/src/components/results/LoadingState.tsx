import { Spinner } from '../ui/Spinner';

export function LoadingState() {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-4 animate-fade-in">
      <Spinner size="lg" />
      <p className="text-sm font-medium" style={{ color: 'var(--lg-text-muted)' }}>
        Querying devices...
      </p>
    </div>
  );
}
