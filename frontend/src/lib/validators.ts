const IPV4_REGEX = /^(\d{1,3}\.){3}\d{1,3}(\/\d{1,2})?$/;
const IPV6_REGEX = /^[0-9a-fA-F:]+(::\S*)?(%\S+)?(\/\d{1,3})?$/;

export function isValidTarget(value: string, queryType: string): string | null {
  if (!value.trim()) return 'Please enter a target address';
  if (value.length > 255) return 'Target address is too long';

  if (['bgp_route', 'ping', 'traceroute'].includes(queryType)) {
    if (!IPV4_REGEX.test(value) && !IPV6_REGEX.test(value)) {
      return 'Please enter a valid IP address or prefix';
    }
  }

  return null;
}
