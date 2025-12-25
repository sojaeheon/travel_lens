import api from "./axios"; // 너 프로젝트 axios 인스턴스 경로에 맞춰서

export const fetchNewsByCountry = (iso2, q = "", page = 1, size = 10) => {
  return api.get("/search/news/", {
    params: { iso2, q, page, size },
  });
};

export const fetchBlogsByCountry = (iso2, q = "", page = 1, size = 10) => {
  return api.get("/search/blogs/", {
    params: { iso2, q, page, size },
  });
};

export const fetchCountrySuggestions = (q, size = 5) => {
  return api.get("/search/autosearch/", {
    params: { q, size },
  });
};

export const fetchCountries = (q, size = 10) => {
  return api.get("/search/countries/", {
    params: { q, size },
  });
};
