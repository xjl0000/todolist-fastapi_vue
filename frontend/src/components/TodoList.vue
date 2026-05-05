<template>
  <div class="todo-container">
    <div class="header">
      <h1>待办清单</h1>
      <p class="subtitle">管理你的日常任务</p>
    </div>

    <!-- 新增待办区域 -->
    <div class="add-form">
      <div class="input-wrapper">
        <input
          v-model="newTodo"
          placeholder="输入新任务，按回车添加..."
          @keyup.enter="handleAdd"
          class="add-input"
        />
        <button @click="handleAdd" class="add-button">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
        </button>
      </div>
    </div>

    <!-- 任务统计 -->
    <div class="stats">
      <div class="stat-item">
        <span class="stat-number">{{ todos.length }}</span>
        <span class="stat-label">总数</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">{{ completedCount }}</span>
        <span class="stat-label">已完成</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">{{ pendingCount }}</span>
        <span class="stat-label">待完成</span>
      </div>
    </div>

    <!-- 待办列表 -->
    <div class="todo-list">
      <transition-group name="list" tag="div">
        <div
          v-for="todo in todos"
          :key="todo.id"
          class="todo-item"
          :class="{ completed: todo.completed }"
        >
          <label class="todo-checkbox">
            <input
              type="checkbox"
              v-model="todo.completed"
              @change="handleToggle(todo)"
            />
            <span class="checkmark"></span>
          </label>
          <span class="todo-title">{{ todo.title }}</span>
          <button class="delete-btn" @click="handleDelete(todo.id)" title="删除任务">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 6h18"></path>
              <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path>
              <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
            </svg>
          </button>
        </div>
      </transition-group>
    </div>

    <!-- 空状态提示 -->
    <div v-if="todos.length === 0" class="empty-state">
      <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="empty-icon">
        <circle cx="12" cy="12" r="10"></circle>
        <path d="M8 12h8"></path>
        <path d="M12 8v8"></path>
      </svg>
      <p>暂无待办事项</p>
      <p class="empty-subtext">添加一个新任务开始吧</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { getTodos, addTodo, updateTodo, deleteTodo } from '../api/todo'

// 响应式数据
const todos = ref([])
const newTodo = ref('')

// 计算已完成和待完成的任务数量
const completedCount = computed(() => {
  return todos.value.filter(todo => todo.completed).length
})

const pendingCount = computed(() => {
  return todos.value.filter(todo => !todo.completed).length
})

// 页面加载时获取所有待办
onMounted(() => {
  fetchTodos()
})

// 从后端获取待办列表
const fetchTodos = async () => {
  try {
    const res = await getTodos()
    todos.value = res.data
  } catch (err) {
    console.error('获取待办失败：', err)
    if (err.response) {
      // 服务器返回了错误状态码
      if (err.response.status === 404) {
        alert('后端服务接口不存在，请检查服务配置')
      } else if (err.response.status >= 500) {
        alert('后端服务内部错误，请稍后重试')
      } else {
        alert('网络请求失败，请检查网络连接')
      }
    } else if (err.request) {
      // 请求已发出但没有收到响应
      alert('无法连接到后端服务，请检查服务是否正常运行')
    } else {
      // 其他错误
      alert('发生未知错误，请刷新页面重试')
    }
  }
}

// 新增待办
const handleAdd = async () => {
  const title = newTodo.value.trim()
  if (!title) return

  try {
    await addTodo({ title })
    newTodo.value = ''
    fetchTodos() // 刷新列表
  } catch (err) {
    console.error('新增失败：', err)
    alert('新增待办失败')
  }
}

// 切换完成状态
const handleToggle = async (todo) => {
  try {
    await updateTodo(todo.id, {
      title: todo.title,
      completed: todo.completed
    })
  } catch (err) {
    console.error('修改状态失败：', err)
    todo.completed = !todo.completed // 失败回滚
    alert('修改状态失败')
  }
}

// 删除待办
const handleDelete = async (id) => {
  if (!confirm('确定要删除这条待办吗？')) return

  try {
    await deleteTodo(id)
    fetchTodos() // 刷新列表
  } catch (err) {
    console.error('删除失败：', err)
    alert('删除待办失败')
  }
}
</script>

<style scoped>
.todo-container {
  max-width: 640px;
  margin: 0 auto;
  padding: 2rem 1rem;
  font-family: var(--sans);
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  min-height: 600px;
  display: flex;
  flex-direction: column;
}

.header {
  text-align: center;
  margin-bottom: 2rem;
}

.header h1 {
  margin: 0 0 0.5rem 0;
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--text-h);
}

.subtitle {
  color: var(--text-light);
  margin: 0;
  font-size: 0.875rem;
}

.add-form {
  margin-bottom: 1.5rem;
}

.input-wrapper {
  display: flex;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  overflow: hidden;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.input-wrapper:focus-within {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-bg);
}

.add-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: none;
  outline: none;
  font-size: 1rem;
  background: transparent;
}

.add-input::placeholder {
  color: var(--text-light);
}

.add-button {
  padding: 0.75rem 1rem;
  background: var(--accent);
  color: white;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.add-button:hover {
  background: var(--accent-hover);
}

.stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: var(--border-light);
  border-radius: var(--radius-md);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-number {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-h);
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-light);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.todo-list {
  flex: 1;
  overflow-y: auto;
}

.todo-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: white;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  margin-bottom: 0.75rem;
  transition: all 0.2s ease;
  animation: fadeIn 0.3s ease;
}

.todo-item:hover {
  border-color: var(--accent-border);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.completed .todo-title {
  text-decoration: line-through;
  color: var(--text-light);
}

.todo-checkbox {
  position: relative;
  display: inline-block;
  width: 20px;
  height: 20px;
  cursor: pointer;
}

.todo-checkbox input {
  opacity: 0;
  width: 0;
  height: 0;
}

.checkmark {
  position: absolute;
  top: 0;
  left: 0;
  height: 20px;
  width: 20px;
  background-color: white;
  border: 1.5px solid var(--border);
  border-radius: 4px;
  transition: all 0.2s ease;
}

.todo-checkbox input:checked ~ .checkmark {
  background-color: var(--accent);
  border-color: var(--accent);
}

.checkmark:after {
  content: '';
  position: absolute;
  display: none;
}

.todo-checkbox input:checked ~ .checkmark:after {
  display: block;
}

.todo-checkbox .checkmark:after {
  left: 6px;
  top: 2px;
  width: 6px;
  height: 12px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.todo-title {
  flex: 1;
  font-size: 1rem;
  color: var(--text-h);
  word-break: break-word;
  padding-right: 0.5rem;
}

.delete-btn {
  padding: 0.5rem;
  background: transparent;
  color: var(--danger);
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.delete-btn:hover {
  background: rgba(239, 68, 68, 0.08);
  color: var(--danger-hover);
  border-color: rgba(239, 68, 68, 0.2);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  text-align: center;
  color: var(--text-light);
  flex: 1;
  gap: 0.75rem;
}

.empty-icon {
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-subtext {
  font-size: 0.875rem;
  color: var(--text-light);
}

/* 动画效果 */
.list-enter-active, .list-leave-active {
  transition: all 0.3s ease;
}

.list-enter-from, .list-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>