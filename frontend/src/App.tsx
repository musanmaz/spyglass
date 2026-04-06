import { useEffect } from 'react';
import { Header } from './components/layout/Header';
import { Footer } from './components/layout/Footer';
import { QueryForm } from './components/query/QueryForm';
import { ResultsContainer } from './components/results/ResultsContainer';
import { ToastContainer } from './components/ui/Toast';
import { useQueryStore } from './store/queryStore';
import { branding } from './lib/branding';

export default function App() {
  const streamingStatus = useQueryStore((s) => s.streamingStatus);
  const setSupportedQueryTypes = useQueryStore((s) => s.setSupportedQueryTypes);

  useEffect(() => {
    const base = import.meta.env.VITE_WS_URL
      ? new URL(import.meta.env.VITE_WS_URL).origin.replace(/^ws/, 'http')
      : '';
    fetch(`${base}/api/v1/info`)
      .then((r) => r.json())
      .then((data) => {
        if (Array.isArray(data.supported_query_types)) {
          setSupportedQueryTypes(data.supported_query_types);
        }
      })
      .catch(() => {});
  }, [setSupportedQueryTypes]);

  return (
    <div className="min-h-screen flex flex-col" style={{ backgroundColor: 'var(--lg-bg-primary)' }}>
      <Header />
      <main className="flex-1">
        <section className="bg-brand-hero py-12 md:py-20 px-4">
          <div className="max-w-3xl mx-auto text-center mb-8">
            <h1 className="text-3xl md:text-5xl font-bold text-white tracking-tight mb-3">
              {branding.orgName || branding.appName}{' '}
              {branding.asn && <span className="font-normal opacity-80">(AS {branding.asn})</span>}{' '}
              {branding.orgName && branding.appName}
            </h1>
            <p className="text-brand-primary-200 text-lg">
              Network view from our perspective
            </p>
          </div>
          <div className="max-w-2xl mx-auto">
            <QueryForm />
          </div>
        </section>

        {streamingStatus !== 'idle' && (
          <section className="max-w-4xl mx-auto px-4 py-8">
            <ResultsContainer />
          </section>
        )}
      </main>
      <Footer />
      <ToastContainer />
    </div>
  );
}
