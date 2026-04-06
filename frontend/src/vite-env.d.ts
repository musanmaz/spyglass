/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_APP_NAME?: string;
  readonly VITE_ORG_NAME?: string;
  readonly VITE_ASN?: string;
  readonly VITE_WEBSITE_URL?: string;
  readonly VITE_PEERINGDB_URL?: string;
  readonly VITE_LOGO_LIGHT?: string;
  readonly VITE_LOGO_DARK?: string;
  readonly VITE_WS_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
