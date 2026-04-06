import { useQuery } from '@tanstack/react-query';
import api from '../lib/api';
import type { Device, DeviceListResponse } from '../types/device';

export function useDevices() {
  return useQuery<Device[]>({
    queryKey: ['devices'],
    queryFn: async () => {
      const res = await api.get<DeviceListResponse>('/v1/devices');
      return res.data.devices;
    },
    staleTime: 60_000,
  });
}
