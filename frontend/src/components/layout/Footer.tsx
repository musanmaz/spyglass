import { useState } from 'react';
import { TermsModal } from './TermsModal';
import { branding } from '../../lib/branding';

export function Footer() {
  const [showTerms, setShowTerms] = useState(false);

  return (
    <>
      <footer className="bg-brand-primary-950 text-brand-primary-300 py-6 mt-auto">
        <div className="max-w-6xl mx-auto px-4 flex flex-col md:flex-row items-center justify-between gap-3 text-sm">
          <span>&copy; {new Date().getFullYear()} {branding.copyright}</span>
          <div className="flex gap-4">
            <button onClick={() => setShowTerms(true)} className="hover:text-white transition-colors">
              Terms
            </button>
            {branding.peeringdbUrl && (
              <a href={branding.peeringdbUrl} target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">PeeringDB</a>
            )}
            {branding.websiteUrl && (
              <a href={branding.websiteUrl} target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">
                {(() => { try { return new URL(branding.websiteUrl).hostname; } catch { return branding.websiteUrl; } })()}
              </a>
            )}
          </div>
        </div>
      </footer>
      {showTerms && <TermsModal onClose={() => setShowTerms(false)} />}
    </>
  );
}
