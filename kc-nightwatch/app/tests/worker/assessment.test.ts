import { describe, it, expect } from 'bun:test'
import type { RunSummaryAction, PerTargetSummary } from '../../shared/types.ts'

describe('assessment display', () => {
  it('RunSummaryAction.assessment has required fields', () => {
    const action: RunSummaryAction = {
      signal_id: 'test:001',
      type: 'code-fix',
      summary: 'Fixed lint warnings',
      indicator: 'code-quality',
      assessment: {
        closer_to_north_star: 'yes',
        confidence: 'high',
        reasoning: 'Lint fixes directly improve code quality metric',
      },
    }
    expect(action.assessment.closer_to_north_star).toBe('yes')
    expect(action.assessment.confidence).toBe('high')
    expect(action.assessment.reasoning).toContain('code quality')
  })

  it('PerTargetSummary has pre/post assessment strings', () => {
    const summary: Partial<PerTargetSummary> = {
      pre_assessment: 'Analysis shows 3 high-priority signals. Focusing on code quality and test coverage.',
      post_assessment: 'Executed 2 of 3 actions. Code quality improved. Test coverage unchanged due to scope limitation.',
    }
    expect(summary.pre_assessment).toContain('high-priority')
    expect(summary.post_assessment).toContain('Code quality improved')
  })

  it('assessment closer_to_north_star has exactly 3 valid values', () => {
    const valid = ['yes', 'no', 'uncertain']
    for (const v of valid) {
      expect(valid).toContain(v)
    }
  })

  it('assessment confidence has exactly 3 valid values', () => {
    const valid = ['high', 'medium', 'low']
    for (const v of valid) {
      expect(valid).toContain(v)
    }
  })

  it('assessment reasoning is human-readable prose', () => {
    const action: RunSummaryAction = {
      signal_id: 'test:002',
      type: 'proposal',
      summary: 'Add error handling to API endpoints',
      indicator: 'reliability',
      assessment: {
        closer_to_north_star: 'uncertain',
        confidence: 'medium',
        reasoning: 'Adding error handling improves reliability but the impact depends on usage patterns. Recommend monitoring error rates after deployment.',
      },
    }
    // Reasoning should be a sentence, not raw JSON or code
    expect(action.assessment.reasoning.length).toBeGreaterThan(20)
    expect(action.assessment.reasoning).not.toContain('{')
    expect(action.assessment.reasoning).not.toContain('}')
  })
})
