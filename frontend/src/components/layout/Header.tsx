import { ThemeToggle } from './ThemeToggle';
import { branding } from '../../lib/branding';

export function Header() {
  return (
    <header className="sticky top-0 z-50 border-b" style={{ borderColor: 'var(--lg-border)', backgroundColor: 'var(--lg-bg-primary)' }}>
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <a href="/" className="text-lg font-semibold" style={{ color: 'var(--lg-text-primary)' }}>
          {branding.appName}
        </a>
        <ThemeToggle />
      </div>
    </header>
  );
}
