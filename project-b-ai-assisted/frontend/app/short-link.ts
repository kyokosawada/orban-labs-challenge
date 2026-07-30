export type ShortLink = {
  short_code: string;
  destination: string;
  created_at: string;
  expires_at: string | null;
  clicks: number;
};
