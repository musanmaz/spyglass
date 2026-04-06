import clsx from 'clsx';
import { SelectHTMLAttributes, forwardRef } from 'react';

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  options: { value: string; label: string }[];
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ options, className, ...props }, ref) => {
    return (
      <select
        ref={ref}
        className={clsx(
          'w-full px-4 py-3 rounded-xl text-[15px] transition-all duration-200 outline-none appearance-none cursor-pointer border focus:border-brand-primary-500 focus:shadow-brand-glow',
          className,
        )}
        style={{
          backgroundColor: 'var(--lg-bg-secondary)',
          borderColor: 'var(--lg-border)',
          color: 'var(--lg-text-primary)',
        }}
        {...props}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>
    );
  },
);
Select.displayName = 'Select';
