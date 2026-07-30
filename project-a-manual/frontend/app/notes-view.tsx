"use client";

import { useCallback, useEffect, useState } from "react";
import { describeFailure, type ErrorEnvelope, type FieldError } from "./errors";

type Note = {
  id: number;
  title: string;
  body: string;
  created_at: string;
  updated_at: string;
};

const NETWORK_FAILURE: ErrorEnvelope = {
  code: "network_error",
  message: "The interface could not reach its own server. Check your connection.",
};

async function readJson(response: Response): Promise<unknown> {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

const FIELDS_SHOWN_BESIDE_THEIR_INPUT = ["title", "body"];

function messageFor(failure: ErrorEnvelope, field: string): string | undefined {
  return failure.fields?.find((entry) => entry.field === field)?.message;
}

function unattachedFields(failure: ErrorEnvelope): FieldError[] {
  return (failure.fields ?? []).filter(
    (entry) => !FIELDS_SHOWN_BESIDE_THEIR_INPUT.includes(entry.field),
  );
}

function formatTimestamp(value: string): string {
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime())
    ? value
    : parsed.toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}

export default function NotesView() {
  const [notes, setNotes] = useState<Note[] | null>(null);
  const [listSettled, setListSettled] = useState(false);
  const [failure, setFailure] = useState<ErrorEnvelope | null>(null);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [saving, setSaving] = useState(false);

  const loadNotes = useCallback(async () => {
    try {
      const response = await fetch("/api/notes");
      const payload = await readJson(response);
      if (!response.ok) {
        setNotes(null);
        setFailure(describeFailure(response.status, payload));
        return;
      }
      setNotes(payload as Note[]);
      setFailure(null);
    } catch {
      setNotes(null);
      setFailure(NETWORK_FAILURE);
    } finally {
      setListSettled(true);
    }
  }, []);

  useEffect(() => {
    void loadNotes();
  }, [loadNotes]);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setSaving(true);
    try {
      const response = await fetch("/api/notes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, body }),
      });
      const payload = await readJson(response);
      if (!response.ok) {
        setFailure(describeFailure(response.status, payload));
        return;
      }
      setFailure(null);
      setTitle("");
      setBody("");
      await loadNotes();
    } catch {
      setFailure(NETWORK_FAILURE);
    } finally {
      setSaving(false);
    }
  }

  const titleError = failure ? messageFor(failure, "title") : undefined;
  const bodyError = failure ? messageFor(failure, "body") : undefined;

  return (
    <main className="page">
      <header>
        <h1>Notes</h1>
        <p className="subtitle">Write something down before you forget it.</p>
      </header>

      {failure ? (
        <div className="alert" role="alert">
          <p>{failure.message}</p>
          {unattachedFields(failure).length > 0 ? (
            <ul>
              {unattachedFields(failure).map((entry) => (
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
          <label htmlFor="title">Title</label>
          <input
            id="title"
            name="title"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            aria-invalid={titleError ? "true" : undefined}
            aria-describedby={titleError ? "title-error" : undefined}
          />
          {titleError ? (
            <span className="field-error" id="title-error">
              {titleError}
            </span>
          ) : null}
        </div>

        <div className="field">
          <label htmlFor="body">Body</label>
          <textarea
            id="body"
            name="body"
            value={body}
            onChange={(event) => setBody(event.target.value)}
            aria-invalid={bodyError ? "true" : undefined}
            aria-describedby={bodyError ? "body-error" : undefined}
          />
          {bodyError ? (
            <span className="field-error" id="body-error">
              {bodyError}
            </span>
          ) : null}
        </div>

        <button type="submit" disabled={saving}>
          {saving ? "Saving..." : "Save note"}
        </button>
      </form>

      <h2>Your notes</h2>
      {!listSettled ? (
        <p className="empty">Loading.</p>
      ) : notes === null ? (
        <p className="empty">Your notes could not be loaded.</p>
      ) : notes.length === 0 ? (
        <p className="empty">Nothing written yet.</p>
      ) : (
        <ul className="notes">
          {notes.map((note) => (
            <li className="card" key={note.id}>
              <h3>{note.title}</h3>
              {note.body ? <p>{note.body}</p> : null}
              <span className="timestamp">
                Written {formatTimestamp(note.created_at)}
              </span>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
