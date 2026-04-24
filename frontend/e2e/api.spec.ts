import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:8000/api/v1';
let token: string;
let studentId = 'student_001';

test.describe.configure({ mode: 'serial' });

test.describe('AI Learning System - Backend API Tests', () => {

  let token: string;
  const studentId = 'student_001';

  test('Auth - Login success', async ({ request }) => {
    const resp = await request.post(`${BASE_URL}/auth/login`, {
      data: { student_id: studentId, password: '123456' },
    });
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body).toHaveProperty('access_token');
    expect(body).toHaveProperty('token_type', 'bearer');
    expect(body).toHaveProperty('expires_in');
    token = body.access_token;
  });

  test('Auth - Login failure (wrong password)', async ({ request }) => {
    const resp = await request.post(`${BASE_URL}/auth/login`, {
      data: { student_id: studentId, password: 'wrong' },
    });
    expect(resp.status()).toBe(401);
  });

  test('Auth - Get current user (with token)', async ({ request }) => {
    const resp = await request.get(`${BASE_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body.data.student_id).toBe(studentId);
  });

  test('Profile - Get student profile', async ({ request }) => {
    const resp = await request.get(`${BASE_URL}/profile/${studentId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body).toHaveProperty('data.knowledge_base');
    expect(body).toHaveProperty('data.cognitive_style');
  });

  test('Dashboard - Get summary', async ({ request }) => {
    const resp = await request.get(`${BASE_URL}/dashboard/${studentId}/summary`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body).toHaveProperty('stats');
    expect(body.stats).toHaveProperty('weekly_hours');
    expect(body.stats).toHaveProperty('streak_days');
    expect(body).toHaveProperty('tasks');
    expect(body).toHaveProperty('recommendations');
    expect(body).toHaveProperty('trend');
  });

  test('Learning Path - Get current path', async ({ request }) => {
    const resp = await request.get(`${BASE_URL}/learning-path/${studentId}/current`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(resp.status()).toBe(200);
  });

  test('Learning Path - Generate new path', async ({ request }) => {
    const resp = await request.post(`${BASE_URL}/learning-path/generate`, {
      headers: { Authorization: `Bearer ${token}` },
      data: {
        student_id: studentId,
        target_topic: 'Python 基础',
        time_constraint: 10,
      },
    });
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body).toHaveProperty('data.path_id');
    expect(body.data.student_id).toBe(studentId);
  });

  test('Resource - Generate document', async ({ request }) => {
    const resp = await request.post(`${BASE_URL}/resource/generate`, {
      headers: { Authorization: `Bearer ${token}` },
      data: {
        student_id: studentId,
        topic: 'Python basics',
        resource_types: ['document'],
      },
      timeout: 30000,
    });
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body).toHaveProperty('task_id');
    expect(body.status).toBe('pending');
  });

  test('Tutor - Ask question', async ({ request }) => {
    const resp = await request.post(`${BASE_URL}/tutor/ask`, {
      headers: { Authorization: `Bearer ${token}` },
      data: {
        student_id: studentId,
        question: 'What is a variable?',
      },
      timeout: 30000,
    });
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body).toHaveProperty('response');
    expect(body.response.length).toBeGreaterThan(0);
  });

  test('Knowledge - List knowledge points', async ({ request }) => {
    const resp = await request.get(`${BASE_URL}/knowledge/list?limit=5`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body).toHaveProperty('data');
  });

  test('Gamification - Get points', async ({ request }) => {
    const resp = await request.get(`${BASE_URL}/gamification/${studentId}/points`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(resp.status()).toBe(200);
  });

  test('Gamification - Get achievements', async ({ request }) => {
    const resp = await request.get(`${BASE_URL}/gamification/${studentId}/achievements`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body).toHaveProperty('data');
  });

  test('Log - Get reflections', async ({ request }) => {
    const resp = await request.get(`${BASE_URL}/log-reflection/${studentId}/reflections`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(resp.status()).toBe(200);
  });

  test('Favorites - Get favorites', async ({ request }) => {
    const resp = await request.get(`${BASE_URL}/favorites/${studentId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(resp.status()).toBe(200);
  });

  test('API Docs - OpenAPI schema accessible', async ({ request }) => {
    const resp = await request.get('http://localhost:8000/openapi.json');
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body).toHaveProperty('openapi');
    expect(body).toHaveProperty('paths');
  });

});
