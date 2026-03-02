import { apiClient } from "../apiClient";

export type UserData = {
  email: string;
};

export const authService = {
  login: (credentials: object) => apiClient.post<any>("/token/", credentials),
  register: (userData: object) =>
    apiClient.post<any>("/accounts/register/", userData),
  getCurrentUser: () => apiClient.get<UserData>("/accounts/current_user/"),
};
