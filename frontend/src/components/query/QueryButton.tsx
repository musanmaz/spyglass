import { Button } from '../ui/Button';
import { Spinner } from '../ui/Spinner';
import { useRateLimit } from '../../hooks/useRateLimit';

interface QueryButtonProps {
  onSubmit: () => void;
  isLoading: boolean;
  disabled?: boolean;
}

export function QueryButton({ onSubmit, isLoading, disabled }: QueryButtonProps) {
  const { isLimited, retryAfter, message, checkLimit } = useRateLimit();

  const handleClick = () => {
    if (!checkLimit()) return;
    onSubmit();
  };

  return (
    <div>
      <Button
        onClick={handleClick}
        disabled={isLoading || isLimited || disabled}
        className="w-full"
        size="lg"
      >
        {isLoading ? (
          <span className="flex items-center gap-2">
            <Spinner size="sm" className="text-white" />
            Querying...
          </span>
        ) : isLimited ? (
          `Wait (${retryAfter}s)`
        ) : (
          'Submit'
        )}
      </Button>
      {isLimited && message && (
        <p className="mt-2 text-sm text-amber-500 text-center animate-slide-up">{message}</p>
      )}
    </div>
  );
}
