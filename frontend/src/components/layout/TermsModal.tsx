import { useEffect } from 'react';
import { branding } from '../../lib/branding';

interface TermsModalProps {
  onClose: () => void;
}

export function TermsModal({ onClose }: TermsModalProps) {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" />
      <div
        className="relative w-full max-w-lg rounded-2xl p-6 shadow-2xl border"
        style={{
          backgroundColor: 'var(--lg-bg-primary)',
          borderColor: 'var(--lg-border)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-semibold" style={{ color: 'var(--lg-text-primary)' }}>
            Terms of Use
          </h2>
          <button
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-brand-primary-100 dark:hover:bg-brand-primary-900/40 transition-colors"
            style={{ color: 'var(--lg-text-muted)' }}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <p className="text-sm leading-relaxed" style={{ color: 'var(--lg-text-secondary)' }}>
          By using {branding.title}, you agree to be bound by the following terms of use:
        </p>
        <p className="text-sm leading-relaxed mt-3" style={{ color: 'var(--lg-text-secondary)' }}>
          All queries executed on this page are logged for analysis and troubleshooting. Users are prohibited from automating queries, or attempting to process queries in bulk. This service is provided on a best effort basis, and {branding.orgName || 'the operator'} makes no availability or performance warranties or guarantees whatsoever.
        </p>
        <div className="mt-6 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl text-sm font-medium bg-brand-gradient text-white shadow-brand-button hover:opacity-90 transition-opacity"
          >
            OK
          </button>
        </div>
      </div>
    </div>
  );
}
