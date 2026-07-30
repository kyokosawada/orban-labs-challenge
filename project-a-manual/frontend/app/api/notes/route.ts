import type { NextRequest } from "next/server";
import { forwardToApi } from "../notes-api";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  return forwardToApi(`/notes${request.nextUrl.search}`, { method: "GET" });
}

export async function POST(request: NextRequest) {
  return forwardToApi("/notes", {
    method: "POST",
    body: await request.text(),
  });
}
