import clsx from 'clsx';
import { HTMLAttributes } from 'react';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  hoverable?: boolean;
}

export function Card({ hoverable = false, className, children, ...props }: CardProps) {
  return (
    <div
      className={clsx(
        'rounded-2xl p-6 border transition-all duration-200',
        'dark:bg-[rgba(26,14,48,0.7)] dark:backdrop-blur-xl',
        hoverable && 'hover:border-brand-primary-300 hover:shadow-brand-card dark:hover:border-brand-primary-700',
        className,
      )}
      style={{
        backgroundColor: 'var(--lg-bg-primary)',
        borderColor: 'var(--lg-border)',
      }}
      {...props}
    >
      {children}
    </div>
  );
}
