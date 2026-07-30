import type { NextRequest } from "next/server";
import { forwardToApi } from "../notes-api";

export const dynamic = "force-dynamic";

export async function GET() {
  return forwardToApi("/notes", { method: "GET" });
}

export async function POST(request: NextRequest) {
  return forwardToApi("/notes", {
    method: "POST",
    body: await request.text(),
  });
}
