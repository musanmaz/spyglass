import { ReactNode } from 'react';

interface TooltipProps {
  text: string;
  children: ReactNode;
}

export function Tooltip({ text, children }: TooltipProps) {
  return (
    <span className="relative group inline-flex">
      {children}
      <span className="pointer-events-none absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2.5 py-1 text-xs font-medium text-white bg-brand-primary-900 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
        {text}
      </span>
    </span>
  );
}
