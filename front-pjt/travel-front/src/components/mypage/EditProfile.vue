<template>
  <div class="wrap">
    <h2>비밀번호 변경</h2>
    <p class="desc">안전한 정보 보호를 위해 비밀번호를 변경해주세요.</p>

    <label class="field">
      <span>현재 비밀번호</span>
      <input type="password" />
    </label>

    <label class="field">
      <span>새 비밀번호</span>
      <input type="password" />
    </label>

    <label class="field">
      <span>새 비밀번호 확인</span>
      <input type="password" />
    </label>

    <button class="btn">변경사항 저장</button>
  </div>
</template>

<script setup>
</script>

<style scoped>
.wrap {
  padding: 40px 60px;
}
.desc {
  font-size: 13px;
  color: #777;
  margin-bottom: 24px;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 16px;
}
.field input {
  border: 1px solid #dedede;
  border-radius: 8px;
  padding: 10px 11px;
}
.btn {
  margin-top: 12px;
  padding: 10px 26px;
  border-radius: 8px;
  border: none;
  background: #222;
  color: #fff;
  cursor: pointer;
}
</style>
