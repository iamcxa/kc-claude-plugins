import { describe, it, expect } from 'bun:test'
import path from 'node:path'

/**
 * Static wiring verification tests for executor.ts feedback integration.
 *
 * These tests confirm the production code path exists by reading executor.ts
 * source and verifying key strings are present. This approach avoids mocking
 * the full executor (spawning safehouse/claude processes) while still verifying
 * the wiring is in place.
 *
 * FEED-04: collectImplicitFeedback wired into post-run flow
 * FEED-07: writeFeedbackTrends wired into post-run flow
 */

const EXECUTOR_PATH = path.join(import.meta.dir, '../../worker/executor.ts')

describe('executor.ts feedback wiring (static verification)', () => {
  it('imports collectImplicitFeedback from feedback-collector.ts', async () => {
    const source = await Bun.file(EXECUTOR_PATH).text()
    expect(source).toMatch(/import\s*\{[^}]*collectImplicitFeedback[^}]*\}\s*from\s*['"].*feedback-collector/)
  })

  it('imports appendFeedback from feedback-store.ts', async () => {
    const source = await Bun.file(EXECUTOR_PATH).text()
    expect(source).toMatch(/import\s*\{[^}]*appendFeedback[^}]*\}\s*from\s*['"].*feedback-store/)
  })

  it('imports writeFeedbackTrends from feedback-store.ts', async () => {
    const source = await Bun.file(EXECUTOR_PATH).text()
    expect(source).toMatch(/import\s*\{[^}]*writeFeedbackTrends[^}]*\}\s*from\s*['"].*feedback-store/)
  })

  it('calls collectImplicitFeedback in post-run flow (not just imported)', async () => {
    const source = await Bun.file(EXECUTOR_PATH).text()
    // Must appear at least twice: import line + actual call
    const matches = source.match(/collectImplicitFeedback/g)
    expect(matches).not.toBeNull()
    expect(matches!.length).toBeGreaterThanOrEqual(2)
  })

  it('calls writeFeedbackTrends in post-run flow (not just imported)', async () => {
    const source = await Bun.file(EXECUTOR_PATH).text()
    // Must appear at least twice: import line + actual call
    const matches = source.match(/writeFeedbackTrends/g)
    expect(matches).not.toBeNull()
    expect(matches!.length).toBeGreaterThanOrEqual(2)
  })

  it('feedback block is guarded by !timedOut check (skipped on timeout)', async () => {
    const source = await Bun.file(EXECUTOR_PATH).text()
    // The feedback block must be conditional on !timedOut so it's skipped when run timed out
    expect(source).toMatch(/!timedOut/)
    // And the feedback call must be within a block that checks timedOut
    const feedbackIndex = source.indexOf('collectImplicitFeedback(actionsWithTargets')
    const timedOutIndex = source.lastIndexOf('!timedOut', feedbackIndex)
    // timedOut check must precede the collectImplicitFeedback call
    expect(timedOutIndex).toBeGreaterThan(0)
    expect(timedOutIndex).toBeLessThan(feedbackIndex)
  })

  it('feedback block is wrapped in try/catch (errors never block run completion)', async () => {
    const source = await Bun.file(EXECUTOR_PATH).text()
    // The feedback section should have a try block that wraps both calls
    // Check that there's a catch after the feedback calls
    expect(source).toMatch(/Post-run feedback collection error/)
  })

  it('feedback-collector module resolves correctly', async () => {
    // Verify the import resolves — this catches path typos
    const mod = await import('../../worker/feedback-collector.ts')
    expect(typeof mod.collectImplicitFeedback).toBe('function')
  })

  it('feedback-store module resolves correctly', async () => {
    // Verify the import resolves — this catches path typos
    const mod = await import('../../server/services/feedback-store.ts')
    expect(typeof mod.appendFeedback).toBe('function')
    expect(typeof mod.writeFeedbackTrends).toBe('function')
  })
})

/**
 * EXTFEED-02: collectPrReviewFeedback wired into post-run flow
 */
describe('executor.ts PR review feedback wiring (EXTFEED-02)', () => {
  it('imports collectPrReviewFeedback from feedback-collector.ts', async () => {
    const source = await Bun.file(EXECUTOR_PATH).text()
    expect(source).toMatch(/import\s*\{[^}]*collectPrReviewFeedback[^}]*\}\s*from\s*['"].*feedback-collector/)
  })

  it('calls collectPrReviewFeedback in post-run flow (not just imported)', async () => {
    const source = await Bun.file(EXECUTOR_PATH).text()
    // Must appear at least twice: import line + actual call
    const matches = source.match(/collectPrReviewFeedback/g)
    expect(matches).not.toBeNull()
    expect(matches!.length).toBeGreaterThanOrEqual(2)
  })

  it('calls collectPrReviewFeedback with actionsWithTargets and appendFeedback', async () => {
    const source = await Bun.file(EXECUTOR_PATH).text()
    expect(source).toContain('collectPrReviewFeedback(actionsWithTargets, appendFeedback)')
  })

  it('EXTFEED-02 comment present in executor.ts (requirement traced)', async () => {
    const source = await Bun.file(EXECUTOR_PATH).text()
    expect(source).toContain('EXTFEED-02')
  })

  it('collectPrReviewFeedback is inside the same try/catch as collectImplicitFeedback', async () => {
    const source = await Bun.file(EXECUTOR_PATH).text()
    // Both calls must appear before the 'Post-run feedback collection error' catch message
    const catchMsgIndex = source.indexOf('Post-run feedback collection error')
    const implicitIndex = source.indexOf('collectImplicitFeedback(actionsWithTargets')
    const reviewIndex = source.indexOf('collectPrReviewFeedback(actionsWithTargets')
    expect(implicitIndex).toBeGreaterThan(0)
    expect(reviewIndex).toBeGreaterThan(0)
    // Both calls should come before the catch message (inside the try block)
    expect(implicitIndex).toBeLessThan(catchMsgIndex)
    expect(reviewIndex).toBeLessThan(catchMsgIndex)
  })

  it('feedback-collector module exports collectPrReviewFeedback', async () => {
    const mod = await import('../../worker/feedback-collector.ts')
    expect(typeof mod.collectPrReviewFeedback).toBe('function')
  })
})
