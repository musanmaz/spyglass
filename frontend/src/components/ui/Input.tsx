import clsx from 'clsx';
import { InputHTMLAttributes, forwardRef } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ error, className, ...props }, ref) => {
    return (
      <div className="w-full">
        <input
          ref={ref}
          className={clsx(
            'w-full px-4 py-3 rounded-xl text-[15px] font-mono transition-all duration-200 outline-none',
            error
              ? 'border-2 border-red-400 focus:border-red-500 focus:ring-2 focus:ring-red-200'
              : 'border focus:border-brand-primary-500 focus:shadow-brand-glow',
            className,
          )}
          style={{
            backgroundColor: 'var(--lg-bg-secondary)',
            borderColor: error ? undefined : 'var(--lg-border)',
            color: 'var(--lg-text-primary)',
          }}
          {...props}
        />
        {error && <p className="mt-1.5 text-sm text-red-500">{error}</p>}
      </div>
    );
  },
);
Input.displayName = 'Input';
