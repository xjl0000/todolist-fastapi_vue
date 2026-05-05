<template>
  <div class="app-shell">
    <!-- Ambient background -->
    <div class="bg-orb bg-orb-1"></div>
    <div class="bg-orb bg-orb-2"></div>

    <div class="main-container">
      <!-- Header -->
      <header class="app-header">
        <div class="logo">
          <span class="logo-icon">✦</span>
          <h1>每日待办</h1>
        </div>
        <p class="tagline">专注每一天</p>
      </header>

      <!-- Date Navigation -->
      <div class="date-section">
        <div class="month-label">{{ monthLabel }}</div>
        <div class="date-nav">
          <button class="nav-arrow" @click="shiftDates(-7)" aria-label="上一周">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>
          </button>
          <div class="date-strip">
            <button
              v-for="d in dateRange"
              :key="d.dateStr"
              class="date-cell"
              :class="{ active: d.dateStr === selectedDate, today: d.isToday }"
              @click="selectDate(d.dateStr)"
            >
              <span class="day-name">{{ d.dayName }}</span>
              <span class="day-num">{{ d.day }}</span>
              <span v-if="d.status" class="day-dot" :class="d.status"></span>
            </button>
          </div>
          <button class="nav-arrow" @click="shiftDates(7)" aria-label="下一周">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
          </button>
        </div>
        <button v-if="selectedDate !== todayStr" class="today-btn" @click="goToday">回到今天</button>
      </div>

      <!-- Day Status -->
      <div class="day-status" :class="{ 'all-done': dayAllDone && todos.length > 0 }">
        <div class="status-header">
          <h2>{{ formattedSelectedDate }}</h2>
          <Transition name="badge">
            <span v-if="dayAllDone && todos.length > 0" class="badge-done">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
              已全部完成
            </span>
          </Transition>
        </div>
        <div class="stats-row">
          <div class="stat"><span class="stat-val">{{ todos.length }}</span><span class="stat-label">总计</span></div>
          <div class="stat"><span class="stat-val done-val">{{ completedCount }}</span><span class="stat-label">已完成</span></div>
          <div class="stat"><span class="stat-val pend-val">{{ pendingCount }}</span><span class="stat-label">待完成</span></div>
        </div>
        <div class="progress-track" v-if="todos.length > 0">
          <div class="progress-fill" :style="{ width: progressPct + '%' }"></div>
        </div>
      </div>

      <!-- Add Todo -->
      <div class="add-section">
        <div class="add-form" :class="{ focused: inputFocused }">
          <input
            v-model="newTodo"
            placeholder="添加新任务..."
            @keyup.enter="handleAdd"
            @focus="inputFocused = true"
            @blur="inputFocused = false"
          />
          <button class="add-btn" @click="handleAdd" :disabled="!newTodo.trim()">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
          </button>
        </div>
      </div>

      <!-- Todo List -->
      <div class="todo-list">
        <TransitionGroup name="list">
          <div
            v-for="todo in todos"
            :key="todo.id"
            class="todo-item"
            :class="{ completed: todo.completed }"
          >
            <label class="cb-wrap">
              <input type="checkbox" v-model="todo.completed" @change="handleToggle(todo)" />
              <span class="cb-box">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
              </span>
            </label>
            <span class="todo-text">{{ todo.title }}</span>
            <button class="del-btn" @click="handleDelete(todo.id)" title="删除">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
            </button>
          </div>
        </TransitionGroup>
      </div>

      <!-- Empty State -->
      <div v-if="todos.length === 0 && !loading" class="empty-state">
        <div class="empty-icon">📋</div>
        <p class="empty-title">暂无任务</p>
        <p class="empty-sub">添加一个新任务开始今天的计划吧</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { getTodos, getDates, addTodo, updateTodo, deleteTodo } from '../api/todo'

const DAY_NAMES = ['日', '一', '二', '三', '四', '五', '六']

// --- State ---
const todos = ref([])
const dateStatuses = ref([])
const loading = ref(false)
const newTodo = ref('')
const inputFocused = ref(false)

// Date navigation
const todayStr = computed(() => fmtDate(new Date()))
const selectedDate = ref(fmtDate(new Date()))
const anchorDate = ref(new Date())

// --- Helpers ---
function fmtDate(d) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function addDays(d, n) {
  const r = new Date(d)
  r.setDate(r.getDate() + n)
  return r
}

// --- Computed ---
const dateRange = computed(() => {
  const center = anchorDate.value
  const result = []
  for (let i = -3; i <= 3; i++) {
    const d = addDays(center, i)
    const ds = fmtDate(d)
    const statusObj = dateStatuses.value.find(s => s.date === ds)
    let status = null
    if (statusObj) {
      status = statusObj.all_completed ? 'done' : 'pending'
    }
    result.push({
      dateStr: ds,
      day: d.getDate(),
      dayName: DAY_NAMES[d.getDay()],
      isToday: ds === todayStr.value,
      status
    })
  }
  return result
})

