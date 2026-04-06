import clsx from 'clsx';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'error' | 'warning';
  className?: string;
}

const variants = {
  default: 'bg-brand-primary-100 text-brand-primary-800 dark:bg-brand-primary-950 dark:text-brand-primary-300',
  success: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300',
  error: 'bg-red-50 text-red-700 dark:bg-red-950 dark:text-red-300',
  warning: 'bg-amber-50 text-amber-700 dark:bg-amber-950 dark:text-amber-300',
};

export function Badge({ children, variant = 'default', className }: BadgeProps) {
  return (
    <span className={clsx('inline-flex items-center text-xs font-medium px-3 py-1 rounded-lg', variants[variant], className)}>
      {children}
    </span>
  );
}
