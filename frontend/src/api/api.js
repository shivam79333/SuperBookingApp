import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
  withCredentials: true,
});

api.interceptors.request.use(
  async (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        await api.post("/auth/refresh/");
        return api(originalRequest);
      } catch (err) {
        alert(err);
        store.dispatch(logoutUser());
        window.location.href = "/login";
        return Promise.reject(err);
      }
    }
    return Promise.reject(error);
  },
);

export const getExperiences = () => api.get("/experiences");
export const getExperience = (id) => api.get(`/experiences/${id}`);
export const createBooking = (data) => api.post("/bookings", data);
export const getBookings = (userId) => api.get(`/bookings/user/${userId}`);
export const loginUser = (data) => api.post("/auth/login", data);
export default api;
