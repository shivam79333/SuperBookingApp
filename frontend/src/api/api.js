import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:5000/api",
});

export const getExperiences = () => API.get("/experiences");

export const getExperience = (id) =>
  API.get(`/experiences/${id}`);

export const createBooking = (data) =>
  API.post("/bookings", data);

export const getBookings = (userId) =>
  API.get(`/bookings/user/${userId}`);

export const loginUser = (data) =>
  API.post("/auth/login", data);

export default API;