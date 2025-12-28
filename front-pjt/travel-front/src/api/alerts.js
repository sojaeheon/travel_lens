import api from "./axios";

export const fetchTravelAlerts = () => api.get("/travel/alerts");
