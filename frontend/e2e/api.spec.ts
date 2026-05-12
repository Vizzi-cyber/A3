import { test, expect } from "@playwright/test";

const BASE_URL = "http://localhost:8000/api/v1";
let token: string;
let studentId = "student_001";

test.describe.configure({ mode: "serial" });

test.describe("AI Learning System - Backend API Tests", () => {
  let token: string;
  const studentId = "student_001";

  test("Auth - Login success", async ({ request }) => {
    const resp = await request.post(`${BASE_URL}/auth/login`, {
      data: { student_id: studentId, password: "123456" },
    });
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body).toHaveProperty("access_token");
    expect(body).toHaveProperty("token_type", "bearer");
    expect(body).toHaveProperty("expires_in");
    token = body.access_token;
  });

  test("Auth - Login failure (wrong password)", async ({ request }) => {
    const resp = await request.post(`${BASE_URL}/auth/login`, {
      data: { student_id: studentId, password: "wrong" },
    });
    expect(resp.status()).toBe(401);
  });

  test("Auth - Get current user (with token)", async ({ request }) => {
    const resp = await request.get(`${BASE_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body.data.student_id).toBe(studentId);
  });

  test("Profile - Get student profile", async ({ request }) => {
    const resp = await request.get(`${BASE_URL}/profile/${studentId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body).toHaveProperty("data.knowledge_base");
    expect(body).toHaveProperty("data.cognitive_style");
  });

  test("Dashboard - Get summary", async ({ request }) => {
    const resp = await request.get(
      `${BASE_URL}/dashboard/${studentId}/summary`,
      {
        headers: { Authorization: `Bearer ${token}` },
      },
    );
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body).toHaveProperty("stats");
    expect(body.stats).toHaveProperty("weekly_hours");
    expect(body.stats).toHaveProperty("streak_days");
    expect(body).toHaveProperty("tasks");
    expect(body).toHaveProperty("recommendations");
    expect(body).toHaveProperty("trend");
  });

  test("Learning Path - Get current path", async ({ request }) => {
    const resp = await request.get(
      `${BASE_URL}/learning-path/${studentId}/current`,
      {
        headers: { Authorization: `Bearer ${token}` },
      },
    );
    expect(resp.status()).toBe(200);
  });

  test("Learning Path - Generate new path", async ({ request }) => {
    const resp = await request.post(`${BASE_URL}/learning-path/generate`, {
      headers: { Authorization: `Bearer ${token}` },
      data: {
        student_id: studentId,
        target_topic: "Python 基础",
        time_constraint: 10,
      },
    });
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body).toHaveProperty("data.path_id");
    expect(body.data.student_id).toBe(studentId);
  });

  test("Resource - Generate document", async ({ request }) => {
    const resp = await request.post(`${BASE_URL}/resource/generate`, {
      headers: { Authorization: `Bearer ${token}` },
      data: {
        student_id: studentId,
        topic: "Python basics",
        resource_types: ["document"],
      },
      timeout: 30000,
    });
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body).toHaveProperty("task_id");
    expect(body.status).toBe("pending");
  });

  test("Tutor - Ask question", async ({ request }) => {
    const resp = await request.post(`${BASE_URL}/tutor/ask`, {
      headers: { Authorization: `Bearer ${token}` },
      data: {
        student_id: studentId,
        question: "What is a variable?",
      },
      timeout: 30000,
    });
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body).toHaveProperty("response");
    expect(body.response.length).toBeGreaterThan(0);
  });

  test("Knowledge - List knowledge points", async ({ request }) => {
    const resp = await request.get(`${BASE_URL}/knowledge/list?limit=5`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body).toHaveProperty("data");
  });

  test("Gamification - Get points", async ({ request }) => {
    const resp = await request.get(
      `${BASE_URL}/gamification/${studentId}/points`,
      {
        headers: { Authorization: `Bearer ${token}` },
      },
    );
    expect(resp.status()).toBe(200);
  });

  test("Gamification - Get achievements", async ({ request }) => {
    const resp = await request.get(
      `${BASE_URL}/gamification/${studentId}/achievements`,
      {
        headers: { Authorization: `Bearer ${token}` },
      },
    );
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body).toHaveProperty("data");
  });

  test("Log - Get reflections", async ({ request }) => {
    const resp = await request.get(
      `${BASE_URL}/log-reflection/${studentId}/reflections`,
      {
        headers: { Authorization: `Bearer ${token}` },
      },
    );
    expect(resp.status()).toBe(200);
  });

  test("Favorites - Get favorites", async ({ request }) => {
    const resp = await request.get(`${BASE_URL}/favorites/${studentId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(resp.status()).toBe(200);
  });

  test("API Docs - OpenAPI schema accessible", async ({ request }) => {
    const resp = await request.get("http://localhost:8000/openapi.json");
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body).toHaveProperty("openapi");
    expect(body).toHaveProperty("paths");
  });

  // ========== 游化系统 API 测试 ==========

  test("Gamification Tree - Level config", async ({ request }) => {
    const resp = await request.get(
      `${BASE_URL}/gamification-tree/level-config`,
    );
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body.status).toBe("success");
    expect(body.data).toHaveProperty("xp_per_level", 500);
    expect(body.data).toHaveProperty("max_level");
    expect(body.data).toHaveProperty("level_names");
    expect(Object.keys(body.data.level_names).length).toBeGreaterThan(0);
  });

  test("Gamification Tree - Knowledge tree with level info", async ({
    request,
  }) => {
    const resp = await request.get(
      `${BASE_URL}/gamification-tree/${studentId}/tree`,
    );
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body.status).toBe("success");
    expect(body.data).toHaveProperty("tree_state");
    expect(body.data).toHaveProperty("level");
    expect(body.data).toHaveProperty("level_name");
    expect(body.data).toHaveProperty("level_info");
    expect(body.data.level_info).toHaveProperty("xp_per_level");
    expect(body.data.level_info).toHaveProperty("current_xp");
    expect(body.data.level_info).toHaveProperty("progress_pct");
  });

  test("Gamification Challenge - Get challenges", async ({ request }) => {
    const resp = await request.get(
      `${BASE_URL}/gamification-challenge/${studentId}/challenges`,
    );
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body.status).toBe("success");
    expect(body.data).toHaveProperty("challenges");
    expect(body.data).toHaveProperty("map_nodes");
    expect(body.data).toHaveProperty("summary");
    expect(body.data.challenges.length).toBeGreaterThan(0);
    expect(body.data.challenges[0]).toHaveProperty("id");
    expect(body.data.challenges[0]).toHaveProperty("name");
    expect(body.data.challenges[0]).toHaveProperty("progress");
  });

  test("Gamification Challenge - Leaderboard (points)", async ({ request }) => {
    const resp = await request.get(
      `${BASE_URL}/gamification-challenge/leaderboard/points?period=weekly&limit=5`,
    );
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body.status).toBe("success");
    expect(body.data).toHaveProperty("dimension", "points");
    expect(body.data).toHaveProperty("entries");
    if (body.data.entries.length > 0) {
      expect(body.data.entries[0]).toHaveProperty("student_id");
      expect(body.data.entries[0]).toHaveProperty("username");
      expect(body.data.entries[0]).toHaveProperty("score");
      expect(body.data.entries[0]).toHaveProperty("rank");
    }
  });

  test("Dashboard - Growth timeline", async ({ request }) => {
    const resp = await request.get(
      `${BASE_URL}/dashboard/${studentId}/timeline`,
    );
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body.status).toBe("success");
    expect(body.data).toHaveProperty("milestones");
    expect(body.data).toHaveProperty("daily_curve");
  });

  test("Agent Flow - Start run and check status", async ({ request }) => {
    // Start a run
    const startResp = await request.post(`${BASE_URL}/agent-flow/run`, {
      data: { student_id: studentId, task_type: "profile_update" },
    });
    expect(startResp.status()).toBe(200);
    const startBody = await startResp.json();
    expect(startBody).toHaveProperty("run_id");
    expect(startBody.status).toBe("running");

    // Check status
    const runId = startBody.run_id;
    const statusResp = await request.get(
      `${BASE_URL}/agent-flow/${runId}/status`,
    );
    expect(statusResp.status()).toBe(200);
    const statusBody = await statusResp.json();
    expect(statusBody).toHaveProperty("run_id", runId);
    expect(statusBody).toHaveProperty("agents");
    expect(statusBody).toHaveProperty("logs");
  });

  test("PPT - Generate and check status", async ({ request }) => {
    // Start PPT generation
    const genResp = await request.post(`${BASE_URL}/ppt/generate`, {
      data: { topic: "test topic", subject: "C语言数据结构" },
    });
    expect(genResp.status()).toBe(200);
    const genBody = await genResp.json();
    expect(genBody).toHaveProperty("task_id");
    expect(genBody.status).toBe("success");

    // Wait and check status
    const taskId = genBody.task_id;
    await new Promise((resolve) => setTimeout(resolve, 8000));
    const statusResp = await request.get(`${BASE_URL}/ppt/${taskId}/status`);
    expect(statusResp.status()).toBe(200);
    const statusBody = await statusResp.json();
    expect(statusBody.data).toHaveProperty("task_id", taskId);
    expect([
      "completed",
      "building_pptx",
      "generating_outline",
      "pending",
    ]).toContain(statusBody.data.status);
  });
});
