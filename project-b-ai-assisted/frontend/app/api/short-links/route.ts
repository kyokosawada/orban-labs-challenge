import type { NextRequest } from "next/server";
import { forwardToApi } from "../shortener-api";

export const dynamic = "force-dynamic";

export async function POST(request: NextRequest) {
  return forwardToApi("/short-links", {
    method: "POST",
    body: await request.text(),
  });
}
