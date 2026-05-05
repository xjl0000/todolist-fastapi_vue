import axios from 'axios'

// 创建axios实例，指向我们的后端接口
const api = axios.create({
  baseURL: '/api',
  timeout: 5000
})

// 获取指定日期的待办（默认今天）
export const getTodos = (date) => api.get('/todos', { params: { date } })

// 获取所有日期的完成状态
export const getDates = () => api.get('/dates')

// 新增待办
export const addTodo = (data) => api.post('/todos', data)

// 修改待办（内容+状态）
export const updateTodo = (id, data) => api.put(`/todos/${id}`, data)

// 删除待办
export const deleteTodo = (id) => api.delete(`/todos/${id}`)