const monthLabel = computed(() => {
  const d = anchorDate.value
  return `${d.getFullYear()}年${d.getMonth() + 1}月`
})

const formattedSelectedDate = computed(() => {
  const parts = selectedDate.value.split('-')
  const d = new Date(+parts[0], +parts[1] - 1, +parts[2])
  const dayName = DAY_NAMES[d.getDay()]
  return `${+parts[1]}月${+parts[2]}日 星期${dayName}`
})

const completedCount = computed(() => todos.value.filter(t => t.completed).length)
const pendingCount = computed(() => todos.value.filter(t => !t.completed).length)
const dayAllDone = computed(() => todos.value.length > 0 && completedCount.value === todos.value.length)
const progressPct = computed(() => {
  if (todos.value.length === 0) return 0
  return Math.round((completedCount.value / todos.value.length) * 100)
})

// --- Actions ---
async function fetchTodos() {
  loading.value = true
  try {
    const res = await getTodos(selectedDate.value)
    todos.value = res.data
  } catch (err) {
    console.error('获取待办失败：', err)
  } finally {
    loading.value = false
  }
}

async function fetchDates() {
  try {
    const res = await getDates()
    dateStatuses.value = res.data
  } catch (err) {
    console.error('获取日期状态失败：', err)
  }
}

async function handleAdd() {
  const title = newTodo.value.trim()
  if (!title) return
  try {
    await addTodo({ title, date: selectedDate.value })
    newTodo.value = ''
    fetchTodos()
    fetchDates()
  } catch (err) {
    console.error('新增失败：', err)
    alert('新增待办失败')
  }
}

async function handleToggle(todo) {
  try {
    await updateTodo(todo.id, { title: todo.title, completed: todo.completed })
    fetchDates()
  } catch (err) {
    console.error('修改状态失败：', err)
    todo.completed = !todo.completed
  }
}

async function handleDelete(id) {
  if (!confirm('确定要删除这条待办吗？')) return
  try {
    await deleteTodo(id)
    fetchTodos()
    fetchDates()
  } catch (err) {
    console.error('删除失败：', err)
  }
}

function selectDate(dateStr) {
  selectedDate.value = dateStr
}

function shiftDates(days) {
  anchorDate.value = addDays(anchorDate.value, days)
}

function goToday() {
  selectedDate.value = fmtDate(new Date())
  anchorDate.value = new Date()
}

// --- Lifecycle ---
onMounted(() => {
  fetchTodos()
  fetchDates()
})

watch(selectedDate, () => {
  fetchTodos()
})
</script>

<style scoped>
/* ========== Shell & Background ========== */
.app-shell {
  width: 100%;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  position: relative;
}

.bg-orb {
  position: fixed;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.35;
  pointer-events: none;
  z-index: 0;
}
.bg-orb-1 {
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(139,124,247,0.3), transparent 70%);
  top: -150px; left: -100px;
}
.bg-orb-2 {
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(52,211,153,0.2), transparent 70%);
  bottom: -100px; right: -80px;
}

/* ========== Main Container ========== */
.main-container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 520px;
  padding: 2.5rem 0 3rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* ========== Header ========== */
.app-header { text-align: center; }
.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
}
.logo-icon {
  font-size: 1.5rem;
  background: linear-gradient(135deg, var(--accent), var(--success));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.logo h1 {
  font-size: 1.6rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  background: linear-gradient(135deg, var(--text-primary), var(--text-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.tagline {
  color: var(--text-tertiary);
  font-size: 0.85rem;
  margin-top: 0.3rem;
  font-weight: 400;
  letter-spacing: 0.08em;
}

/* ========== Date Navigation ========== */
.date-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.month-label {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--text-secondary);
  letter-spacing: 0.05em;
}

.date-nav {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
}

.nav-arrow {
  width: 36px; height: 36px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: var(--bg-card);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}
.nav-arrow:hover {
  background: var(--bg-card-hover);
  color: var(--text-primary);
  border-color: var(--border-hover);
}

.date-strip {
  display: flex;
  flex: 1;
  gap: 0.25rem;
}

.date-cell {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.15rem;
  padding: 0.5rem 0;
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  background: transparent;
  cursor: pointer;
  transition: all var(--transition-fast);
  color: var(--text-secondary);
  position: relative;
}
.date-cell:hover {
  background: var(--bg-card);
  color: var(--text-primary);
}
.date-cell.active {
  background: var(--accent-subtle);
  border-color: var(--border-active);
  color: var(--text-primary);
}
.date-cell.today .day-num {
  color: var(--accent);
  font-weight: 700;
}

.day-name {
  font-size: 0.65rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.day-num {
  font-size: 1.05rem;
  font-weight: 600;
  line-height: 1;
}
.day-dot {
  width: 5px; height: 5px;
  border-radius: 50%;
  margin-top: 2px;
}
.day-dot.pending { background: var(--accent); }
.day-dot.done { background: var(--success); }

.today-btn {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--accent);
  background: var(--accent-subtle);
  border: 1px solid var(--border-active);
  border-radius: 20px;
  padding: 0.3rem 1rem;
  cursor: pointer;
  transition: all var(--transition-fast);
}
.today-btn:hover {
  background: var(--accent);
  color: white;
}

/* ========== Day Status ========== */
.day-status {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.25rem 1.5rem;
  transition: all var(--transition-normal);
}
.day-status.all-done {
  border-color: rgba(52, 211, 153, 0.25);
  background: rgba(52, 211, 153, 0.04);
}

.status-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}
.status-header h2 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}

.badge-done {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--success);
  background: var(--success-subtle);
  padding: 0.25rem 0.7rem;
  border-radius: 20px;
  letter-spacing: 0.02em;
}

