import ShortenView from "./shorten-view";

const DEFAULT_PUBLIC_BASE_URL = "http://127.0.0.1:8000";

export const dynamic = "force-dynamic";

export default function Page() {
  const configured =
    process.env.SHORTENER_PUBLIC_BASE_URL ??
    process.env.SHORTENER_API_URL ??
    DEFAULT_PUBLIC_BASE_URL;

  return <ShortenView publicBaseUrl={configured.replace(/\/+$/, "")} />;
}
