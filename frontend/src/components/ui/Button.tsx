import clsx from 'clsx';
import { ButtonHTMLAttributes, forwardRef } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', size = 'md', className, disabled, children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        disabled={disabled}
        className={clsx(
          'inline-flex items-center justify-center font-semibold rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-brand-primary-500/30',
          {
            'bg-brand-gradient text-white shadow-brand-button hover:shadow-brand-button-hover hover:-translate-y-0.5 active:translate-y-0 active:scale-[0.98]': variant === 'primary' && !disabled,
            'bg-gray-400 text-white cursor-not-allowed': variant === 'primary' && disabled,
            'border text-brand-primary-700 dark:text-brand-primary-300 hover:bg-brand-primary-50 dark:hover:bg-brand-primary-950': variant === 'secondary',
            'text-brand-primary-700 dark:text-brand-primary-300 hover:bg-brand-primary-50 dark:hover:bg-brand-primary-950': variant === 'ghost',
          },
          {
            'text-sm px-4 py-2': size === 'sm',
            'px-6 py-3': size === 'md',
            'text-lg px-8 py-4': size === 'lg',
          },
          className,
        )}
        style={variant === 'secondary' ? { borderColor: 'var(--lg-border)' } : undefined}
        {...props}
      >
        {children}
      </button>
    );
  },
);
Button.displayName = 'Button';
