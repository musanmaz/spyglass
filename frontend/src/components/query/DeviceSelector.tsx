import { useDevices } from '../../hooks/useDevices';
import { useQueryStore } from '../../store/queryStore';

export function DeviceSelector() {
  const { data: devices, isLoading } = useDevices();
  const selectedDevices = useQueryStore((s) => s.selectedDevices);
  const setSelectedDevices = useQueryStore((s) => s.setSelectedDevices);

  const toggleDevice = (id: string) => {
    if (selectedDevices.includes(id)) {
      setSelectedDevices(selectedDevices.filter((d) => d !== id));
    } else if (selectedDevices.length < 5) {
      setSelectedDevices([...selectedDevices, id]);
    }
  };

  if (isLoading) {
    return <div className="text-sm" style={{ color: 'var(--lg-text-muted)' }}>Loading devices...</div>;
  }

  if (!devices?.length) {
    return <div className="text-sm" style={{ color: 'var(--lg-text-muted)' }}>No devices available</div>;
  }

  return (
    <div className="flex flex-wrap gap-2">
      {devices.map((device) => (
        <button
          key={device.id}
          onClick={() => toggleDevice(device.id)}
          className={`px-3 py-2 rounded-xl text-sm transition-all duration-200 ${
            selectedDevices.includes(device.id)
              ? 'bg-brand-primary-800 text-white dark:bg-brand-primary-700'
              : 'border hover:border-brand-primary-300 dark:hover:border-brand-primary-700'
          }`}
          style={!selectedDevices.includes(device.id) ? { borderColor: 'var(--lg-border)', color: 'var(--lg-text-secondary)', backgroundColor: 'var(--lg-bg-secondary)' } : undefined}
        >
          <span className="font-medium">{device.name}</span>
          <span className="ml-1.5 opacity-60">{device.location.city}</span>
        </button>
      ))}
    </div>
  );
}
