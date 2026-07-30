"use client";

import { useCallback, useEffect, useState } from "react";
import { describeFailure, type ErrorEnvelope, type FieldError } from "./errors";

type Note = {
  id: number;
  title: string;
  body: string;
  tags: string[];
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

const FIELDS_SHOWN_BESIDE_THEIR_INPUT = ["title", "body", "tags"];

function inputFor(entry: FieldError): string {
  return entry.field.split(".")[0];
}

function messageFor(failure: ErrorEnvelope, field: string): string | undefined {
  return failure.fields?.find((entry) => inputFor(entry) === field)?.message;
}

function unattachedFields(failure: ErrorEnvelope): FieldError[] {
  return (failure.fields ?? []).filter(
    (entry) => !FIELDS_SHOWN_BESIDE_THEIR_INPUT.includes(inputFor(entry)),
  );
}

function TagButton({
  label,
  pressed,
  onPress,
}: {
  label: string;
  pressed: boolean;
  onPress: () => void;
}) {
  return (
    <button type="button" className="tag" aria-pressed={pressed} onClick={onPress}>
      {label}
    </button>
  );
}

function tagsTyped(value: string): string[] {
  return value
    .split(",")
    .map((tag) => tag.trim())
    .filter((tag) => tag.length > 0);
}

function formatTimestamp(value: string): string {
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime())
    ? value
    : parsed.toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}

const SEARCH_SETTLES_AFTER_MS = 200;

function listingQuery(keyword: string, tag: string | null): string {
  const parameters = new URLSearchParams();
  if (keyword) {
    parameters.set("q", keyword);
  }
  if (tag) {
    parameters.set("tag", tag);
  }
  const query = parameters.toString();
  return query ? `?${query}` : "";
}

function nothingFound(keyword: string, tag: string | null): string {
  if (keyword && tag) {
    return `Nothing tagged ${tag} mentions ${keyword}.`;
  }
  if (keyword) {
    return `Nothing mentions ${keyword}.`;
  }
  if (tag) {
    return `Nothing tagged ${tag}.`;
  }
  return "Nothing written yet.";
}

export default function NotesView() {
  const [notes, setNotes] = useState<Note[] | null>(null);
  const [tagsInUse, setTagsInUse] = useState<string[]>([]);
  const [filterTag, setFilterTag] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [keyword, setKeyword] = useState("");
  const [listSettled, setListSettled] = useState(false);
  const [failure, setFailure] = useState<ErrorEnvelope | null>(null);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [tags, setTags] = useState("");
  const [saving, setSaving] = useState(false);

  const loadNotes = useCallback(async () => {
    const query = listingQuery(keyword, filterTag);
    try {
      const response = await fetch(`/api/notes${query}`);
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
  }, [filterTag, keyword]);

  const loadTagsInUse = useCallback(async () => {
    try {
      const response = await fetch("/api/tags");
      const payload = await readJson(response);
      if (!response.ok) {
        setFailure(describeFailure(response.status, payload));
        return;
      }
      setTagsInUse(payload as string[]);
    } catch {
      setFailure(NETWORK_FAILURE);
    }
  }, []);

  useEffect(() => {
    const settling = setTimeout(
      () => setKeyword(search.trim()),
      SEARCH_SETTLES_AFTER_MS,
    );
    return () => clearTimeout(settling);
  }, [search]);

  useEffect(() => {
    void loadNotes();
  }, [loadNotes]);

  useEffect(() => {
    void loadTagsInUse();
  }, [loadTagsInUse]);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setSaving(true);
    try {
      const response = await fetch("/api/notes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, body, tags: tagsTyped(tags) }),
      });
      const payload = await readJson(response);
      if (!response.ok) {
        setFailure(describeFailure(response.status, payload));
        return;
      }
      setFailure(null);
      setTitle("");
      setBody("");
      setTags("");
      await Promise.all([loadNotes(), loadTagsInUse()]);
    } catch {
      setFailure(NETWORK_FAILURE);
    } finally {
      setSaving(false);
    }
  }

  const titleError = failure ? messageFor(failure, "title") : undefined;
  const bodyError = failure ? messageFor(failure, "body") : undefined;
  const tagsError = failure ? messageFor(failure, "tags") : undefined;

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

        <div className="field">
          <label htmlFor="tags">Tags</label>
          <input
            id="tags"
            name="tags"
            value={tags}
            onChange={(event) => setTags(event.target.value)}
            placeholder="work, invoices"
            aria-invalid={tagsError ? "true" : undefined}
            aria-describedby={tagsError ? "tags-error" : "tags-hint"}
          />
          {tagsError ? (
            <span className="field-error" id="tags-error">
              {tagsError}
            </span>
          ) : (
            <span className="field-hint" id="tags-hint">
              Separate them with commas. Capitalisation is not kept.
            </span>
          )}
        </div>

        <button type="submit" disabled={saving}>
          {saving ? "Saving..." : "Save note"}
        </button>
      </form>

      <h2>Your notes</h2>

      <div className="field search">
        <label htmlFor="search">Search</label>
        <input
          id="search"
          name="search"
          type="search"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="A word from the note"
        />
      </div>

      {tagsInUse.length > 0 || filterTag !== null ? (
        <div className="filters" role="group" aria-label="Filter by tag">
          <TagButton
            label="All"
            pressed={filterTag === null}
            onPress={() => setFilterTag(null)}
          />
          {tagsInUse.map((tag) => (
            <TagButton
              key={tag}
              label={tag}
              pressed={filterTag === tag}
              onPress={() => setFilterTag(filterTag === tag ? null : tag)}
            />
          ))}
        </div>
      ) : null}

      {!listSettled ? (
        <p className="empty">Loading.</p>
      ) : notes === null ? (
        <p className="empty">Your notes could not be loaded.</p>
      ) : notes.length === 0 ? (
        <p className="empty">{nothingFound(keyword, filterTag)}</p>
      ) : (
        <ul className="notes">
          {notes.map((note) => (
            <li className="card" key={note.id}>
              <h3>{note.title}</h3>
              {note.body ? <p>{note.body}</p> : null}
              {note.tags.length > 0 ? (
                <div className="note-tags">
                  {note.tags.map((tag) => (
                    <TagButton
                      key={tag}
                      label={tag}
                      pressed={filterTag === tag}
                      onPress={() => setFilterTag(filterTag === tag ? null : tag)}
                    />
                  ))}
                </div>
              ) : null}
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
