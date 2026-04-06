import { useState } from 'react';

interface OutputRendererProps {
  output: string;
}

export function OutputRenderer({ output }: OutputRendererProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(output);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative group">
      <pre
        className="font-mono text-[13px] leading-relaxed p-4 rounded-xl overflow-x-auto whitespace-pre-wrap break-words border"
        style={{
          backgroundColor: 'var(--lg-bg-tertiary)',
          borderColor: 'var(--lg-border)',
          color: 'var(--lg-text-primary)',
        }}
      >
        {output}
      </pre>
      <button
        onClick={handleCopy}
        className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity px-3 py-1.5 rounded-lg text-xs font-medium bg-brand-primary-800 text-white hover:bg-brand-primary-700"
      >
        {copied ? 'Copied' : 'Copy'}
      </button>
    </div>
  );
}
