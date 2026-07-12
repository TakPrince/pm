export const getApiBaseUrl = () => {
  if (typeof window === "undefined") {
    return process.env.NEXT_PUBLIC_API_BASE_URL ?? "";
  }

  if (process.env.NEXT_PUBLIC_API_BASE_URL) {
    return process.env.NEXT_PUBLIC_API_BASE_URL;
  }

  if (process.env.NODE_ENV === "development") {
    return "http://127.0.0.1:8001";
  }

  return "";
};

export const buildApiUrl = (path: string) => {
  const baseUrl = getApiBaseUrl();
  return `${baseUrl}${path}`;
};
