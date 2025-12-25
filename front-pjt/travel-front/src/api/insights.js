import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
});

export const fetchCountryInsight = (iso2) =>
  api.get("/travel/insights/country", { params: { iso2 } });
