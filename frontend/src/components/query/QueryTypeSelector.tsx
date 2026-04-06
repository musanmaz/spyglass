import { QUERY_TYPES } from '../../lib/constants';
import { useQueryStore } from '../../store/queryStore';

export function QueryTypeSelector() {
  const queryType = useQueryStore((s) => s.queryType);
  const setQueryType = useQueryStore((s) => s.setQueryType);
  const isLoading = useQueryStore((s) => s.isLoading);
  const supported = useQueryStore((s) => s.supportedQueryTypes);

  return (
    <div className="flex flex-wrap gap-2">
      {QUERY_TYPES.map((qt) => {
        const isSupported = supported.length === 0 || supported.includes(qt.id);
        return (
          <button
            key={qt.id}
            onClick={() => setQueryType(qt.id)}
            disabled={isLoading || !isSupported}
            title={!isSupported ? `${qt.name} is not supported by this device` : undefined}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed ${
              queryType === qt.id && isSupported
                ? 'bg-brand-gradient text-white shadow-brand-button'
                : 'border hover:border-brand-primary-300 dark:hover:border-brand-primary-700'
            }`}
            style={!(queryType === qt.id && isSupported) ? { borderColor: 'var(--lg-border)', color: 'var(--lg-text-secondary)', backgroundColor: 'var(--lg-bg-secondary)' } : undefined}
          >
            {qt.name}
          </button>
        );
      })}
    </div>
  );
}