.badge-enter-active, .badge-leave-active { transition: all var(--transition-normal); }
.badge-enter-from, .badge-leave-to { opacity: 0; transform: scale(0.8); }

.stats-row {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1rem;
}
.stat {
  display: flex;
  align-items: baseline;
  gap: 0.4rem;
}
.stat-val {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--text-primary);
}
.done-val { color: var(--success); }
.pend-val { color: var(--accent); }
.stat-label {
  font-size: 0.7rem;
  color: var(--text-tertiary);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.progress-track {
  height: 4px;
  background: var(--border);
  border-radius: 4px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent), var(--success));
  border-radius: 4px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ========== Add Form ========== */
.add-section { margin-top: -0.25rem; }
.add-form {
  display: flex;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--bg-card);
  overflow: hidden;
  transition: all var(--transition-fast);
}
.add-form.focused {
  border-color: var(--border-active);
  box-shadow: 0 0 0 3px var(--accent-subtle), var(--shadow-glow);
}

.add-form input {
  flex: 1;
  padding: 0.85rem 1.15rem;
  border: none;
  outline: none;
  background: transparent;
  color: var(--text-primary);
  font-size: 0.9rem;
  font-family: var(--font);
}
.add-form input::placeholder { color: var(--text-tertiary); }

.add-btn {
  padding: 0 1.1rem;
  background: var(--accent);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}
.add-btn:hover:not(:disabled) { background: var(--accent-hover); }
.add-btn:disabled { opacity: 0.35; cursor: not-allowed; }

/* ========== Todo Items ========== */
.todo-list { display: flex; flex-direction: column; gap: 0.5rem; }

.todo-item {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.9rem 1.15rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}
.todo-item:hover {
  background: var(--bg-card-hover);
  border-color: var(--border-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}
.todo-item.completed { opacity: 0.55; }

/* Custom Checkbox */
.cb-wrap {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px; height: 22px;
  cursor: pointer;
  flex-shrink: 0;
}
.cb-wrap input { position: absolute; opacity: 0; width: 0; height: 0; }
.cb-box {
  width: 22px; height: 22px;
  border: 2px solid var(--border-hover);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
  color: transparent;
}
.cb-wrap input:checked ~ .cb-box {
  background: var(--accent);
  border-color: var(--accent);
  color: white;
}
.cb-wrap:hover .cb-box { border-color: var(--accent); }

.todo-text {
  flex: 1;
  font-size: 0.92rem;
  color: var(--text-primary);
  word-break: break-word;
  transition: all var(--transition-fast);
}
.completed .todo-text {
  text-decoration: line-through;
  color: var(--text-tertiary);
}

.del-btn {
  padding: 0.4rem;
  background: transparent;
  color: var(--text-tertiary);
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
  opacity: 0;
  flex-shrink: 0;
}
.todo-item:hover .del-btn { opacity: 1; }
.del-btn:hover {
  color: var(--danger);
  background: var(--danger-subtle);
  border-color: rgba(248, 113, 113, 0.15);
}

/* ========== Empty State ========== */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 3rem 1rem;
  gap: 0.5rem;
}
.empty-icon { font-size: 2.5rem; opacity: 0.6; margin-bottom: 0.5rem; }
.empty-title { font-size: 1rem; font-weight: 500; color: var(--text-secondary); }
.empty-sub { font-size: 0.8rem; color: var(--text-tertiary); }

/* ========== List Transitions ========== */
.list-enter-active { transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1); }
.list-leave-active { transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1); }
.list-enter-from { opacity: 0; transform: translateY(12px); }
.list-leave-to { opacity: 0; transform: translateX(-20px); }
.list-move { transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1); }

/* ========== Responsive ========== */
@media (max-width: 540px) {
  .main-container { padding: 1.5rem 1rem 2rem; }
  .day-name { font-size: 0.6rem; }
  .day-num { font-size: 0.9rem; }
  .stats-row { gap: 1rem; }
  .status-header { flex-direction: column; align-items: flex-start; gap: 0.5rem; }
}
</style>