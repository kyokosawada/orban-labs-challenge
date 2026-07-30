export type FieldError = {
  field: string;
  message: string;
};

export type ErrorEnvelope = {
  code: string;
  message: string;
  fields?: FieldError[];
};

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
