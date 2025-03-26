import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getToken, getUserRole } from "../utils/auth";
import "../styles/Navbar.css";

function Navbar() {
  const [userRole, setUserRole] = useState(null);
  const isAuthenticated = !!getToken();

  useEffect(() => {
    const loadUserRole = async () => {
      const role = await getUserRole(); // Ожидаем завершения Promise
      setUserRole(role);
    };

    if (isAuthenticated) {
      loadUserRole();
    }
  }, [isAuthenticated]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    window.location.href = "/login";
  };

  return (
    <nav className="navbar">
      <h1>Food Service</h1>
      <div className="navbar-links">
        <Link to="/menu">Menu</Link>
        <Link to="/orders">Orders</Link>
        <Link to="/cart">Cart</Link>
        {isAuthenticated && userRole === "admin" && <Link to="/admin">Admin Panel</Link>}
        {isAuthenticated ? (
          <button onClick={handleLogout} className="navbar-button">
            Logout
          </button>
        ) : (
          <>
            <Link to="/login">
              <button className="navbar-button">Login</button>
            </Link>
            <Link to="/register">
              <button className="navbar-button">Register</button>
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
