import type { FileData } from "../types/questionTypes";

export function isImageExt(filename: string) {
  const ext = filename.split(".").at(-1)?.toLowerCase();
  return ext === "png" || ext === "jpg" || ext === "jpeg";
}
export function getImageBase64FileData(f: FileData): string | null {
  if (f.content && f.mime_type?.startsWith("image")) {
    return `data:${f.mime_type};base64,${f.content}`;
  }
  return null;
}
