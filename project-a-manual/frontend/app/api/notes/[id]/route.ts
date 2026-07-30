import type { NextRequest } from "next/server";
import { forwardToApi } from "../../notes-api";

export const dynamic = "force-dynamic";

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;
  return forwardToApi(`/notes/${encodeURIComponent(id)}`, {
    method: "PUT",
    body: await request.text(),
  });
}
