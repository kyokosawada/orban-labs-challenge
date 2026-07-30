import { NextResponse } from "next/server";
import type { ErrorEnvelope } from "../errors";

const DEFAULT_API_URL = "http://127.0.0.1:8000";

function failureResponse(
  status: number,
  code: string,
  message: string,
): NextResponse<ErrorEnvelope> {
  return NextResponse.json({ code, message }, { status });
}

export async function forwardToApi(
  path: string,
  init: { method: string; body?: string },
): Promise<NextResponse> {
  const apiKey = process.env.SHORTENER_API_KEY;
  if (!apiKey) {
    return failureResponse(
      500,
      "configuration_error",
      "This server has no SHORTENER_API_KEY configured, so it cannot reach the URL Shortener API.",
    );
  }

  const baseUrl = process.env.SHORTENER_API_URL ?? DEFAULT_API_URL;
  let response: Response;
  try {
    response = await fetch(`${baseUrl}${path}`, {
      method: init.method,
      body: init.body,
      headers: {
        "X-API-Key": apiKey,
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });
  } catch {
    return failureResponse(
      502,
      "api_unreachable",
      `The URL Shortener API at ${baseUrl} did not answer. Check that it is running.`,
    );
  }

  const text = await response.text();
  return new NextResponse(text || null, {
    status: response.status,
    headers: { "Content-Type": "application/json" },
  });
}
