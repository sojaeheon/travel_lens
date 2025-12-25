<template>
  <div class="map-container" ref="mapContainer">
    <SearchBar
      class="search-bar"
      v-model="keyword"
      @select="moveToCountry"
    />
    <div class="risk-legend">
      <div class="legend-nav">
        <span class="legend-arrow">&lt;</span>
        <span class="legend-title">위험</span>
        <span class="legend-arrow">&gt;</span>
      </div>
      <div class="legend-card">
        <div class="legend-item" v-for="item in RISK_LEGEND" :key="item.key">
          <span class="legend-dot" :style="{ background: RISK_COLOR[item.key] }"></span>
          <span>{{ item.label }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from "vue";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import SearchBar from "@/components/common/SearchBar.vue";
import { sendLog } from "@/api/log";
import { fetchFavoriteCountries } from "@/api/favorite";
import { fetchTravelAlerts } from "@/api/alerts";
import { useUserStore } from "@/store/user";

const emit = defineEmits(["country-click"]);
const mapContainer = ref(null);
const map = ref(null);
const keyword = ref("");
const mapLoaded = ref(false);
const favoriteIso2 = ref([]);
const favoriteMarkers = ref([]);
const userStore = useUserStore();

const continents = ref([]);
const subregions = ref([]);
const countryFeatures = ref([]);

const COUNTRY_CENTER = {
  KR: { lng: 127.7669, lat: 35.9078 },
  US: { lng: -98.5795, lat: 39.8283 },
  FR: { lng: 2.2137, lat: 46.2276 },
  JP: { lng: 138.2529, lat: 36.2048 }
};

const RISK_COLOR = {
  safe: "rgba(0, 160, 90, 0.45)",
  caution: "rgba(255, 140, 0, 0.45)",
  warning: "rgba(220, 53, 69, 0.5)"
};

const RISK_LEGEND = [
  { key: "safe", label: "안전" },
  { key: "caution", label: "주의" },
  { key: "warning", label: "경고" }
];

const riskIso2 = ref({
  safe: [],
  caution: [],
  warning: []
});

onMounted(async () => {
  continents.value = (await fetch("/continents.json").then(r => r.json())).continents;
  subregions.value = (await fetch("/subregions.json").then(r => r.json())).subregions;

  map.value = new maplibregl.Map({
    container: mapContainer.value,
    style: "travel-lens-style.json",
    center: [10, 20],
    zoom: 1.8
  });

  map.value.on("load", async () => {
    console.log("Map fully loaded");

    const countries = await fetch("/countries_csv.geojson").then(r => r.json());
    countryFeatures.value = countries.features || [];

    map.value.addSource("countries-labels", {
      type: "geojson",
      data: countries
    });

      const admin1 = await fetch("/admin1.geojson").then(r => r.json());
      map.value.addSource("admin1", {
        type: "geojson",
        data: admin1
      });

      map.value.addLayer({
        id: "country-favorites-fill",
        type: "fill",
        source: "countries-labels",
      paint: {
        "fill-color": "rgba(255, 105, 130, 0.35)",
        "fill-outline-color": "rgba(255, 105, 130, 0.6)"
      },
      filter: ["in", ["get", "iso2"], ["literal", []]]
    });

    map.value.addLayer({
      id: "country-labels-ko",
      type: "symbol",
      source: "countries-labels",
      minzoom: 1.7,
      maxzoom: 9,
      layout: {
        "text-field": ["get", "name_ko"],
        "text-size": 12,
        "text-font": ["Noto Sans Regular"],
        "text-allow-overlap": false
      },
      paint: {
        "text-color": "#ffffff",
        "text-halo-color": "rgba(0,0,0,0.55)",
        "text-halo-width": 1.4
      }
    });

    addRiskLayers();

    map.value.on("click", (e) => {
      const features = map.value.queryRenderedFeatures(e.point, {
        layers: ["country-labels-ko"]
      });

      if (!features.length) return;

      const props = features[0].properties;
      const iso2 = props.iso2;

      sendLog({
        event_type: "country_click",
        country_code: iso2
      });

      emit("country-click", {
        name_ko: props.name_ko,
        name_en: props.name_en,
        iso: iso2
      });
    });

    map.value.addControl(
      new maplibregl.NavigationControl(),
      "bottom-left"
    );

    mapLoaded.value = true;
    await refreshFavorites();
    await fetchRiskData();
  });
});

const refreshFavorites = async () => {
  if (!userStore.isAuth) {
    favoriteIso2.value = [];
    updateFavoriteLayer();
    return;
  }
  try {
    const res = await fetchFavoriteCountries();
    favoriteIso2.value = (res.data?.results || [])
      .map((item) => (item.iso2 || "").toUpperCase())
      .filter(Boolean);
  } catch {
    favoriteIso2.value = [];
  }
  updateFavoriteLayer();
  updateFavoriteMarkers();
};

const updateFavoriteLayer = () => {
  if (!mapLoaded.value || !map.value) return;
  const filter = ["in", ["get", "iso2"], ["literal", favoriteIso2.value]];
  map.value.setFilter("country-favorites-fill", filter);
};

const updateFavoriteMarkers = () => {
  if (!mapLoaded.value || !map.value) return;

  favoriteMarkers.value.forEach((marker) => marker.remove());
  favoriteMarkers.value = [];

  favoriteIso2.value.forEach((iso2) => {
    const feature = countryFeatures.value.find(
      (f) => (f?.properties?.iso2 || "").toUpperCase() === iso2
    );
    const center = getFeatureCenter(feature);
    if (!center) return;

    const el = document.createElement("div");
    el.textContent = "❤";
    el.style.width = "16px";
    el.style.height = "16px";
    el.style.borderRadius = "50%";
    el.style.display = "flex";
    el.style.alignItems = "center";
    el.style.justifyContent = "center";
    el.style.fontSize = "11px";
    el.style.lineHeight = "11px";
    el.style.color = "#ff4d6d";
    el.style.background = "rgba(255, 255, 255, 0.9)";
    el.style.border = "1px solid rgba(255, 77, 109, 0.5)";
    el.style.boxShadow = "0 2px 6px rgba(0, 0, 0, 0.25)";
    el.style.opacity = "0.85";
    el.style.pointerEvents = "none";

    const marker = new maplibregl.Marker({ element: el, offset: [12, -12] })
      .setLngLat(center)
      .addTo(map.value);

    favoriteMarkers.value.push(marker);
  });
};

const onFavoritesUpdated = () => {
  refreshFavorites();
};

watch(
  () => userStore.isAuth,
  () => {
    refreshFavorites();
  }
);

window.addEventListener("favorites-updated", onFavoritesUpdated);
onBeforeUnmount(() => {
  window.removeEventListener("favorites-updated", onFavoritesUpdated);
});

function normalizeRiskLevel(level) {
  if (level === "1") return "safe";
  if (level === "2") return "caution";
  if (level === "3" || level === "4") return "warning";
  return null;
}

async function fetchRiskData() {
  try {
    const res = await fetchTravelAlerts();
    const results = res.data?.results || [];
    const buckets = { safe: [], caution: [], warning: [] };

    results.forEach((item) => {
      const level = normalizeRiskLevel(String(item.alarm_level || ""));
      const iso2 = (item.iso2 || "").toUpperCase();
      if (!level || !iso2) return;
      if (!buckets[level].includes(iso2)) buckets[level].push(iso2);
    });

    riskIso2.value = buckets;
  } catch {
    riskIso2.value = { safe: [], caution: [], warning: [] };
  }

  applyRiskFilters();
}

function addRiskLayers() {
  if (!map.value) return;

      const beforeId = map.value.getLayer("countries-boundary")
        ? "countries-boundary"
        : undefined;

  const layers = [
    { id: "country-risk-safe", color: RISK_COLOR.safe },
    { id: "country-risk-caution", color: RISK_COLOR.caution },
    { id: "country-risk-warning", color: RISK_COLOR.warning }
  ];

  layers.forEach((layer) => {
    if (map.value.getLayer(layer.id)) return;
    map.value.addLayer(
      {
        id: layer.id,
        type: "fill",
            source: "admin1",
        paint: {
          "fill-color": layer.color,
          "fill-opacity": 0.6,
          "fill-outline-color": "rgba(255, 255, 255, 0.25)"
        },
            filter: ["in", ["get", "iso_a2"], ["literal", []]]
      },
      beforeId
    );
  });
}

function applyRiskFilters() {
  if (!mapLoaded.value || !map.value) return;

  map.value.setFilter(
        "country-risk-safe",
        ["in", ["get", "iso_a2"], ["literal", riskIso2.value.safe]]
      );
      map.value.setFilter(
        "country-risk-caution",
        ["in", ["get", "iso_a2"], ["literal", riskIso2.value.caution]]
      );
      map.value.setFilter(
        "country-risk-warning",
        ["in", ["get", "iso_a2"], ["literal", riskIso2.value.warning]]
      );
}

function moveToCountry(country) {
  const iso2 = (country?.iso2 || "").toUpperCase();
  if (!iso2) {
    alert("해당 국가를 찾을 수 없습니다.");
    return;
  }

  sendLog({
    event_type: "country_search_select",
    country_code: iso2
  });

  const feature = countryFeatures.value.find(
    (f) => (f?.properties?.iso2 || "").toUpperCase() === iso2
  );

  if (feature) {
    const bounds = getFeatureBounds(feature);
    if (bounds) {
      map.value.fitBounds(bounds, { padding: 40, duration: 800 });
    } else {
      const center = getFeatureCenter(feature);
      if (center) {
        map.value.flyTo({
          center,
          zoom: 4,
          speed: 0.8
        });
      }
    }
  } else if (COUNTRY_CENTER[iso2]) {
    map.value.flyTo({
      center: [COUNTRY_CENTER[iso2].lng, COUNTRY_CENTER[iso2].lat],
      zoom: 4,
      speed: 0.8
    });
  }

  emit("country-click", {
    name_ko: country?.name_ko || "",
    name_en: country?.name_en || "",
    iso: iso2
  });
}

function getFeatureBounds(feature) {
  const geom = feature?.geometry;
  if (!geom) return null;

  let coords = [];
  if (geom.type === "Polygon") {
    coords = geom.coordinates.flat();
  } else if (geom.type === "MultiPolygon") {
    coords = geom.coordinates.flat(2);
  } else {
    return null;
  }

  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;

  coords.forEach((c) => {
    const x = c[0];
    const y = c[1];
    if (x < minX) minX = x;
    if (y < minY) minY = y;
    if (x > maxX) maxX = x;
    if (y > maxY) maxY = y;
  });

  if (!Number.isFinite(minX)) return null;
  return [[minX, minY], [maxX, maxY]];
}

function getFeatureCenter(feature) {
  const geom = feature?.geometry;
  if (!geom) return null;
  if (geom.type === "Point" && Array.isArray(geom.coordinates)) {
    return geom.coordinates;
  }
  const bounds = getFeatureBounds(feature);
  if (!bounds) return null;
  const [[minX, minY], [maxX, maxY]] = bounds;
  return [(minX + maxX) / 2, (minY + maxY) / 2];
}
</script>

<style scoped>
.map-container {
  position: relative;
  flex: 1;
  height: calc(100vh - 72px);
}

.search-bar {
  position: absolute;
  top: 20px;
  left: 20px;
  width: 300px;
  z-index: 5;
}

.risk-legend {
  position: absolute;
  left: 70px;
  bottom: 20px;
  z-index: 6;
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-family: "Noto Sans", sans-serif;
}

.legend-nav {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: rgba(235, 235, 235, 0.95);
  border-radius: 14px;
  font-size: 12px;
  color: #333;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

.legend-title {
  font-weight: 600;
}

.legend-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 14px;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.18);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #1f1f1f;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.75);
}
</style>
