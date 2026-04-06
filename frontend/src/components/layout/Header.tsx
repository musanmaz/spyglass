import { ThemeToggle } from './ThemeToggle';
import { useTheme } from '../../hooks/useTheme';
import { branding } from '../../lib/branding';

export function Header() {
  const { isDark } = useTheme();

  return (
    <header className="sticky top-0 z-50 border-b" style={{ borderColor: 'var(--lg-border)', backgroundColor: 'var(--lg-bg-primary)' }}>
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <a href="/" className="flex items-center gap-3">
          <img
            src={isDark ? branding.logoDark : branding.logoLight}
            alt={branding.orgName || branding.appName}
            className="h-8"
          />
        </a>
        <ThemeToggle />
      </div>
    </header>
  );
}
