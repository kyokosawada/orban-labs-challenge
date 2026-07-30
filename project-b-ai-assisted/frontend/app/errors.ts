export type FieldError = {
  field: string;
  message: string;
};

export type ErrorEnvelope = {
  code: string;
  message: string;
  fields?: FieldError[];
};

export const NETWORK_FAILURE: ErrorEnvelope = {
  code: "network_error",
  message: "The interface could not reach its own server. Check your connection.",
};

export async function readJson(response: Response): Promise<unknown> {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

export function isErrorEnvelope(value: unknown): value is ErrorEnvelope {
  if (typeof value !== "object" || value === null) {
    return false;
  }
  const candidate = value as Record<string, unknown>;
  return (
    typeof candidate.code === "string" && typeof candidate.message === "string"
  );
}

export function describeFailure(status: number, payload: unknown): ErrorEnvelope {
  if (isErrorEnvelope(payload)) {
    return payload;
  }
  return {
    code: "unexpected_response",
    message: `The server answered with status ${status} and an unrecognised body.`,
  };
}
