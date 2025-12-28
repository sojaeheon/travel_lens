import api from "@/api/axios";

export function fetchPopularCountries(limit = 5, windowType = "hourly") {
  return api.get("/analytics/popular/", {
    params: {
      limit,
      window_type: windowType,
    },
  });
}

export function fetchPopularityMap(windowType = "hourly") {
  return api.get("/analytics/popularity/map/", {
    params: {
      window_type: windowType,
    },
  });
}
