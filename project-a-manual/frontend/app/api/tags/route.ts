import { forwardToApi } from "../notes-api";

export const dynamic = "force-dynamic";

export async function GET() {
  return forwardToApi("/tags", { method: "GET" });
}
