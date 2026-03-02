const BASE_URL = "http://100.105.194.90:8000/api";

async function request<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {
  const token = localStorage.getItem("access_token");

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  // В fetch ошибки 400, 401, 500 не вызывают catch автоматически.
  // Нужно проверять response.ok вручную.
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Server error: ${response.status}`);
  }

  return response.json();
}

export const apiClient = {
  get: <T>(url: string) => request<T>(url, { method: "GET" }),
  post: <T>(url: string, body: any) =>
    request<T>(url, {
      method: "POST",
      body: JSON.stringify(body),
    }),
  delete: (url: string) => request(url, { method: "DELETE" }),
};
