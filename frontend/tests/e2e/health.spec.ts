import { test, expect } from '@playwright/test'

test.describe('Backend Health Check', () => {
  test('should return healthy status from /health endpoint', async ({ request }) => {
    const response = await request.get('/health')
    expect(response.ok()).toBeTruthy()
    const data = await response.json()
    expect(data).toHaveProperty('status', 'healthy')
  })

  test('should return API info from root endpoint', async ({ request }) => {
    const response = await request.get('/')
    expect(response.ok()).toBeTruthy()
    const data = await response.json()
    expect(data).toHaveProperty('message', 'EstiMate API')
    expect(data).toHaveProperty('version')
  })
})
