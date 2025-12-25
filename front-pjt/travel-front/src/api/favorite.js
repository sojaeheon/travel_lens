// api/favorite.js
import axios from "@/api/axios";

export const fetchFavoriteStatus = (iso2) => {
  return axios.get(`interaction/countries/${iso2}/favorite/`);
};

export const fetchFavoriteCountries = () => {
  return axios.get("interaction/favorites/");
};
