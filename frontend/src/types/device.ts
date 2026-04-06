export interface DeviceLocation {
  city: string;
  country: string;
  facility?: string;
  coordinates?: [number, number];
}

export interface DeviceNetwork {
  asn: number;
  as_name: string;
}

export interface Device {
  id: string;
  name: string;
  platform: string;
  location: DeviceLocation;
  supported_queries: string[];
  status: string;
  network: DeviceNetwork;
}

export interface DeviceListResponse {
  devices: Device[];
}
