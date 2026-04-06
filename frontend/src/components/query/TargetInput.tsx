import { useCallback, useState } from 'react';
import { useQueryStore } from '../../store/queryStore';
import { isValidTarget } from '../../lib/validators';
import { QUERY_TYPE_PLACEHOLDERS } from '../../lib/constants';
import clsx from 'clsx';

export function TargetInput() {
  const target = useQueryStore((s) => s.target);
  const setTarget = useQueryStore((s) => s.setTarget);
  const queryType = useQueryStore((s) => s.queryType);
  const isLoading = useQueryStore((s) => s.isLoading);
  const [error, setError] = useState<string | null>(null);
  const [loadingIp, setLoadingIp] = useState(false);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const val = e.target.value;
      setTarget(val);
      if (val.trim()) {
        setError(isValidTarget(val, queryType));
      } else {
        setError(null);
      }
    },
    [queryType, setTarget],
  );

  const handleMyIp = async () => {
    setLoadingIp(true);
    try {
      const res = await fetch('https://api.ipify.org?format=json');
      const data = await res.json();
      if (data.ip) {
        setTarget(data.ip);
        setError(null);
      } else {
        throw new Error();
      }
    } catch {
      setError('Could not detect IP address');
    } finally {
      setLoadingIp(false);
    }
  };

  return (
    <div className="w-full">
      <div className="relative">
        <input
          value={target}
          onChange={handleChange}
          disabled={isLoading}
          placeholder={QUERY_TYPE_PLACEHOLDERS[queryType] || 'IP address or prefix'}
          spellCheck={false}
          autoComplete="off"
          className={clsx(
            'w-full pl-4 pr-20 py-3 rounded-xl text-[15px] font-mono transition-all duration-200 outline-none disabled:opacity-50 disabled:cursor-not-allowed',
            error
              ? 'border-2 border-red-400 focus:border-red-500 focus:ring-2 focus:ring-red-200'
              : 'border focus:border-brand-primary-500 focus:shadow-brand-glow',
          )}
          style={{
            backgroundColor: 'var(--lg-bg-secondary)',
            borderColor: error ? undefined : 'var(--lg-border)',
            color: 'var(--lg-text-primary)',
          }}
        />
        <button
          type="button"
          onClick={handleMyIp}
          disabled={loadingIp || isLoading}
          className="absolute right-2 top-1/2 -translate-y-1/2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 hover:bg-brand-primary-100 dark:hover:bg-brand-primary-900/40 disabled:opacity-50 disabled:cursor-not-allowed"
          style={{ color: 'var(--lg-text-secondary)', backgroundColor: 'var(--lg-bg-tertiary)' }}
        >
          {loadingIp ? (
            <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
          ) : (
            'My IP'
          )}
        </button>
      </div>
      {error && <p className="mt-1.5 text-sm text-red-500">{error}</p>}
    </div>
  );
}
