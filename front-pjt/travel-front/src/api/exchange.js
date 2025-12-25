import api from "@/api/axios";

export function fetchExchangeRates(limit = 10) {
  return api.get("/travel/exchange", {
    params: { limit },
  });
}
