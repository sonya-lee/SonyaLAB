<script setup>
import { onMounted, ref } from 'vue'

const modules = ref([])
const error = ref('')
const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

onMounted(async () => {
  try {
    const response = await fetch(`${apiBase}/api/modules`)
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    modules.value = await response.json()
  } catch (e) {
    error.value = `모듈 목록을 불러오지 못했습니다: ${e.message}`
  }
})
</script>

<template>
  <main class="page">
    <header class="hero">
      <p class="eyebrow">SONYA ECOSYSTEM</p>
      <h1>Sonya Lab</h1>
      <p>가격, 논문, 뉴스처럼 외부 정보를 찾고 비교하고 설명하는 개인 탐색 비서</p>
    </header>

    <p v-if="error" class="error">{{ error }}</p>

    <section class="grid">
      <article v-for="module in modules" :key="module.id" class="card">
        <h2>{{ module.name }}</h2>
        <p>{{ module.description }}</p>
        <button type="button">준비 중</button>
      </article>
    </section>
  </main>
</template>
