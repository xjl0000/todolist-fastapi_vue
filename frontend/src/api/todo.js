import axios from 'axios'

// 创建axios实例，指向我们的后端接口
const api = axios.create({
  baseURL: '/api',
  timeout: 5000
})

// 获取所有待办
export const getTodos = () => api.get('/todos')

// 新增待办
export const addTodo = (data) => api.post('/todos', data)

// 修改待办（内容+状态）
export const updateTodo = (id, data) => api.put(`/todos/${id}`, data)

// 删除待办
export const deleteTodo = (id) => api.delete(`/todos/${id}`)