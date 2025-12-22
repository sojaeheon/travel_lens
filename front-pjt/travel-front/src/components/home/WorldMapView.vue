<template>
  <div class="map-container" ref="mapContainer">
    <SearchBar
      class="search-bar"
      v-model="keyword"
      @select="moveToCountry"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import SearchBar from "@/components/common/SearchBar.vue";
import { sendLog } from "@/api/log";   // ⭐ Django interaction/logs API

const emit = defineEmits(["country-click"]);
const mapContainer = ref(null);
const map = ref(null);
const keyword = ref("");

const continents = ref([]);
const subregions = ref([]);

// ⚠️ ISO2 기준으로 사용 (Django Country.iso2)
const COUNTRY_CENTER = {
  KR: { lng: 127.7669, lat: 35.9078 },
  US: { lng: -98.5795, lat: 39.8283 },
  FR: { lng: 2.2137, lat: 46.2276 },
  JP: { lng: 138.2529, lat: 36.2048 }
};

const RISK_POINTS = [
  { id: 1, lat: 37.5, lng: 127, level: "safe" },
  { id: 2, lat: 48.8, lng: 2.3, level: "danger" },
  { id: 3, lat: 40.7, lng: -73.9, level: "warning" }
];

const COLOR_MAP = {
  safe: "rgba(0, 200, 0, 0.4)",
  warning: "rgba(255, 200, 0, 0.4)",
  danger: "rgba(255, 0, 0, 0.5)"
};

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
    console.log("🌍 Map fully loaded");

    // ==========================
    // 1️⃣ 국가 한국어 라벨
    // ==========================
    const countries = await fetch("/countries_csv.geojson").then(r => r.json());

    map.value.addSource("countries-labels", {
      type: "geojson",
      data: countries
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

    // ==========================
    // 위험 지역 표시
    // ==========================
    drawRiskCircles();

    // ==========================
    // 국가 클릭 이벤트 (click)
    // ==========================
    map.value.on("click", (e) => {
      const features = map.value.queryRenderedFeatures(e.point, {
        layers: ["country-labels-ko"]
      });

      if (!features.length) return;

      const props = features[0].properties;
      const iso2 = props.iso2; // ⭐ 반드시 ISO2

      // 🔥 Django 로그 전송
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
  });
});

function drawRiskCircles() {
  RISK_POINTS.forEach(point => {
    const el = document.createElement("div");
    el.className = `risk-circle ${point.level}`;
    el.style.background = COLOR_MAP[point.level];

    new maplibregl.Marker({ element: el })
      .setLngLat([point.lng, point.lat])
      .addTo(map.value);
  });
}

// ==========================
// 검색 이동 (search)
// ==========================
function moveToCountry(name) {
  const code = Object.keys(COUNTRY_CENTER).find(c =>
    name.toUpperCase().includes(c)
  );

  if (!code) {
    alert("해당 국가를 찾을 수 없습니다.");
    return;
  }

  // 🔥 검색 로그
  sendLog({
    event_type: "country_search_select",
    country_code: code
  });

  map.value.flyTo({
    center: [COUNTRY_CENTER[code].lng, COUNTRY_CENTER[code].lat],
    zoom: 4,
    speed: 0.8
  });

  emit("country-click", {
    name_ko: name,
    name_en: name,
    iso: code
  });
}
</script>

<style scoped>
.map-container {
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

.risk-circle {
  width: 60px;
  height: 60px;
  border-radius: 50%;
}
</style>