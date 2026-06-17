import React, { createContext, useContext, useState, useEffect } from "react";
import { userAPI } from "../api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const savedUser = localStorage.getItem("user");
    if (token && savedUser) {
      try {
        setUser((u => ({...u, role: u.role?.toLowerCase() }))(JSON.parse(savedUser)));
      } catch {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
      }
    }
    setLoading(false);
  }, []);

const login = (token, userData) => {
  const normalized = { ...userData, role: userData.role?.toLowerCase() || userData.role };
  localStorage.setItem("token", token);
  localStorage.setItem("user", JSON.stringify(normalized));
  setUser(normalized);
};

const logout = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  setUser(null);
};

const updateUser = (data) => {
  const updated = { ...user, ...data };
  updated.role = updated.role?.toLowerCase() || updated.role;
  localStorage.setItem("user", JSON.stringify(updated));
  setUser(updated);
};

  return (
    <AuthContext.Provider value={{ user, login, logout, updateUser, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}


