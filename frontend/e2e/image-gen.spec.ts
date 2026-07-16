import { test, expect } from "@playwright/test";

test("AI image generation API", async ({ request }) => {
  // 登录
  const loginRes = await request.post(
    "http://localhost:8000/api/v1/auth/login",
    {
      data: { student_id: "student_001", password: "123456" },
    },
  );
  const { access_token } = await loginRes.json();
  expect(access_token).toBeTruthy();

  // 提交文生图
  const genRes = await request.post(
    "http://localhost:8000/api/v1/image/generate",
    {
      headers: { Authorization: `Bearer ${access_token}` },
      data: { prompt: "C语言指针示意图", use_pre_llm: true },
    },
  );
  const genData = await genRes.json();
  expect(genData.status).toBe("submitted");
  expect(genData.task_id).toBeTruthy();

  const taskId = genData.task_id;

  // 轮询结果（最多等 60s）
  let imageUrl = "";
  for (let i = 0; i < 20; i++) {
    await new Promise((r) => setTimeout(r, 3000));
    const pollRes = await request.get(
      `http://localhost:8000/api/v1/image/result/${taskId}`,
      { headers: { Authorization: `Bearer ${access_token}` } },
    );
    const data = await pollRes.json();

    if (data.status === "done" && data.image_urls?.length) {
      imageUrl = data.image_urls[0];
      break;
    }
    if (data.status === "failed" || data.status === "error") {
      test.fail(true, `Image gen failed: ${data.message}`);
    }
  }

  expect(imageUrl).toBeTruthy();

  // 验证图片可下载
  const imgRes = await request.get(imageUrl);
  expect(imgRes.status()).toBe(200);
  const contentType = imgRes.headers()["content-type"] || "";
  expect(contentType).toContain("image");
});
