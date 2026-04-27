/**
 * 测试 MarkdownViewer 组件渲染逻辑
 * 运行：cd frontend && node scripts/test-markdown-render.js
 */
const { remark } = require('remark')
const remarkGfm = require('remark-gfm')
const sqlite3 = require('sqlite3').verbose()
const path = require('path')

const DB_PATH = path.resolve(__dirname, '../../backend/ai_learning_v2.db')

async function testRender(doc) {
  try {
    const result = await remark()
      .use(remarkGfm)
      .process(doc)
    return { ok: true, warnings: result.messages.map(m => m.message) }
  } catch (e) {
    return { ok: false, error: e.message }
  }
}

async function main() {
  const db = new sqlite3.Database(DB_PATH, sqlite3.OPEN_READONLY)

  db.all('SELECT kp_id, name, document FROM knowledge_points ORDER BY kp_id', async (err, rows) => {
    if (err) {
      console.error('DB error:', err)
      process.exit(1)
    }

    let allOk = true
    for (const row of rows) {
      const result = await testRender(row.document)
      const status = result.ok ? '✅' : '❌'
      const info = result.ok
        ? (result.warnings.length ? `warnings:${result.warnings.length}` : 'ok')
        : result.error
      console.log(`${status} ${row.kp_id} — ${row.name} | ${info}`)

      if (!result.ok) {
        allOk = false
        console.log('   Error:', result.error)
      }
    }

    db.close()
    console.log(allOk ? '\n🎉 All passed' : '\n⚠️ Some failed')
    process.exit(allOk ? 0 : 1)
  })
}

main()
