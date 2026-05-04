<template>
  <TodoList />
</template>

<script setup>
import TodoList from './components/TodoList.vue'
</script>

<style>
body {
  margin: 0;
  padding: 0;
  background-color: var(--bg);
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 1rem;
  font-family: var(--sans);
}
</style>