# Recipe: Node 24 Native Test Suite (TDD Starter)

Standard Node 24 native test runner (`node --experimental-strip-types --test` or `node --test`).
Zero external dependencies required.

---

## 1. Unit Test Starter for Utilities & Logic

File location: `src/utils/__tests__/[module].test.ts`

```typescript
import { describe, it } from 'node:test'
import assert from 'node:assert/strict'
import { myFunction } from '../myModule.js'

describe('myFunction', () => {
  it('handles standard input correctly', () => {
    const result = myFunction('test-input')
    assert.strictEqual(result.success, true)
    assert.strictEqual(result.data, 'test-input-normalized')
  })

  it('clamps values within bounds', () => {
    assert.strictEqual(myFunction(-5).value, 0)
    assert.strictEqual(myFunction(150).value, 100)
  })

  it('handles edge cases (null, empty string, undefined)', () => {
    assert.strictEqual(myFunction(''), null)
    assert.strictEqual(myFunction(null as unknown as string), null)
  })
})
```

---

## 2. Asynchronous Operations & Timeout Testing

```typescript
import { describe, it } from 'node:test'
import assert from 'node:assert/strict'

describe('async test suite', () => {
  it('resolves asynchronous promises', async () => {
    const result = await Promise.resolve(42)
    assert.strictEqual(result, 42)
  })

  it('asserts promise rejections', async () => {
    const failingPromise = Promise.reject(new Error('Network error'))
    await assert.rejects(async () => failingPromise, {
      message: 'Network error',
    })
  })
})
```

---

## Execution Command
```bash
# Run all unit tests
npm test

# Run a specific test file
node --experimental-strip-types --test "src/utils/__tests__/myModule.test.ts"
```
