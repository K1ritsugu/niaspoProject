import api from "./api";
export const getToken = () => localStorage.getItem("token");

export const getUserRole = async () => {
  const token = getToken();
  if (!token) return null;

  try {
    const response = await api.get("/users/users/me", {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data.role;
  } catch (error) {
    console.error("Failed to fetch user role:", error);
    return null;
  }
};

export const isAuthenticated = () => !!getToken();
