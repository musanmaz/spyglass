export const branding = {
  appName: import.meta.env.VITE_APP_NAME || 'Spyglass',
  orgName: import.meta.env.VITE_ORG_NAME || '',
  asn: import.meta.env.VITE_ASN || '',
  websiteUrl: import.meta.env.VITE_WEBSITE_URL || '',
  peeringdbUrl: import.meta.env.VITE_PEERINGDB_URL || '',
  logoLight: import.meta.env.VITE_LOGO_LIGHT || '/images/logo-light.png',
  logoDark: import.meta.env.VITE_LOGO_DARK || '/images/logo-dark.png',

  get title(): string {
    if (this.orgName && this.asn) return `${this.orgName} (AS ${this.asn}) ${this.appName}`;
    if (this.orgName) return `${this.orgName} ${this.appName}`;
    return this.appName;
  },

  get copyright(): string {
    if (this.orgName && this.asn) return `${this.orgName} · AS${this.asn}`;
    if (this.orgName) return this.orgName;
    return this.appName;
  },
};
