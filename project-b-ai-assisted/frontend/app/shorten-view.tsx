"use client";

import { useState } from "react";
import DashboardView from "./dashboard-view";
import {
  NETWORK_FAILURE,
  describeFailure,
  readJson,
  type ErrorEnvelope,
  type FieldError,
} from "./errors";
import type { ShortLink } from "./short-link";

const ATTACHED_FIELDS = new Set(["destination", "expires_at"]);

const COPY_FAILURE: ErrorEnvelope = {
  code: "copy_failed",
  message: "Your browser would not let the page copy that. Select it and copy by hand.",
};

function messageFor(failure: ErrorEnvelope, field: string): string | undefined {
  return failure.fields?.find((entry) => entry.field === field)?.message;
}

function unattachedFields(failure: ErrorEnvelope): FieldError[] {
  return (failure.fields ?? []).filter((entry) => !ATTACHED_FIELDS.has(entry.field));
}

function expiryPayload(entered: string): { expires_at?: string } {
  if (entered === "") {
    return {};
  }
  const chosen = new Date(entered);
  return {
    expires_at: Number.isNaN(chosen.getTime()) ? entered : chosen.toISOString(),
  };
}

function readableMoment(value: string): string {
  const moment = new Date(value);
  return Number.isNaN(moment.getTime()) ? value : moment.toLocaleString();
}

export default function ShortenView({
  publicBaseUrl,
}: {
  publicBaseUrl: string;
}) {
  const [destination, setDestination] = useState("");
  const [expiry, setExpiry] = useState("");
  const [shortLink, setShortLink] = useState<ShortLink | null>(null);
  const [failure, setFailure] = useState<ErrorEnvelope | null>(null);
  const [shortening, setShortening] = useState(false);
  const [copied, setCopied] = useState(false);
  const [mintedCount, setMintedCount] = useState(0);

  const shortUrl = shortLink ? `${publicBaseUrl}/${shortLink.short_code}` : null;

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setShortening(true);
    setCopied(false);
    try {
      const response = await fetch("/api/short-links", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ destination, ...expiryPayload(expiry) }),
      });
      const payload = await readJson(response);
      if (!response.ok) {
        setShortLink(null);
        setFailure(describeFailure(response.status, payload));
        return;
      }
      setShortLink(payload as ShortLink);
      setFailure(null);
      setDestination("");
      setExpiry("");
      setMintedCount((count) => count + 1);
    } catch {
      setShortLink(null);
      setFailure(NETWORK_FAILURE);
    } finally {
      setShortening(false);
    }
  }

  async function copy() {
    if (!shortUrl) {
      return;
    }
    try {
      await navigator.clipboard.writeText(shortUrl);
      setCopied(true);
      setFailure(null);
    } catch {
      setCopied(false);
      setFailure(COPY_FAILURE);
    }
  }

  const destinationError = failure ? messageFor(failure, "destination") : undefined;
  const expiryError = failure ? messageFor(failure, "expires_at") : undefined;
  const unattached = failure ? unattachedFields(failure) : [];
  const shownBesideAField = Boolean(destinationError || expiryError);
  const banner =
    failure && (unattached.length > 0 || !shownBesideAField) ? failure : null;

  return (
    <main className="page">
      <header>
        <h1>Short Links</h1>
        <p className="subtitle">
          Paste a long web address and get a short one you can actually share.
        </p>
      </header>

      {banner ? (
        <div className="alert" role="alert">
          <p>{banner.message}</p>
          {unattached.length > 0 ? (
            <ul>
              {unattached.map((entry) => (
                <li key={`${entry.field}-${entry.message}`}>
                  <code>{entry.field}</code>: {entry.message}
                </li>
              ))}
            </ul>
          ) : null}
        </div>
      ) : null}

      <form className="card" onSubmit={submit} noValidate>
        <div className="field">
          <label htmlFor="destination">Destination</label>
          <input
            id="destination"
            name="destination"
            type="url"
            inputMode="url"
            autoComplete="off"
            spellCheck={false}
            placeholder="https://example.com/a/genuinely/long/address"
            value={destination}
            onChange={(event) => setDestination(event.target.value)}
            aria-invalid={destinationError ? "true" : undefined}
            aria-describedby={destinationError ? "destination-error" : undefined}
          />
          {destinationError ? (
            <span className="field-error" id="destination-error" role="alert">
              {destinationError}
            </span>
          ) : null}
        </div>

        <div className="field">
          <label htmlFor="expires-at">Expiry</label>
          <input
            id="expires-at"
            name="expires-at"
            type="datetime-local"
            value={expiry}
            onChange={(event) => setExpiry(event.target.value)}
            aria-invalid={expiryError ? "true" : undefined}
            aria-describedby={expiryError ? "expiry-error" : "expiry-hint"}
          />
          {expiryError ? (
            <span className="field-error" id="expiry-error" role="alert">
              {expiryError}
            </span>
          ) : (
            <span className="field-hint" id="expiry-hint">
              Optional. Leave it empty and the link keeps working indefinitely.
            </span>
          )}
        </div>

        <button type="submit" disabled={shortening || destination.trim() === ""}>
          {shortening ? "Shortening..." : "Shorten"}
        </button>
      </form>

      {shortLink && shortUrl ? (
        <section className="result card" aria-live="polite">
          <h2>Your short link</h2>
          <div className="result-row">
            <a
              className="short-url"
              href={shortUrl}
              target="_blank"
              rel="noopener noreferrer"
            >
              {shortUrl}
            </a>
            <button type="button" className="secondary" onClick={copy}>
              {copied ? "Copied" : "Copy"}
            </button>
          </div>
          <p className="destination">
            <span className="destination-label">Goes to</span>
            {shortLink.destination}
          </p>
          {shortLink.expires_at ? (
            <p className="expiry">
              <span className="expiry-label">Stops working</span>
              {readableMoment(shortLink.expires_at)}
            </p>
          ) : null}
        </section>
      ) : null}

      <DashboardView publicBaseUrl={publicBaseUrl} mintedCount={mintedCount} />
    </main>
  );
}
