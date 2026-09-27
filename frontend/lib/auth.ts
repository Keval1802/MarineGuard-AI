export const getAuthToken = (): string => {
  if (typeof window === "undefined") return "Bearer dev-admin-token";
  return localStorage.getItem("marineguard_token") || "Bearer dev-admin-token";
};

export const setAuthToken = (token: string) => {
  if (typeof window !== "undefined") {
    localStorage.setItem("marineguard_token", token.startsWith("Bearer ") ? token : `Bearer ${token}`);
  }
};

export const clearAuthToken = () => {
  if (typeof window !== "undefined") {
    localStorage.removeItem("marineguard_token");
  }
};
