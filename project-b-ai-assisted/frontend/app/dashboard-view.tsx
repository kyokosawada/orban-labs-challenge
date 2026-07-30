"use client";

import { useCallback, useEffect, useState } from "react";
import {
  NETWORK_FAILURE,
  describeFailure,
  readJson,
  type ErrorEnvelope,
} from "./errors";
import type { ShortLink } from "./short-link";

const REFRESH_INTERVAL_MS = 5000;

function formatCreatedAt(value: string): string {
  const moment = new Date(value);
  return Number.isNaN(moment.getTime())
    ? value
    : moment.toLocaleString(undefined, {
        dateStyle: "short",
        timeStyle: "short",
      });
}

export default function DashboardView({
  publicBaseUrl,
  refreshSignal,
}: {
  publicBaseUrl: string;
  refreshSignal: number;
}) {
  const [shortLinks, setShortLinks] = useState<ShortLink[] | null>(null);
  const [failure, setFailure] = useState<ErrorEnvelope | null>(null);

  const load = useCallback(async () => {
    try {
      const response = await fetch("/api/short-links", { cache: "no-store" });
      const payload = await readJson(response);
      if (!response.ok) {
        setFailure(describeFailure(response.status, payload));
        return;
      }
      setShortLinks(payload as ShortLink[]);
      setFailure(null);
    } catch {
      setFailure(NETWORK_FAILURE);
    }
  }, []);

  useEffect(() => {
    void load();
    const timer = window.setInterval(() => void load(), REFRESH_INTERVAL_MS);
    return () => window.clearInterval(timer);
  }, [load, refreshSignal]);

  const loading = shortLinks === null && failure === null;

  return (
    <section className="dashboard card">
      <h2>Your short links</h2>
      <p className="dashboard-note">
        Clicks count every request that reached a Destination, including
        automated previews by chat applications. The figures refresh on their
        own every few seconds.
      </p>

      {failure ? (
        <div className="alert" role="alert">
          <p>{failure.message}</p>
          {shortLinks ? <p className="alert-note">Showing the last figures it managed to read.</p> : null}
        </div>
      ) : null}

      {loading ? (
        <p className="dashboard-state" aria-live="polite">
          Reading your short links...
        </p>
      ) : null}

      {shortLinks && shortLinks.length === 0 ? (
        <p className="dashboard-state">
          No short links yet. Shorten an address above and it appears here.
        </p>
      ) : null}

      {shortLinks && shortLinks.length > 0 ? (
        <table className="short-links">
          <colgroup>
            <col className="column-code" />
            <col />
            <col className="column-clicks" />
            <col className="column-created" />
          </colgroup>
          <thead>
            <tr>
              <th scope="col">Short link</th>
              <th scope="col">Destination</th>
              <th scope="col" className="numeric">
                Clicks
              </th>
              <th scope="col">Created</th>
            </tr>
          </thead>
          <tbody>
            {shortLinks.map((shortLink) => (
              <tr key={shortLink.short_code}>
                <td>
                  <a
                    className="short-code"
                    href={`${publicBaseUrl}/${shortLink.short_code}`}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {shortLink.short_code}
                  </a>
                </td>
                <td className="destination-cell" title={shortLink.destination}>
                  {shortLink.destination}
                </td>
                <td className="numeric">{shortLink.clicks}</td>
                <td className="created-cell">
                  <time dateTime={shortLink.created_at}>
                    {formatCreatedAt(shortLink.created_at)}
                  </time>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : null}
    </section>
  );
}
