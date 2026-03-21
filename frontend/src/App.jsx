import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./Page/Home";
import { ExperienceDetails } from "./Page/ExperienceDetails";
// import BookingPage from "./pages/BookingPage";
// import MyBookings from "./pages/MyBookings";
import Login from "./Page/Login";
import Navbar from "./components/Navbar";
import { AuthProvider } from "./context/AuthContext";

import LoginSignup from "./components/LoginSignup";
function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Navbar />

        <Routes>
          {/* <Route path="/" element={<Home />} /> */}
          <Route path="/experience/:id" element={<ExperienceDetails />} />
          {/* <Route path="/booking/:id" element={<BookingPage />} /> */}
          {/* <Route path="/my-bookings" element={<MyBookings />} /> */}
          <Route path="/login" element={<Login />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
