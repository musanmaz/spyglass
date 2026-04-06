import { QUERY_TYPES } from '../../lib/constants';
import { useQueryStore } from '../../store/queryStore';

export function QueryTypeSelector() {
  const queryType = useQueryStore((s) => s.queryType);
  const setQueryType = useQueryStore((s) => s.setQueryType);
  const isLoading = useQueryStore((s) => s.isLoading);
  const supported = useQueryStore((s) => s.supportedQueryTypes);

  const visibleTypes = supported.length > 0
    ? QUERY_TYPES.filter((qt) => supported.includes(qt.id))
    : QUERY_TYPES;

  return (
    <div className="flex flex-wrap gap-2">
      {visibleTypes.map((qt) => (
        <button
          key={qt.id}
          onClick={() => setQueryType(qt.id)}
          disabled={isLoading}
          className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed ${
            queryType === qt.id
              ? 'bg-brand-gradient text-white shadow-brand-button'
              : 'border hover:border-brand-primary-300 dark:hover:border-brand-primary-700'
          }`}
          style={queryType !== qt.id ? { borderColor: 'var(--lg-border)', color: 'var(--lg-text-secondary)', backgroundColor: 'var(--lg-bg-secondary)' } : undefined}
        >
          {qt.name}
        </button>
      ))}
    </div>
  );
}
