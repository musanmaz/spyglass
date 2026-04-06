export const QUERY_TYPES = [
  { id: 'bgp_route', name: 'BGP Route', description: 'BGP routing table lookup' },
  { id: 'ping', name: 'Ping', description: 'ICMP ping test' },
  { id: 'traceroute', name: 'Traceroute', description: 'Traceroute path trace' },
] as const;

export const QUERY_TYPE_PLACEHOLDERS: Record<string, string> = {
  bgp_route: '203.0.113.0/24',
  ping: '203.0.113.1',
  traceroute: '203.0.113.1',
};
