import { Link } from "react-router-dom";
import { useContext } from "react";
import AuthContext from "../context/AuthContext";

function Navbar() {
  const { user, logout } = useContext(AuthContext);

  return (
    <nav>
      <h2>Ticket Booking</h2>

      <div>
        <Link to="/">Home</Link>
        <Link to="/my-bookings">My Bookings</Link>
        {user ? (
          <>
            <span>Hello, {user.email}</span>
            <button onClick={logout}>Logout</button>
          </>
        ) : (
          <Link to="/login">Login</Link>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
