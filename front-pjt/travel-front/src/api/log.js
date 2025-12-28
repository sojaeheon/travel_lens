import api from "@/api/axios";

/**
 * 사용자 행동 로그 전송
 * - 로그인/비로그인 모두 가능
 * - JWT는 axios interceptor에서 자동 처리
 */
export function sendLog({ event_type, country_code, value }) {
  return api.post("/interaction/logs/", {
    event_type,
    country_code,
    value,
  });
}
