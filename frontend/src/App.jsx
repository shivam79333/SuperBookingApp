import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import ExperienceDetails from "./pages/ExperienceDetails";
import BookingPage from "./pages/BookingPage";
import MyBookings from "./pages/MyBookings";
import Login from "./pages/Login";
import Navbar from "./components/Navbar";

function App() {
  return (
    <BrowserRouter>
      <Navbar />

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/experience/:id" element={<ExperienceDetails />} />
        <Route path="/booking/:id" element={<BookingPage />} />
        <Route path="/my-bookings" element={<MyBookings />} />
        <Route path="/login" element={<Login />} />
      </Routes>

    </BrowserRouter>
  );
}

export default App;