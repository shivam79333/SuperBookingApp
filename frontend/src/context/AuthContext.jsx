import { createContext, useState, useEffect } from "react";
import { jwtDecode } from "jwt-decode";
import { loginUser as loginUserApi } from "../api/api";
import api from "../api/api";

const AuthContext = createContext();

export default AuthContext;

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const token = getCookie("access_token");
    if (token) {
      try {
        return jwtDecode(token);
      } catch (e) {
        console.error("Invalid token:", e);
        return null;
      }
    }
    return null;
  });

  const [token, setToken] = useState(() => getCookie("access_token"));

  useEffect(() => {
    const checkUserLoggedIn = () => {
      const token = getCookie("access_token");
      if (token) {
        try {
          const decodedUser = jwtDecode(token);
          setUser(decodedUser);
          setToken(token);
        } catch (e) {
          console.error("Invalid token:", e);
          setUser(null);
          setToken(null);
        }
      } else {
        setUser(null);
        setToken(null);
      }
    };
    checkUserLoggedIn();
  }, []);

  const login = async (email, password) => {
    const response = await loginUserApi({ email, password });
    if (response.status === 200) {
      const token = getCookie("access_token");
      if (token) {
        try {
          const decodedUser = jwtDecode(token);
          setUser(decodedUser);
          setToken(token);
        } catch (e) {
          console.error("Invalid token:", e);
        }
      }
    }
  };

  const logout = async () => {
    // The backend should handle clearing the cookie
    await api.post("/auth/logout/");
    setUser(null);
    setToken(null);
  };

  const contextData = {
    user,
    token,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={contextData}>{children}</AuthContext.Provider>
  );
};
