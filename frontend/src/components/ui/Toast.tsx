import { useEffect, useState } from 'react';
import clsx from 'clsx';

interface ToastMessage {
  id: number;
  message: string;
  type: 'error' | 'warning' | 'info';
}

export function ToastContainer() {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  useEffect(() => {
    const handler = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      const toast: ToastMessage = {
        id: Date.now(),
        message: detail.message || 'An error occurred.',
        type: detail.type || 'error',
      };
      setToasts((prev) => [...prev, toast]);
      setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== toast.id)), 5000);
    };
    window.addEventListener('rate-limit-exceeded', handler);
    window.addEventListener('show-toast', handler);
    return () => {
      window.removeEventListener('rate-limit-exceeded', handler);
      window.removeEventListener('show-toast', handler);
    };
  }, []);

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={clsx(
            'animate-slide-up px-4 py-3 rounded-xl shadow-lg text-sm font-medium',
            toast.type === 'error' && 'bg-red-500 text-white',
            toast.type === 'warning' && 'bg-amber-500 text-white',
            toast.type === 'info' && 'bg-brand-primary-600 text-white',
          )}
        >
          {toast.message}
        </div>
      ))}
    </div>
  );
}
