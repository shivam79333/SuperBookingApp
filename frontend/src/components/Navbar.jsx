import { Link } from "react-router-dom";

function Navbar() {
  return (
    <nav>
      <h2>Ticket Booking</h2>

      <div>
        <Link to="/">Home</Link>
        <Link to="/my-bookings">My Bookings</Link>
        <Link to="/login">Login</Link>
      </div>
    </nav>
  );
}

export default Navbar;